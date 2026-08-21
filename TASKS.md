# Tasks

The living implementation checklist. Strategy, release boundaries, and the fixed
frame live in **[`ROADMAP.md`](ROADMAP.md)**.

_Last reviewed: 2026-08-21_

> Milestones **A–B** are shipped. **C is the only execution-ready milestone.**
> Items under D–F are deliberately coarse and must be re-planned after the
> preceding retrospective.

---

## Next — Milestone C: correct, private, independently scannable output ▶

**Capacity ceiling:** 12 maintainer-days.

**Release-candidate checkpoint (2026-08-21):** all locally executable work below
is complete, and the remote gate is now closed. The branch is pushed at
`6ea790f`, the full GitHub Actions matrix passes **10/10** including both Windows
legs, and Dependabot is accepted and green. Two release gates remain open:
real-device scan evidence, and the final release commit/tag plus D re-plan.

The first push (`0512cf3`) failed CI on both Windows runners: `.gitattributes`
did not disable end-of-line conversion for the vendored encoder, so those
checkouts arrived as CRLF and the pinned SHA-256 did not match. `qrcodegen.py`
now carries `-text`, which fixed it.

**Exit outcome:** terminal and web requests pass through one validated generation
core, produce the same exact payload/SVG semantics, reject or explain unsafe
choices, protect sensitive content, and pass independent decoder tests.

### 0. Start the fixed frame

- [x] Record the implementation kickoff date and resulting six-week end date in
      [`ROADMAP.md`](ROADMAP.md#fixed-frame); keep the 30-day total and C's 12-day
      ceiling fixed.
- [x] Capture a clean git baseline and record the starting commit in C's release
      notes. Preserve unrelated work if the tree is not clean.
- [x] Create a fixture catalog with exact expected payloads for plain ASCII and
      Unicode text, normalized URLs, email optional fields, international phone,
      WiFi WPA/WEP/nopass/hidden networks, SMS bodies, empty input, and capacity
      boundaries.
- [x] Include reserved characters (`&`, `?`, `;`, `:`, comma, backslash, quotes,
      percent, spaces, and line breaks) plus non-Latin text in the fixture catalog.
- [x] Capture representative current CLI/web SVGs and decoded results before
      changing generation semantics.

### 1. Lock the generation contract

- [x] Define a canonical generation request with payload type/fields, requested
      error correction, foreground/background, border, and optional output name.
- [x] Define a canonical result with encoded payload, privacy-safe summary, SVG,
      QR version/module size/mask, requested and actual error correction, border,
      warnings, and deterministic error codes.
- [x] Decide and document URL normalization, email/SMS query encoding, phone
      normalization limits, and WiFi escaping/security/hidden-field semantics.
- [x] Preserve arbitrary valid Unicode and define whether output comparison is by
      exact text, UTF-8 bytes, or normalized form; never normalize invisibly.
- [x] Define strict limits by request bytes and encoder capacity for each error
      correction level, including the difference between too-large requests and
      invalid structured fields.
- [x] Define safe defaults and allowed ranges for border and colors. Document when
      a risky choice is rejected versus returned with a warning.
- [x] Define encoder ECL boosting semantics: either request an exact level or expose
      both requested and actual levels when the encoder increases protection.
- [x] Make SVG structure deterministic enough for cross-surface parity while
      keeping semantic tests resilient to harmless formatting.

### 2. Build one shared core

- [x] Extract payload builders, validation, `qrcodegen` invocation, SVG rendering,
      scanability assessment, and result metadata into import-safe shared modules.
- [x] Make `main.py` a terminal adapter and `app.py` a Flask adapter; neither may
      maintain a second SVG renderer or payload rule.
- [x] Keep framework/terminal concerns out of the core so unit tests can call it
      with plain Python values.
- [x] Remove the external SVG doctype and emit well-formed minimal XML with only
      validated numeric/color/path data.
- [x] Preserve the SVG quiet zone and module grid exactly; prevent renderer changes
      from moving, rounding, or merging functional modules incorrectly.
- [x] Record the vendored `qrcodegen.py` upstream URL, license notice, upstream
      version/commit, local checksum, and deliberate local modifications, if any.
- [x] Add a documented encoder-update procedure that requires the full decoder
      matrix before changing the vendored file.

### 3. Correct structured payloads and CLI safety

- [x] Encode email subject/body and SMS fields with the chosen URI rules so reserved
      characters and Unicode round-trip exactly.
- [x] Escape WiFi SSID/password reserved characters, validate security modes, omit
      irrelevant credentials for `nopass`, and preserve the hidden-network flag.
- [x] Normalize only clearly incomplete URLs; preserve valid schemes deliberately
      allowed by the contract and reject malformed values with actionable errors.
- [x] Validate required fields for email, phone, WiFi, and SMS without pretending to
      prove that an address, number, network, or destination exists.
- [x] Replace recursive “create another” calls with an iterative session loop.
- [x] Replace bare exception handling with specific cancellation, validation,
      capacity, filesystem, and unexpected-error paths.
- [x] Stop printing complete sensitive payloads. Show a redacted summary by default
      and require explicit intent to reveal/copy a WiFi password or private body.
- [x] Sanitize the requested filename to a safe basename, preserve meaningful dots,
      force the `.svg` suffix, and prove the resolved path stays inside `saved/`.
- [x] Create the output directory safely and write via an exclusive/atomic path so
      collision handling cannot overwrite an existing file.

### 4. Harden the generation API

- [x] Require `application/json` and a JSON object; reject missing, malformed,
      scalar, array, and unknown-field requests with stable 4xx responses.
- [x] Set an explicit request-body limit before JSON parsing and map oversized
      requests to a stable 413 response.
- [x] Validate payload fields, strict six-digit colors, error level, border, and
      content capacity through the shared core rather than silently defaulting bad
      values.
- [x] Map validation, capacity, unsupported-type, media-type, and unexpected errors
      to a documented response envelope and status code.
- [x] Never return raw exception strings, filesystem details, stack traces, or
      payload content in production errors.
- [x] Remove wildcard CORS for the same-origin application. If a future consumer
      requires cross-origin access, add an explicit allowlist as a separate product
      decision.
- [x] Add `Cache-Control: no-store` to payload-bearing responses and ensure app/
      proxy logs do not include request bodies or generated SVG content.
- [x] Return QR metadata and warnings beside SVG so the browser can explain what
      was generated instead of inferring success from HTTP 200 alone.

### 5. Define and prove scanability

- [x] Choose a documented, implementation-independent contrast/polarity assessment
      and label it as a scanability guard—not a guarantee or accessibility score.
- [x] Preserve a safe quiet-zone default. Reject or strongly warn on reduced borders
      according to evidence from the decoder/device matrix.
- [x] Include QR version, module count, border, and recommended minimum rendered
      dimensions in result metadata without claiming one universal physical size.
- [x] Add an independent decoder as a development/test dependency, not a production
      runtime dependency.
- [x] Decode generated fixtures and compare exact expected payloads across all six
      content types, four requested error levels, Unicode, and capacity boundaries.
- [x] Test representative high/low contrast, normal/reversed polarity, safe/reduced
      border, and small/large QR versions; encode expected rejection/warning/pass
      outcomes from evidence.
- [ ] Scan a release fixture set with representative real mobile scanners and
      record device/app, display/print size, lighting/medium, and result.
      Generate the artifacts first with `python export_release_fixtures.py`; it
      writes the eight matrix fixtures, a print sheet, and a manifest into
      `fixtures/release/` and refuses to emit anything it cannot independently
      decode.
- [x] Never make a release claim broader than the automated and manual matrix.

### 6. Replace the print-only test with a release suite

- [x] Convert `test_app.py` into assertions under a standard test runner and split
      unit, endpoint, CLI/filesystem, parity, SVG/XML, decoder, and security cases
      as the suite grows.
- [x] Test every payload fixture for exact builder output and exact independent
      decode output.
- [x] Test malformed colors, unknown ECL/type, wrong JSON shapes/media types,
      empty/oversized content, encoder capacity failure, and stable error codes.
- [x] Test safe filenames against `..`, absolute paths, separators, dotfiles,
      repeated dots/extensions, reserved names where relevant, collisions, and
      filesystem failures.
- [x] Test that sensitive fixture values are absent from captured stdout, logs,
      errors, response metadata, and filenames unless explicit reveal was selected.
- [x] Test CLI/web parity from the same canonical request, comparing payload,
      warnings, metadata, module matrix, and semantic SVG output.
- [x] Parse every SVG as XML and assert dimension, background, path/module count,
      colors, absence of external references/scripts, and deterministic structure.
- [x] Add CI for the actually supported Python range and operating systems; use
      evidence to replace the unverified README claim of Python 3.7+.

### 7. Reconcile dependencies, docs, and release evidence

- [x] Separate runtime and development/test dependencies, pin or constrain them
      deliberately, and run a current dependency/license/security audit before
      release.
- [x] Fix `.github/dependabot.yml` to monitor the real Python package manifest and
      verify the configuration is accepted. Accepted and green on 2026-08-20; the
      obsolete `Flask-Cors` PR #1 was closed on 2026-08-21 because Milestone C
      removed that dependency.
- [x] Update `README.md` to document both CLI and web surfaces, exact supported
      payloads per surface, privacy behavior, validation/scanability limits, actual
      files, correct `run.bat` instructions, deployment, and test commands.
- [x] Update `CONTRIBUTING.md` so completed web/API work is not still listed as a
      future idea and so its test/release checklist is executable.
- [x] Add `CHANGELOG.md` and record changed payload encoding, validation, errors,
      filename behavior, redaction, and compatibility notes.
- [x] Import/run the project from a clean environment, execute the terminal fixture
      flow, exercise the Flask endpoint/browser, and download/open the resulting
      SVGs.
- [x] Verify no secret is persisted or logged, no filename escapes `saved/`, bad
      requests are bounded, and all release fixtures independently decode.
- [ ] Record the release commit/tag and verification evidence in
      [`ROADMAP.md`](ROADMAP.md), mark C shipped, and re-plan D inside the remaining
      capacity.

---

## Later — Milestone D: complete structured-payload workflow in the browser ⬜

Do not expand these items until C proves shared payload correctness and scanability.

- [ ] Add a payload-type selector and guided fields for text, URL, email, phone,
      WiFi, and SMS using only the shared builders.
- [ ] Show the exact privacy-safe encoded summary, required/optional fields, and
      field-level errors before generation.
- [ ] Expose border and scanability feedback without allowing visual customization
      to hide a warning.
- [ ] Add an accessible debounced preview with stale/loading/error states and no
      accidental submission of incomplete secret fields.
- [ ] Generate a safe meaningful download filename and expose QR metadata with the
      saved SVG.
- [ ] Validate mobile layout, keyboard/focus, contrast, zoom, and screen-reader
      behavior.
- [ ] Run the checkpoint and re-cut E/F using observed web usage and errors.

---

## Later — Milestone E: reliable, private-by-default public deployment ⬜

- [ ] Replace CDN runtime scripts with locally built or dependency-free static
      assets and add a restrictive content security policy.
- [ ] Add security headers, proxy-aware production configuration, redacted
      structured logs, and a documented no-retention privacy statement.
- [ ] Add explicit request, timeout, concurrency, and abuse safeguards proportionate
      to the free hosted service.
- [ ] Add health/readiness and deployed smoke checks that generate and decode a
      non-sensitive fixture.
- [ ] Verify clean deploy/rollback behavior, environment versions, dependency
      updates, and helpful safe failure when the service is unavailable.

---

## Later — Milestone F: reproducible command-line and API automation ⬜

- [ ] Validate demand for scripting or batch generation before expanding the
      interactive CLI.
- [ ] Add `argparse`-based non-interactive generation with stable flags, stdin/JSON,
      stdout/file rules, exit codes, warnings, and machine-readable metadata.
- [ ] Version the API request/result envelope only after C/D semantics stabilize.
- [ ] Add an optional bounded batch manifest with deterministic safe filenames and
      per-item outcomes; one bad item must not obscure the rest.
- [ ] Consider one raster output only if user evidence prioritizes it and the
      decoder matrix can verify resolution, quiet zone, and payload fidelity.

---

## Completed — Milestone B: browser generation and deployment ✅

- [x] Add a Flask endpoint that generates SVG through the vendored encoder.
- [x] Add browser controls for raw content, foreground/background colors, and error
      correction.
- [x] Preview the returned SVG and download it from the browser.
- [x] Configure Gunicorn and Render deployment.
- [x] Repair request argument handling, preview/download behavior, and Windows
      launcher detection through the latest commit `7a76579`.

---

## Completed — Milestone A: interactive terminal generator ✅

- [x] Guide users through text, URL, email, phone, WiFi, and SMS payload entry.
- [x] Support four error-correction choices, custom foreground/background colors,
      and configurable borders.
- [x] Generate scalable SVG through the bundled `qrcodegen.py` encoder.
- [x] Create a `saved/` directory and avoid ordinary filename collisions.
- [x] Render an optional ANSI/Unicode terminal preview.
- [x] Provide a Windows launcher and document local installation/use.

---

## Parked — not committed in the current frame

- Dynamic/redirectable QR codes, link analytics, accounts, history, or a database.
- Embedded logos, decorative modules/eyes, gradients, rounded patterns, or image
  backgrounds before decoder evidence covers them.
- PNG/JPEG/PDF, print sheets, or bulk campaigns without user evidence.
- URL shortening, landing-page hosting, destination reputation scanning, or safety
  guarantees about linked content.
- Paid hosting tiers, an SLA, native mobile apps, or desktop GUI packaging.
