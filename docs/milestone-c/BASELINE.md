# Milestone C baseline

Milestone C started on 2026-08-20 from a clean working tree at commit
`158d033754dd02839d11e86d6217aa1804b31035` (`docs: 📄 add roadmap
and tasks`). The fixed six-week frame ends on 2026-10-01. Milestone C keeps its
12-maintainer-day ceiling inside the existing 30-day C–F budget.

## Reproducible renderer snapshot

The legacy CLI and web renderers were called with the same vendored encoder,
payload, colors, border, and requested correction level before the shared core
was introduced:

```text
payload text:  Hello, QR & 世界\nline 2
payload UTF-8: 48656c6c6f2c205152202620e4b896e7958c0a6c696e652032
requested ECL: M
background:    #FFFFFF
foreground:    #000000
border:        4
QR version:    2
module count:  25
mask:          2
actual ECL:    M
```

The exact artifacts are reproducible from the starting commit by calling
`main.to_svg_str_custom()` and `app.to_svg_string()` with that data. Their byte
snapshots were:

| Surface | Bytes | SHA-256 |
| --- | ---: | --- |
| CLI | 5,013 | `40607cb86b61961f7c349c2b3e937477904372a2105871894995f86636663bf3` |
| Web | 5,016 | `b39dc2768935791703b1d0b7fd91e9eddbd4624b826b1bd87a9fe283faf03e30` |

Both files decoded through ZXing-C++ 3.1.1 to the exact text and UTF-8 bytes
above. They nevertheless differed byte-for-byte because the CLI wrote hex fills
and whitespace while the web renderer wrote RGB fills without whitespace. Both
also emitted an external SVG 1.1 doctype. These are the parity and XML defects
Milestone C is expected to remove.

## Legacy structured-payload observations

The starting implementation concatenated mail subject/body and SMS body values
without URI encoding. It also interpolated WiFi SSID/password fields without
escaping `\\`, `;`, `,`, `:`, or quotes. Those payloads were recorded as known
semantic defects rather than release fixtures; the exact corrected expectations
live in `tests/fixtures/payloads.json`.

## Vendored encoder baseline

The starting `qrcodegen.py` checksum was
`481d392e0c9b2397ff0ab89a863f23cd92133ea9d7c7958f6d6e9084632ee057`.
It matched Project Nayuki commit
`856ba8a74b48a6b3b32dd86f13b66b61b8579fcd` after removal of the upstream
26-line MIT notice. Milestone C restores the notice and updates to the official
bug-fixed revision documented in `docs/ENCODER_PROVENANCE.md`.
