# Generation contract

Milestone C defines one in-process request/result contract in `qr_contract.py`.
The terminal and Flask adapters may collect values differently, but both call
`qr_core.generate()` and receive the same payload, matrix, SVG, warnings, and
metadata semantics.

## Canonical request

| Field | Type | Default / rule |
| --- | --- | --- |
| `payload_type` | string | One of `text`, `url`, `email`, `phone`, `wifi`, `sms` |
| `fields` | mapping | Exact allowed fields for the selected payload type; unknown fields fail |
| `requested_error_correction` | string | `M`; exact uppercase `L`, `M`, `Q`, or `H` |
| `foreground` | string | `#000000`; strict six-digit `#RRGGBB` syntax |
| `background` | string | `#FFFFFF`; strict six-digit `#RRGGBB` syntax |
| `border` | integer | `4`; accepted range 2–16, with a warning below 4 |
| `output_name` | string or null | `custom_qr.svg`; sanitized to a portable basename inside `saved/` |

The Flask JSON adapter uses the equivalent camel-case object:

```json
{
  "payloadType": "text",
  "fields": {"text": "exact text"},
  "errorCorrection": "M",
  "foreground": "#000000",
  "background": "#FFFFFF",
  "border": 4,
  "outputName": "qrcode.svg"
}
```

`payloadType` and `fields` are required. Other values use the defaults in the
table. The API accepts only `application/json`, an object, and the documented
root fields. Its request body limit is 16,384 bytes and is enforced before JSON
parsing.

## Exact payload rules

All output comparison is by the exact Python Unicode scalar sequence and its
exact UTF-8 bytes. The generator never applies NFC/NFD normalization, case
folding, transliteration, or replacement characters. An invalid unpaired
surrogate fails with `invalid_unicode`.

| Type | Fields and output rule |
| --- | --- |
| Text | Required `text`. It is encoded exactly, including whitespace and line breaks. Empty text fails. |
| URL | Required `url`. Surrounding whitespace is removed. A missing scheme (including a host plus numeric port), or a network-path URL beginning `//`, gains `https`. Existing `http` and `https` URLs are otherwise preserved. Other schemes, absent hosts, invalid ports, control characters, and unescaped whitespace fail. |
| Email | Required `address`; optional `subject` and `body`. Basic address structure is validated without claiming deliverability. URI delimiters in the address and all subject/body values use UTF-8 percent encoding with `%20` for spaces; query parameter order is `subject`, then `body`. |
| Phone | Required `phone`. A single leading `+` and 3–15 digits are retained; spaces, parentheses, dots, and hyphens are removed. Letters/extensions fail. This does not prove that the number exists. |
| WiFi | Required `ssid` and `security`; optional `password` and boolean `hidden`. Security is canonicalized to `WPA`, `WEP`, or `nopass`. `\\`, `;`, `,`, `:`, and `"` are backslash-escaped in SSID/password. WPA/WEP require a password. `nopass` omits `P` and warns if a supplied password was ignored. `H:true` or `H:false` is always retained. |
| SMS | Required normalized `phone`; optional `body`. Body uses exact UTF-8 percent encoding after `?body=`. This does not prove that the destination exists. |

Exact authored examples, reserved characters, non-Latin text, line breaks, empty
input, and capacity boundaries are versioned in `tests/fixtures/payloads.json`.

## Capacity and encoder behavior

Before encoding, the complete built payload is UTF-8 encoded and checked against
a conservative version-40 byte-mode ceiling:

| Requested ECL | Maximum payload bytes |
| --- | ---: |
| L | 2,953 |
| M | 2,331 |
| Q | 1,663 |
| H | 1,273 |

Crossing this declared limit is `payload_too_large`. A payload inside the byte
limit that the encoder still cannot place is `encoder_capacity_exceeded`.
Invalid structured fields keep their own validation codes and are not mislabeled
as capacity failures.

Project Nayuki's ECL boosting remains enabled: the encoder may increase
protection when it fits without increasing QR version. Results always expose
both `requested_error_correction` and `actual_error_correction`.

## Scanability guard

The guard is an implementation-independent heuristic, not a scanning guarantee
and not an accessibility score.

- Relative luminance and contrast use the standard sRGB formula.
- Contrast below 3.0:1 is rejected as `unsafe_contrast`.
- Contrast from 3.0:1 through below 4.5:1 returns `low_contrast`.
- Light modules on a darker background return `reversed_polarity`.
- Borders 0–1 are rejected as `unsafe_border`; 2–3 return
  `reduced_quiet_zone`; 4 is the safe default.
- Metadata includes version, module count, border, mask, polarity, contrast, and
  a suggested digital dimension based on eight pixels per module. It is guidance,
  not a universal print or physical-size claim.

Warnings make the result status `warning`; only a normal-polarity, recommended-
contrast result with a four-module-or-larger border receives `pass`. The release
suite independently rasterizes the serialized SVG geometry and decodes it with
ZXing-C++ across types, ECLs, versions, colors, polarity, and borders.

## Canonical result and privacy boundary

The in-process `GenerationResult` contains the exact payload, redacted summary,
sensitivity flag, deterministic SVG, exact module matrix, encoder metadata,
scanability assessment, filename, and stable warnings. Keeping the payload in
process makes exact CLI/web parity and decode assertions possible.

The public HTTP representation intentionally omits the exact payload, sensitivity
flag, and field values. It returns `svg`, a redacted `summary`, `warnings`, and
payload-safe `metadata`. All API responses use `Cache-Control: no-store`; the app
does not log request bodies, SVGs, or exception strings. The terminal displays a
redacted summary and requires an explicit prompt before revealing any sensitive
payload.

Local output rejects a symbolic-link `saved/` directory, resolves the destination,
and uses exclusive creation so traversal, redirection, and collision handling do
not overwrite or escape into another path.

The SVG contains only a validated background color and QR module coordinates; it
has no external doctype, script, event handler, link, or reference. Its structure
is deterministic: XML declaration, one SVG element, one background rectangle,
and one module path.

## Stable HTTP errors

| Status | Error family |
| ---: | --- |
| 400 | malformed JSON, non-object JSON, missing root field, unknown root field |
| 413 | request body above 16,384 bytes |
| 415 | media type other than `application/json` |
| 422 | unsupported payload type, invalid structured field, color/ECL/border/contrast error, or QR capacity failure |
| 500 | generic `internal_error`; no raw exception, path, payload, or traceback |

Every response uses `{ "error": { "code": "...", "message": "..." } }`.
