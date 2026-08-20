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

## Manual device/app matrix — required before release

Use the committed fixture catalog. For each row, record the exact device, OS,
scanner app/version, rendered size, display or print medium, approximate lighting,
payload fixture, border/color variant, decoded result, and pass/fail. Never put a
real password, private message, or personal number into this document.

| Date | Device / OS | Scanner app | Medium / size | Lighting | Fixture / variant | Exact result | Pass? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | Current iOS phone | Built-in Camera | OLED display / 320 px | Indoor | text Unicode / normal | Pending | Pending |
| Pending | Current Android phone | Built-in Camera or Lens | LCD/OLED display / 320 px | Indoor | URL / normal | Pending | Pending |
| Pending | iOS or Android | Built-in scanner | Printed / approximately 30 mm | Office light | WiFi WPA test credential / normal | Pending | Pending |
| Pending | One device above | Same app | Display / 320 px | Indoor | text / 3-module border | Pending | Pending |
| Pending | One device above | Same app | Display / 320 px | Indoor | text / accepted low contrast | Pending | Pending |
| Pending | One device above | Same app | Display / 320 px | Indoor | text / reversed polarity | Pending | Pending |
| Pending | Both device families | Same apps | Display / suggested minimum | Indoor | version-40 boundary fixture | Pending | Pending |

If a scanner fails an accepted warning case, retain the warning and narrow the
release claim. If a normal-polarity, four-module, high-contrast release fixture
fails, stop release work and treat it as a Milestone C blocker.
