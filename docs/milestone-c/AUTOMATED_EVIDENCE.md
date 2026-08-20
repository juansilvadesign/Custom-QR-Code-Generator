# Milestone C automated evidence

Recorded 2026-08-20 from the working-tree release candidate based on starting
commit `158d033754dd02839d11e86d6217aa1804b31035`.

## Clean environment

- Platform: Linux x86-64
- Python: 3.12.3
- Environment: newly created temporary virtual environment
- Install: `python -m pip install -r requirements-dev.txt`
- Import smoke: `app`, `main`, `qr_core`, and `qr_payloads` imported successfully
- Dependency consistency: `python -m pip check` reported no broken requirements

## Release suite

`python -m unittest discover -s tests -v` passed **48/48** tests in the clean
environment. The passing coverage includes:

- exact authored payload/UTF-8 fixtures and deterministic validation codes;
- all six content types at requested ECL L/M/Q/H;
- version-40 byte boundaries for every ECL and an explicit version-32 symbol;
- independent ZXing-C++ decoding of serialized SVG geometry;
- normal, accepted low-contrast, reversed-polarity, and reduced-border evidence;
- Flask media type, JSON shape, unknown fields, body limit, errors, cache headers,
  CORS absence, redaction, and unexpected-error behavior;
- CLI iterative sessions, hidden WiFi password entry, explicit reveal, redaction,
  cancellation, filesystem failures, safe paths, and collisions;
- CLI/web payload, SVG, warning, and metadata parity;
- XML structure, exact module coordinates/count, colors, dimensions, and absence
  of external/active SVG content.

Python byte-compilation, `node --check static/js/app.js`, `git diff --check`, and
the encoder checksum check also passed. The vendored encoder SHA-256 was:

```text
9f4ed1dd201dcb92b1bc0d6e14f46c754bcff0ce48580c5d7e8ace8f6926c8ef
```

## Dependency and license evidence

`pip-audit -r requirements.txt` reported **no known vulnerabilities** for the
pinned runtime requirements on 2026-08-20.

| Direct package | Version | Reported license |
| --- | --- | --- |
| Flask | 3.1.3 | BSD-3-Clause |
| Gunicorn | 26.1.0 | MIT |
| Pillow (test only) | 12.3.0 | MIT-CMU |
| zxing-cpp (test only) | 3.1.1 | Apache-2.0 |

The vendored Nayuki encoder retains its own MIT notice in `qrcodegen.py`.

## Runtime smoke

A clean Gunicorn 26.1.0 process was bound to localhost with one worker.

- `GET /` returned 200 and the browser root element.
- `POST /api/generate` generated an email fixture at requested/actual Q, returned
  200 plus `Cache-Control: no-store`, and omitted the synthetic body from the
  plaintext response.
- The returned SVG parsed as XML and independently decoded to the exact expected
  percent-encoded mailto payload.
- Gunicorn access output contained only method/path/status/size metadata; it did
  not contain the JSON body or SVG.

The clean interactive terminal flow generated a synthetic WPA/hidden-network
fixture. Password entry was not echoed, the summary stayed redacted, the file was
created with mode `0600`, its SVG had no external doctype or plaintext password,
and independent decoding matched the exact escaped WiFi payload.

## Evidence not available locally

This file does not claim that the GitHub Actions matrix has passed remotely or
that Dependabot has accepted the configuration; both require pushing the branch.
It also does not replace the real-device work in `DEVICE_MATRIX.md`. Milestone C
remains unshipped until representative iOS/Android scanning is recorded and a
release commit/tag is verified.
