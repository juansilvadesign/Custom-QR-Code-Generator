# Changelog

All notable changes are recorded here. The project has not assigned a semantic
version yet.

## Unreleased — Milestone C

### Added

- One canonical request/result contract and shared core for terminal and Flask.
- Exact fixture-tested text, URL, email, phone, WiFi, and SMS builders.
- Payload-safe metadata, requested/actual error-correction reporting, deterministic
  errors, and scanability warnings.
- Strict API media type, JSON shape, field, body-size, color, border, ECL, and
  capacity validation with `no-store` responses.
- Race-safe exclusive SVG output paths and portable filename sanitization.
- Assertion-based unit, API, CLI/filesystem, parity, SVG/XML, security, and
  independent ZXing decode tests plus cross-platform CI.
- Encoder provenance, fixture baseline, contract, update procedure, and manual
  device-matrix template.

### Changed

- Email subject/body and SMS body are UTF-8 percent encoded; spaces use `%20`.
- WiFi SSID/password reserved characters are escaped, security modes are strict,
  `nopass` omits credentials, and hidden state is explicit.
- Bare URLs gain `https://`; existing HTTP(S) URLs are preserved; malformed or
  unsupported schemes fail instead of being silently rewritten.
- Common phone formatting is removed while a leading plus and digits are retained.
- Encoder boosting is explicit in result metadata rather than appearing as the
  requested level.
- SVG output no longer contains an external doctype and is byte-identical across
  CLI and web for one canonical request.
- The CLI no longer prints payloads by default, no longer recurses for another QR,
  and no longer silently clamps invalid borders.
- The browser API moved from legacy `content`/`backgroundColor`/
  `foregroundColor`/`errorLevel` fields to the canonical `payloadType`/`fields`/
  `background`/`foreground`/`errorCorrection` envelope.
- The vendored Nayuki source now matches the recorded upstream bug-fixed file and
  includes its required MIT notice.

### Removed

- Duplicate CLI/web SVG renderers, wildcard CORS, raw exception responses,
  dependency on `flask-cors`, and the print-only `test_app.py` smoke script.

### Compatibility notes

- Python 3.7–3.9 are no longer claimed. Milestone C supports Python 3.10–3.14 and
  CI exercises the endpoints plus Windows/macOS representatives.
- Border values 0–1 and contrast below 3.0:1 now fail. Borders 2–3, contrast below
  4.5:1, and reversed polarity return visible warnings.
- Output names retain meaningful dots, receive one `.svg` suffix, and can never
  select a directory outside `saved/`.
