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
| Pending | Current iOS phone | Built-in Camera | OLED display / 320 px | Indoor | `01-text-unicode-normal.svg` — text Unicode / normal | Pending | Pending |
| Pending | Current Android phone | Built-in Camera or Lens | LCD/OLED display / 320 px | Indoor | `02-url-normal.svg` — URL / normal | Pending | Pending |
| Pending | iOS or Android | Built-in scanner | Printed / approximately 30 mm | Office light | `03-wifi-wpa-hidden-printed.svg` — WiFi WPA test credential / normal | Pending | Pending |
| Pending | One device above | Same app | Display / 320 px | Indoor | `04-text-border3.svg` — text / 3-module border | Pending | Pending |
| Pending | One device above | Same app | Display / 320 px | Indoor | `05-text-low-contrast.svg` — text / accepted low contrast | Pending | Pending |
| Pending | One device above | Same app | Display / 320 px | Indoor | `06-text-reversed-polarity.svg` — text / reversed polarity | Pending | Pending |
| Pending | Both device families | Same apps | Display / suggested minimum | Indoor | `07-v40-boundary-L.svg` — version-40 boundary fixture | Pending | Pending |
| Pending | One device above | Same app | Display / 320 px | Indoor | `08-text-border2-minimum.svg` — text / 2-module border (tightest accepted) | Pending | Pending |

The final row is not in the original seven: it covers `MIN_ACCEPTED_BORDER`, the
smallest quiet zone the contract still accepts. The automated evidence matrix in
`tests/test_svg_decode.py` already decodes this case, so the release claim should
either be backed by a real-device result here or be narrowed to a four-module
quiet zone.

If a scanner fails an accepted warning case, retain the warning and narrow the
release claim. If a normal-polarity, four-module, high-contrast release fixture
fails, stop release work and treat it as a Milestone C blocker.
