# Roadmap

Where Custom QR Code Generator goes after its terminal and web MVPs.

**Direction:** turn a flexible QR renderer into a **trustworthy QR creation
workflow**: the encoded payload is exactly what the user intended, the downloaded
artifact is independently proven to scan, private content is handled carefully,
and the terminal and web surfaces share one validated generation core.

This file owns strategy, release boundaries, and status. The actionable checklist
lives in **[`TASKS.md`](TASKS.md)**.

_Last reviewed: 2026-08-05_

---

## Fixed frame

No calendar deadline or monetary budget was supplied. To keep the roadmap
responsive, the inferred planning baseline is fixed as follows:

| Constraint | Fixed planning baseline |
| --- | --- |
| **Outcome** | A user can create and download a QR code from the terminal or browser, verify that it decodes to the exact intended payload, and understand any scannability or privacy limitation before using it. |
| **Deadline** | End of the sixth calendar week after implementation kickoff. Record the kickoff and resulting end date before Milestone C starts; do not extend the six-week window. |
| **Capacity budget** | One maintainer, at most **30 maintainer-days** across Milestones C–F. No paid infrastructure. |
| **Scope** | Open. Milestone C is protected; later releases are cut, reordered, or deferred as evidence and capacity change. |

The following constraints remain fixed throughout the window:

- SVG remains the primary lossless output and the vendored QR encoder remains
  usable without a network connection.
- CLI and web generation delegate to the same payload, validation, encoding, and
  SVG-rendering core. A surface may differ in interaction, not output semantics.
- User payloads—especially WiFi passwords, email bodies, and SMS text—are not
  persisted, echoed, or logged without explicit user intent.
- Public API input is untrusted, bounded, strictly validated, and returns stable
  client errors instead of raw exception details.
- Unsafe quiet-zone, foreground/background, or capacity choices never receive an
  unqualified success state. Customization cannot silently outrank scannability.
- The generator does not claim a QR works because SVG was produced; completion
  requires an independent decode check plus representative real-device evidence.

If 30 days cannot buy every planned release, ship fewer complete benefits. Do not
trade payload correctness, privacy, or scan confidence for later export formats.

---

## Current baseline and why trust comes next

The repository has two end-to-end surfaces: an interactive terminal generator and
a Flask/React web generator deployed through Render. The terminal supports text,
URL, email, phone, WiFi, and SMS payloads plus colors, error correction, borders,
unique filenames, SVG output, and terminal preview. The web surface generates and
downloads a styled SVG from raw text. The latest web/runtime fixes end at
`7a76579`.

| Observed behavior | Consequence | Roadmap response |
| --- | --- | --- |
| `main.py` and `app.py` contain separate SVG renderers and separate validation assumptions. | The same choices can behave differently between terminal and web, and fixes must be duplicated. | Milestone C creates one shared generation contract and core. |
| Email subject/body and SMS body are concatenated without URI encoding; WiFi fields are inserted without escaping reserved characters. | Spaces, `&`, `?`, semicolons, backslashes, or Unicode can decode to a different payload. | Add canonical, fixture-tested payload builders. |
| CLI filenames are derived with `split('.')[0]` and joined to `saved/` without basename/path validation. | A crafted filename can escape the intended output directory or truncate unexpectedly. | Constrain and atomically create safe output paths. |
| The CLI prints the complete encoded content before generation. | WiFi passwords and private messages can be exposed in terminal history or recordings. | Redact sensitive structured payloads by default. |
| `/api/generate` assumes a JSON object, accepts unchecked colors/content/error levels, has no explicit body limit, exposes exception text, and enables wildcard CORS. | Malformed or abusive requests become 500s, unnecessary cross-origin access, or avoidable resource use. | C adds bounded request validation and stable error handling. |
| CLI borders can be reduced to zero and arbitrary color pairs receive no scanability warning. | A visually valid SVG may be difficult or impossible for common scanners to read. | Define a safe quiet-zone/contrast contract and verify output by decoding it. |
| `test_app.py` prints one response but contains no assertions; no payload, SVG, decoder, CLI, or boundary suite exists. | Generation regressions can ship while the “test” still exits successfully. | Replace it with automated unit, integration, parity, and decode tests. |
| The browser depends at runtime on React, ReactDOM, and Tailwind CDN scripts without a production asset/CSP contract. | The UI depends on third parties and is harder to secure or run reliably. | C applies minimum response safety; E removes the deployment dependency. |
| README structure/runtime instructions omit the web app and refer to a missing `run.bat.template`; Dependabot has an empty package ecosystem. | Setup, support, and dependency maintenance do not match the repository. | Reconcile docs and maintenance automation before release. |
| Vendored `qrcodegen.py` has no recorded upstream version/checksum in this repository. | Encoder provenance and future updates are difficult to audit. | Record its license, origin, version/commit, checksum, and update procedure. |

---

## Milestones

`✅ shipped` · `▶ next` · `⬜ later`

| | Benefit-delivering release | State | Capacity ceiling | Assumption retired |
| --- | --- | --- | --- | --- |
| **A** | Interactive terminal QR generator | ✅ | Shipped | Users value custom SVG QR generation without a hosted service. |
| **B** | Browser generation, preview, download, and deployment | ✅ | Shipped | A browser surface reduces setup friction enough to justify hosting. |
| **C** | Correct, private, independently scannable output | ▶ | 12 days | Trust and successful scanning matter more than adding customization options. |
| **D** | Complete structured-payload workflow in the browser | ⬜ | 7 days | Web users need guided URL/email/phone/WiFi/SMS creation, not only raw text. |
| **E** | Reliable, private-by-default public deployment | ⬜ | 6 days | Removing third-party/runtime and operational fragility supports repeat public use. |
| **F** | Reproducible command-line and API automation | ⬜ | 5 days | Teams want to generate tested QR assets repeatedly from scripts and build workflows. |

The current order is **A → B → C → D → E → F**. Only C is detailed enough to
execute. D–F are option boundaries, not promises; re-plan them after every shipped
release.

### A — Interactive terminal QR generator ✅

The original MVP guides a user through payload type, error correction, colors,
border, filename, SVG generation, and a terminal preview. It creates unique files
under `saved/` and uses the vendored Project Nayuki encoder across QR versions and
error-correction levels.

### B — Browser generation and deployment ✅

The web increment adds a Flask endpoint, browser controls for content/colors/error
correction, inline SVG preview, download, Gunicorn startup, and Render deployment.
Follow-up commits repaired request argument handling, preview/download behavior,
and Windows startup logic. It proves both surfaces are useful enough to harden.

### C — Correct, private, independently scannable output ▶

**Value shipped:** whether a QR is created in the terminal or browser, the user
receives the same validated payload and SVG, an honest warning/error for unsafe
choices, and evidence that the artifact decodes back to the intended content.

**Riskiest assumption:** users care more about reliable scanning and exact payload
semantics than they do about adding PNG, logos, templates, or more styling.

The release includes:

1. Define one request/result contract and extract a shared generation core for
   payload building, validation, encoder selection, SVG rendering, and metadata.
   Both CLI and Flask become adapters around it.
2. Canonically encode text, URL, email, phone, WiFi, and SMS inputs, including
   reserved-character escaping, Unicode, security modes, optional fields, and
   privacy-aware summaries.
3. Strictly validate content/capacity, color syntax, error correction, border,
   filenames, JSON shape, and request size. Report requested and actual error
   correction when the encoder safely boosts it.
4. Define a scanability policy for quiet zone, color separation/polarity, symbol
   size, and payload capacity. Unsafe customization yields actionable validation,
   not a generic success.
5. Prove the encoded content with an independent decoder matrix and real-device
   fixtures across payload types, correction levels, Unicode, boundary lengths,
   and representative color/border choices.
6. Remove secret echoing, constrain output paths, return stable API errors, remove
   unnecessary wildcard CORS, and avoid exposing internal exceptions.
7. Record encoder provenance and replace the print-only test with a deterministic
   test/CI/release baseline.

**Protected cut line:** shared-core parity, exact payload encoding, bounded input,
safe filenames, sensitive-content redaction, scanability decisions, independent
decode evidence, and regression tests ship together. Visual redesign, new output
formats, logos, templates, and batch generation are cut first if the 12-day
ceiling is threatened.

**Not in C:** feature parity in the browser, PNG/JPEG/PDF, embedded logos, dynamic
or trackable QR codes, accounts, analytics, persistence, or a public API contract.

### D — Complete structured-payload workflow in the browser ⬜

**Value shipped:** a browser user can create correct text, URL, email, phone, WiFi,
or SMS codes through fields that explain what will be encoded, without manually
constructing URI/WiFi syntax.

Likely scope is a payload-type selector, type-specific validation, privacy cues for
secrets, border/scanability controls, debounced preview, accessible errors, and a
safe downloadable filename. It reuses C's shared builders and does not invent a
second client-side encoding contract.

**Assumption retired:** structured guidance materially reduces invalid payloads and
makes the browser more useful than a raw-text wrapper.

### E — Reliable, private-by-default public deployment ⬜

**Value shipped:** the hosted generator loads predictably, does not depend on
third-party CDNs at runtime, does not retain payloads, and fails safely under bad
or excessive requests.

Candidate scope is locally built or dependency-free frontend assets, a restrictive
content security policy and security headers, redacted structured logs, health and
smoke checks, explicit request/time/concurrency safeguards, correct proxy/runtime
configuration, dependency update automation, and a documented privacy statement.

**Assumption retired:** the hosted surface receives enough repeat use to justify a
maintained production path instead of being treated as a demo.

### F — Reproducible command-line and API automation ⬜

**Value shipped:** a user can generate the same verified asset non-interactively in
a script or CI job and receive machine-readable metadata/errors.

Candidate scope is `argparse`-based single generation, stdin/JSON input, explicit
stdout/file behavior, deterministic safe filenames, stable exit codes, a versioned
API envelope, and an optional small batch manifest. SVG remains the default; a
raster export is considered only if evidence shows it is needed and decoder tests
can guard it.

**Assumption retired:** repeatable automation creates more value than another
interactive customization feature.

---

## Definition of done for every release

A milestone is shipped only when:

- Its end-to-end benefit works from a clean supported-Python environment in every
  surface it claims to support.
- Unit, API, CLI, parity, SVG/XML, independent-decode, and security-boundary tests
  pass where applicable.
- Representative outputs decode to the exact expected bytes/text in an independent
  decoder and scan on real devices at practical display/print sizes.
- Sensitive fixture values do not appear unexpectedly in stdout, logs, errors,
  filenames, analytics, or persisted server state.
- Malformed or oversized user input produces bounded, documented errors rather than
  a 500 or partial artifact.
- `README.md`, `CONTRIBUTING.md`, `TASKS.md`, this roadmap, dependency metadata,
  deployment config, and changelog/version evidence agree with shipped behavior.
- A commit or release identifier and verification evidence are recorded in the
  milestone table; completion requires proof, not intent.

---

## Retrospective and re-plan cadence

Run a checkpoint after each release, or after six maintainer-days without a
release, whichever comes first.

At each checkpoint:

1. Review decode failures, payload mismatches, validation friction, privacy leaks,
   API abuse/errors, cross-surface drift, and capacity spent.
2. Decide whether the release's risky assumption was supported, contradicted, or
   still untested.
3. Re-cut the remaining scope inside the fixed six-week/30-day frame. Detail only
   the next milestone and keep later releases coarse.
4. Update the milestone table, evidence, capacity remaining, and review date in
   both roadmap files.

A payload mismatch, secret leak, path escape, or unscannable “success” interrupts
feature work immediately. The correction replaces planned scope; the deadline and
capacity do not move.

---

## Explicitly parked

These are not part of the six-week frame without new evidence and a new roadmap:

- Dynamic/redirectable QR codes, link analytics, accounts, saved history, or a
  database.
- Embedded logos, decorative modules/eyes, gradients, rounded patterns, or image
  backgrounds before the independent decoder matrix can cover them.
- PNG, JPEG, PDF, print sheets, or bulk campaigns unless D/F evidence prioritizes
  them.
- URL shortening, hosted landing pages, malware/reputation scanning, or claims that
  destination content is safe.
- Paid hosting, commercial rate tiers, or an SLA.
- Native mobile or desktop GUI applications.
