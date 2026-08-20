# Contributing

Thanks for improving Custom QR Code Generator. Payload correctness, privacy, and
independent scan evidence are release constraints, not optional polish. Keep a
change small enough that those properties remain reviewable.

## Set up

Requires Python 3.10–3.14 and Git.

```bash
git clone https://github.com/YOUR_USERNAME/Custom-QR-Code-Generator.git
cd Custom-QR-Code-Generator
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Run the surfaces locally:

```bash
python main.py
flask --app app run --debug
```

`run.bat` launches the terminal surface on Windows and creates `.venv` when it is
missing.

## Architecture boundaries

- `qr_contract.py` owns plain canonical request, result, warning, and error values.
- `qr_payloads.py` owns exact structured payload semantics.
- `qr_core.py` owns validation, Nayuki invocation, scanability assessment,
  metadata, matrix extraction, and the only SVG renderer.
- `qr_files.py` owns safe local output naming and exclusive creation.
- `main.py` and `app.py` are adapters. Do not add a payload rule, capacity rule,
  or second SVG renderer to either surface.
- Test code may independently parse/rasterize SVG, but production code must not
  depend on Pillow or ZXing.

The full contract is in
[`docs/GENERATION_CONTRACT.md`](docs/GENERATION_CONTRACT.md). If behavior changes,
update the contract, authored fixtures, tests, README, and changelog together.

## Make a change

1. Create a focused branch: `git switch -c fix/short-description`.
2. Confirm the tree and baseline: `git status --short` and `git diff`.
3. Add or adjust an authored expectation in `tests/fixtures/payloads.json` before
   changing payload semantics.
4. Implement through the shared core and keep framework/terminal concerns at the
   edges.
5. Run the focused test module while iterating, then the complete release suite.
6. Review the diff for payload values, credentials, machine paths, generated
   artifacts, or debug logging before committing.

Use standard-library type hints and focused functions. Public errors must have a
stable lowercase underscore code and a payload-safe message. Never return raw
exception strings from HTTP or print them on the CLI.

## Required checks

Every pull request:

```bash
python -m unittest discover -s tests -v
python -m pip check
```

Dependency or release changes also require:

```bash
pip-audit -r requirements.txt
pip-licenses --from=mixed --packages Flask gunicorn Pillow zxing-cpp
```

The suite must contain assertions; printing a response is not a test. Relevant
changes need coverage in these layers:

- exact payload builder output and UTF-8 bytes;
- validation/error codes and capacity boundaries;
- API media type/body size/JSON shape/cache/privacy behavior;
- CLI redaction, cancellation, iterative sessions, paths, collisions, and
  filesystem failures;
- CLI/web parity for payload, SVG, warnings, and metadata;
- parsed SVG dimensions, elements, colors, module coordinates, and absence of
  active/external content;
- independent ZXing decode of serialized SVG geometry.

Do not weaken or skip decoder tests to make an encoder/rendering change pass.

## Adding or changing payload semantics

Author exact inputs and output text in `tests/fixtures/payloads.json`, including
reserved characters and non-Latin text relevant to the change. Compare both the
Unicode string and UTF-8 bytes; do not calculate the expected value by calling
the function under test.

Keep validation honest. The project validates formatting limits but does not
claim an email is deliverable, phone exists, WiFi credential works, URL is safe,
or destination content is benign.

A compatibility-affecting change must be called out in `CHANGELOG.md`, especially
URI encoding, WiFi escaping, normalization, ECL boosting, borders/colors,
filenames, response envelopes, or redaction.

## Privacy and security review

Use synthetic secrets with unique markers in tests. Assert they are absent from
stdout, logs, errors, metadata, and filenames unless a test explicitly selects
the reveal path. Generated SVG naturally represents the payload as modules; it
must not contain a plaintext copy.

For API work, test missing/wrong content type, malformed/scalar/array JSON,
unknown fields, body limit, invalid values, unexpected exceptions, `no-store`,
and absence of wildcard CORS. Do not log request bodies or SVG responses.

For output work, test Unix and Windows path separators, traversal, absolute paths,
dotfiles, meaningful/repeated extensions, reserved names, collisions, and failed
writes. Existing files must never be overwritten.

## Updating `qrcodegen.py`

Follow [`docs/ENCODER_PROVENANCE.md`](docs/ENCODER_PROVENANCE.md) exactly. The file
must match an immutable upstream source byte-for-byte, retain its MIT notice, and
have a recorded checksum. An encoder update requires the full automated decoder
matrix and the representative manual device matrix before release.

## Pull request description

Include:

- the user-visible problem and why this scope solves it;
- payload/API compatibility effects;
- privacy, path, capacity, and scanability risks considered;
- exact commands and results used for verification;
- manual device rows when scan behavior or the encoder changed;
- screenshots only when the browser presentation changed.

Use an imperative commit subject under 72 characters. Keep unrelated cleanup in a
separate change.

## Release gate

A release is not complete because SVG generation returned success. Before tag or
deployment, a maintainer must:

1. install from a clean supported-Python environment;
2. run the complete automated suite, dependency check, vulnerability audit, and
   license report;
3. exercise one terminal structured flow and the browser/API download flow;
4. confirm no test secret is unexpectedly printed, logged, named, or persisted;
5. complete the real-device rows in
   `docs/milestone-c/DEVICE_MATRIX.md` for scan-affecting work;
6. record release commit/tag and evidence in `ROADMAP.md`, `TASKS.md`, and
   `CHANGELOG.md`.

See `ROADMAP.md` for release boundaries. New export formats, logos, decorative QR
modules, persistence, analytics, and batch generation remain out of Milestone C.
