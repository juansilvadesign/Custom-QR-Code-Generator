"""Write the Milestone C release fixture set for the manual device matrix.

`docs/milestone-c/DEVICE_MATRIX.md` requires a maintainer to scan representative
artifacts on real phones. This script materializes exactly those artifacts from
the committed fixture catalog, verifies each one against the independent decoder
before writing it, and emits a print sheet plus a manifest to record results in.

It is a release tool, not production code: it imports the development-only
decoder, and nothing under the Flask or terminal surface imports this module.

Usage:

    python export_release_fixtures.py [--output-dir DIR] [--skip-decode]

Exit status is non-zero if any fixture fails to decode to its exact expected
payload, so the script cannot quietly emit an artifact it did not verify.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent / "tests"))

from qr_contract import GenerationRequest, GenerationResult  # noqa: E402
from qr_core import generate, warning_codes  # noqa: E402

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "tests" / "fixtures" / "payloads.json"
DEFAULT_OUTPUT_DIR = ROOT / "fixtures" / "release"


class FixtureRow:
    """One device-matrix row: how to generate it and what to expect back."""

    def __init__(
        self,
        slug: str,
        matrix_row: str,
        fixture_id: str | None = None,
        *,
        expected_warnings: tuple[str, ...] = (),
        medium: str = "Display / 320 px",
        overrides: dict[str, Any] | None = None,
    ) -> None:
        self.slug = slug
        self.matrix_row = matrix_row
        self.fixture_id = fixture_id
        self.expected_warnings = expected_warnings
        self.medium = medium
        self.overrides = overrides or {}


# The first seven rows mirror `docs/milestone-c/DEVICE_MATRIX.md` one-for-one.
# Row 08 adds the tightest border the contract still accepts (MIN_ACCEPTED_BORDER),
# which is the value the automated evidence matrix in tests/test_svg_decode.py
# already covers; row 04 keeps the three-module border named in the document.
ROWS: tuple[FixtureRow, ...] = (
    FixtureRow(
        "01-text-unicode-normal",
        "iOS built-in Camera, display",
        fixture_id="text_unicode_reserved",
    ),
    FixtureRow(
        "02-url-normal",
        "Android built-in Camera or Lens, display",
        fixture_id="url_normalized",
    ),
    FixtureRow(
        "03-wifi-wpa-hidden-printed",
        "Either device, printed ~30 mm",
        fixture_id="wifi_wpa_reserved_hidden",
        medium="Printed / approximately 30 mm",
    ),
    FixtureRow(
        "04-text-border3",
        "Reduced quiet zone (3 modules)",
        fixture_id="text_ascii",
        overrides={"border": 3},
        expected_warnings=("reduced_quiet_zone",),
    ),
    FixtureRow(
        "05-text-low-contrast",
        "Accepted low contrast",
        fixture_id="text_ascii",
        overrides={"foreground": "#777777"},
        expected_warnings=("low_contrast",),
    ),
    FixtureRow(
        "06-text-reversed-polarity",
        "Reversed polarity",
        fixture_id="text_ascii",
        overrides={"foreground": "#FFFFFF", "background": "#000000"},
        expected_warnings=("reversed_polarity",),
    ),
    FixtureRow(
        "07-v40-boundary-L",
        "Version-40 capacity boundary, both device families",
        overrides={"requested_error_correction": "L"},
        medium="Display / recommended minimum",
    ),
    FixtureRow(
        "08-text-border2-minimum",
        "Minimum accepted quiet zone (2 modules)",
        fixture_id="text_ascii",
        overrides={"border": 2},
        expected_warnings=("reduced_quiet_zone",),
    ),
)


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def resolve_row(row: FixtureRow, catalog: dict[str, Any]) -> tuple[GenerationRequest, str]:
    """Return the canonical request for a row plus its exact expected payload."""

    if row.slug == "07-v40-boundary-L":
        # The largest symbol the contract admits: ECL L at its declared byte limit.
        boundary = next(
            entry
            for entry in catalog["capacityBoundaries"]
            if entry["errorCorrection"] == "L"
        )
        text = boundary["value"] * boundary["atLimit"]
        fields: dict[str, Any] = {"text": text}
        payload_type = "text"
        expected = text
    else:
        fixture = next(
            entry for entry in catalog["payloads"] if entry["id"] == row.fixture_id
        )
        fields = dict(fixture["fields"])
        payload_type = fixture["payloadType"]
        expected = fixture["expected"]

    values: dict[str, Any] = {
        "payload_type": payload_type,
        "fields": fields,
        "requested_error_correction": "M",
        "foreground": "#000000",
        "background": "#FFFFFF",
        "border": 4,
    }
    values.update(row.overrides)
    return GenerationRequest(**values), expected


def verify_decode(result: GenerationResult, expected: str) -> None:
    from helpers import decode_svg  # dev-only dependency, imported lazily

    decoded = decode_svg(result.svg)
    if decoded != expected:
        raise AssertionError(
            "decoded payload does not match the expected fixture payload "
            f"(decoded {len(decoded)} chars, expected {len(expected)} chars)"
        )


def display_path(path: Path) -> str:
    """Show a repo-relative path when possible, else the absolute one.

    `--output-dir` may point anywhere, so this must not assume it sits under the
    repository root.
    """

    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def strip_xml_declaration(svg: str) -> str:
    if svg.startswith("<?xml"):
        return svg.split("?>", 1)[1].lstrip("\n")
    return svg


def build_print_sheet(entries: list[dict[str, Any]]) -> str:
    """Build a print sheet that renders each fixture at a defensible size."""

    blocks = []
    for entry in entries:
        printed = "approximately 30 mm" in entry["medium"]
        width_mm = 30 if printed else 45
        warning_text = ", ".join(entry["warnings"]) or "none"
        blocks.append(
            f"""    <figure class="fixture">
      <div class="code" style="width:{width_mm}mm">{strip_xml_declaration(entry['svg'])}</div>
      <figcaption>
        <strong>{html.escape(entry['slug'])}</strong><br>
        {html.escape(entry['matrix_row'])}<br>
        <span class="meta">type {html.escape(entry['payload_type'])} &middot;
        ECL {html.escape(entry['requested_ecl'])}&rarr;{html.escape(entry['actual_ecl'])} &middot;
        v{entry['version']} &middot; {entry['module_count']} modules &middot;
        border {entry['border']} &middot; {width_mm} mm</span><br>
        <span class="meta">warnings: {html.escape(warning_text)}</span>
      </figcaption>
    </figure>"""
        )

    body = "\n".join(blocks)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Milestone C release fixtures - print sheet</title>
<style>
  @page {{ margin: 12mm; }}
  body {{ font-family: system-ui, sans-serif; color: #111; background: #fff; }}
  h1 {{ font-size: 14pt; }}
  p.note {{ font-size: 9pt; max-width: 150mm; color: #444; }}
  .grid {{ display: flex; flex-wrap: wrap; gap: 10mm; }}
  .fixture {{ margin: 0; page-break-inside: avoid; }}
  .code {{ background: #fff; }}
  .code svg {{ width: 100%; height: auto; display: block; }}
  figcaption {{ font-size: 8pt; margin-top: 2mm; max-width: 45mm; line-height: 1.35; }}
  .meta {{ color: #555; }}
</style>
</head>
<body>
<h1>Milestone C release fixtures</h1>
<p class="note">Print at 100% scale with no fit-to-page scaling, then record each
result in <code>docs/milestone-c/DEVICE_MATRIX.md</code>. All credentials below are
synthetic fixture values and are not real networks or passwords.</p>
<div class="grid">
{body}
</div>
</body>
</html>
"""


def build_manifest(entries: list[dict[str, Any]], decoded: bool) -> str:
    lines = [
        "# Milestone C release fixture manifest",
        "",
        "Generated by `export_release_fixtures.py` from `tests/fixtures/payloads.json`.",
        "Regenerate rather than edit. Payload summaries are the contract's own",
        "privacy-safe summaries; exact payloads are deliberately not reproduced here.",
        "",
        f"Independent decode verification: **{'passed' if decoded else 'SKIPPED'}**.",
        "",
        "| File | Matrix row | Type | ECL req/act | Version | Modules | Border | Contrast | Polarity | Min px | Warnings | Summary |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        warning_text = ", ".join(entry["warnings"]) or "none"
        lines.append(
            f"| `{entry['slug']}.svg` | {entry['matrix_row']} | {entry['payload_type']} "
            f"| {entry['requested_ecl']}/{entry['actual_ecl']} | {entry['version']} "
            f"| {entry['module_count']} | {entry['border']} | {entry['contrast']}:1 "
            f"| {entry['polarity']} | {entry['min_px']} | {warning_text} "
            f"| {entry['summary']} |"
        )
    lines.extend(
        [
            "",
            "## Recording results",
            "",
            "Scan each file on a real device and fill the matching row in",
            "`docs/milestone-c/DEVICE_MATRIX.md` with the device, OS, scanner app and",
            "version, rendered size, medium, lighting, and the exact decoded result.",
            "",
            "A normal-polarity, four-module, high-contrast fixture that fails to scan is a",
            "Milestone C blocker. A warned fixture that fails keeps its warning and narrows",
            "the release claim instead.",
            "",
        ]
    )
    return "\n".join(lines)


def export(output_dir: Path, skip_decode: bool) -> int:
    catalog = load_catalog()
    output_dir.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, Any]] = []
    failures: list[str] = []

    for row in ROWS:
        request, expected = resolve_row(row, catalog)
        result = generate(request)

        observed_warnings = warning_codes(result.warnings)
        if observed_warnings != row.expected_warnings:
            failures.append(
                f"{row.slug}: expected warnings {row.expected_warnings or ('none',)}, "
                f"got {observed_warnings or ('none',)}"
            )

        if not skip_decode:
            try:
                verify_decode(result, expected)
            except AssertionError as error:
                failures.append(f"{row.slug}: {error}")
                continue
            except ImportError as error:
                print(
                    f"error: independent decoder unavailable ({error}).\n"
                    "Install the development requirements or pass --skip-decode.",
                    file=sys.stderr,
                )
                return 2

        path = output_dir / f"{row.slug}.svg"
        path.write_text(result.svg, encoding="utf-8")

        entries.append(
            {
                "slug": row.slug,
                "matrix_row": row.matrix_row,
                "medium": row.medium,
                "svg": result.svg,
                "payload_type": result.payload_type,
                "requested_ecl": result.requested_error_correction,
                "actual_ecl": result.actual_error_correction,
                "version": result.version,
                "module_count": result.module_count,
                "border": result.border,
                "contrast": result.scanability.contrast_ratio,
                "polarity": result.scanability.polarity,
                "min_px": result.scanability.recommended_minimum_pixels,
                "warnings": list(observed_warnings),
                "summary": result.summary,
            }
        )
        print(f"wrote {display_path(path)}")

    if failures:
        print("\nFAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    sheet_path = output_dir / "print-sheet.html"
    sheet_path.write_text(build_print_sheet(entries), encoding="utf-8")
    print(f"wrote {display_path(sheet_path)}")

    manifest_path = output_dir / "MANIFEST.md"
    manifest_path.write_text(build_manifest(entries, not skip_decode), encoding="utf-8")
    print(f"wrote {display_path(manifest_path)}")

    verified = "all independently decoded OK" if not skip_decode else "decode SKIPPED"
    print(f"\n{len(entries)} fixtures, {verified}.")
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="directory to write fixtures into (default: fixtures/release)",
    )
    parser.add_argument(
        "--skip-decode",
        action="store_true",
        help="write fixtures without independent decoder verification",
    )
    arguments = parser.parse_args(list(argv) if argv is not None else None)
    return export(arguments.output_dir.resolve(), arguments.skip_decode)


if __name__ == "__main__":
    raise SystemExit(main())
