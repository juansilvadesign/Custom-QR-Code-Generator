# Milestone C scan evidence

The automated matrix is necessary but does not justify a universal “will scan”
claim. Milestone C must not be marked shipped until a maintainer completes the
representative real-device rows below using generated release fixtures.

## Automated independent-decoder evidence

Run:

```bash
python -m unittest discover -s tests -v
```

`tests/test_svg_decode.py` reads the serialized SVG, independently reconstructs
its background and module rectangles, and passes the resulting bitmap to
ZXing-C++ 3.1.1. It asserts:

- exact output for every authored ASCII/Unicode/structured fixture;
- all six payload types at requested ECL L/M/Q/H;
- exact L/M/Q/H conservative capacity boundaries at QR version 40;
- QR version 32, guarding the vendored alignment-pattern update;
- high contrast, accepted low contrast, reversed polarity, and two-module quiet
  zone outcomes;
- exact decoded Unicode text, not merely the presence of a barcode.

## Generating the artifacts to scan

The rows below are generated from the committed fixture catalog, not created by
hand:

```bash
python export_release_fixtures.py
```

This writes `fixtures/release/` with one SVG per row, a `print-sheet.html` sized
for the printed row, and a `MANIFEST.md` recording each artifact's payload type,
requested/actual error correction, QR version, module count, border, contrast,
polarity, recommended minimum pixels, and warnings. Every fixture is decoded
through the independent decoder before it is written, and the command exits
non-zero if any artifact fails to decode to its exact expected payload — so a
file that exists is a file that was verified.

The output is deterministic and regenerable, so it is gitignored rather than
committed. All credentials in the WiFi row are synthetic catalog values.

## Manual device/app matrix — required before release

For each row, record the exact device, OS, scanner app/version, rendered size,
display or print medium, approximate lighting, payload fixture, border/color
variant, decoded result, and pass/fail. Never put a real password, private
message, or personal number into this document.

| Date | Device / OS | Scanner app | Medium / size | Lighting | Fixture file / variant | Exact result | Pass? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-21 | Android phone, not the iOS phone this row specifies | Built-in Camera | 1080p monitor / 320 device px | Indoor | `01-text-unicode-normal.svg` — text Unicode / normal | Decoded; text not captured | Pass |
| 2026-08-21 | Android phone | Built-in Camera | 1080p monitor / 320 device px | Indoor | `02-url-normal.svg` — URL / normal | Decoded; text not captured | Pass |
| 2026-08-21 | Android phone | Built-in Camera | 1080p monitor at a calibrated 30 mm, not printed | Indoor | `03-wifi-wpa-hidden-printed.svg` — WiFi WPA test credential / normal | Decoded; text not captured | Pass |
| 2026-08-21 | Android phone | Built-in Camera | 1080p monitor / 320 device px | Indoor | `04-text-border3.svg` — text / 3-module border | Decoded; text not captured | Pass |
| 2026-08-21 | Android phone | Built-in Camera | 1080p monitor / 320 device px | Indoor | `05-text-low-contrast.svg` — text / accepted low contrast | Decoded; text not captured | Pass |
| 2026-08-21 | Android phone | Built-in Camera | 1080p monitor / 320 device px | Indoor | `06-text-reversed-polarity.svg` — text / reversed polarity | Decoded; text not captured | Pass |
| 2026-08-21 | Android phone only, not both device families | Built-in Camera | 1080p monitor / largest size the browser window allowed; exact size not recorded | Indoor | `07-v40-boundary-L.svg` — version-40 boundary fixture | Decoded; text not captured | Pass |
| 2026-08-21 | Android phone | Built-in Camera | 1080p monitor / 320 device px | Indoor | `08-text-border2-minimum.svg` — text / 2-module border (tightest accepted) | Decoded; text not captured | Pass |

The final row is not in the original seven: it covers `MIN_ACCEPTED_BORDER`, the
smallest quiet zone the contract still accepts. The automated evidence matrix in
`tests/test_svg_decode.py` already decodes this case, so the release claim should
either be backed by a real-device result here or be narrowed to a four-module
quiet zone.

If a scanner fails an accepted warning case, retain the warning and narrow the
release claim. If a normal-polarity, four-module, high-contrast release fixture
fails, stop release work and treat it as a Milestone C blocker.

## What the recorded rows evidence

All eight fixtures were scanned on 2026-08-21 with one Android phone and its
built-in Camera app. A local harness page, which is not part of this repository,
displayed them on a 1080p monitor under indoor light. It inlines the
`fixtures/release/` SVGs unchanged and sizes them in device pixels. The rows were
written on 2026-10-06 from the maintainer's account of that session, because the
rows the harness exported were not kept.

Not captured, and therefore not claimed:

- The phone model, the Android version, and the Camera app version.
- The decoded text. Each pass means the phone read the symbol. Exact payload
  equality rests on the automated decoder matrix above, not on these rows.
- Row 07's exact size, beyond being the largest the browser window allowed.

Four rows were shown below the recommended minimum pixel size in
`fixtures/release/MANIFEST.md`: rows 01 and 02 at 320 px against 328 px, row 03
because 30 mm on a 1080p monitor spans far fewer than 360 px, and row 07 because
1480 px exceeds a 1080p panel. Those passes are additional evidence. They do not
lower the recommendations.

Three rows carry less than the row specified, so the release claim is narrowed to
**Android, on-display, at the recorded sizes**:

- Row 01 was scanned on Android. It evidences the Unicode payload, not the iOS
  device family.
- Row 03 was displayed at a calibrated 30 mm, not printed. The physical size
  holds; the printed medium stays unevidenced.
- Row 07 was scanned on Android only, not on both device families.

iOS and printed media remain covered by the automated matrix alone. An emissive
display also flatters contrast, so row 05's pass at 4.48:1 does not transfer to
reflective print. Row 08 passed, so the two-module quiet zone is backed by a
real-device result on that phone and display.
