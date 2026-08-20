from __future__ import annotations

import unittest
from xml.etree import ElementTree

from qr_contract import GenerationRequest
from qr_core import generate, warning_codes
from tests.helpers import (
    SVG_NAMESPACE,
    decode_svg,
    load_fixture_catalog,
    parse_svg,
    svg_module_coordinates,
)


class SvgAndIndependentDecodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_fixture_catalog()

    def _generate_fixture(
        self,
        fixture: dict[str, object],
        error_correction: str = "M",
        **overrides: object,
    ):
        values = {
            "payload_type": fixture["payloadType"],
            "fields": fixture["fields"],
            "requested_error_correction": error_correction,
            "foreground": "#000000",
            "background": "#FFFFFF",
            "border": 4,
        }
        values.update(overrides)
        return generate(GenerationRequest(**values))

    def test_svg_is_minimal_well_formed_and_matches_the_matrix(self) -> None:
        result = self._generate_fixture(self.catalog["payloads"][1])
        root, rectangle, path = parse_svg(result.svg)
        self.assertEqual(root.tag, f"{{{SVG_NAMESPACE}}}svg")
        self.assertEqual(len(root), 2)
        self.assertEqual(rectangle.attrib["fill"], result.background)
        self.assertEqual(path.attrib["fill"], result.foreground)
        self.assertNotIn("DOCTYPE", result.svg)
        self.assertNotIn("<script", result.svg.lower())
        self.assertNotIn("href=", result.svg.lower())
        self.assertNotIn("onload=", result.svg.lower())
        ElementTree.fromstring(result.svg)

        expected_dimension = result.module_count + result.border * 2
        self.assertEqual(
            root.attrib["viewBox"],
            f"0 0 {expected_dimension} {expected_dimension}",
        )
        coordinates = svg_module_coordinates(result.svg)
        expected_coordinates = {
            (x + result.border, y + result.border)
            for y, row in enumerate(result.matrix)
            for x, dark in enumerate(row)
            if dark
        }
        self.assertEqual(coordinates, expected_coordinates)
        self.assertEqual(len(coordinates), sum(map(sum, result.matrix)))
        self.assertEqual(path.attrib["d"].count("M"), sum(map(sum, result.matrix)))

    def test_every_catalog_fixture_decodes_to_exact_expected_text(self) -> None:
        for fixture in self.catalog["payloads"]:
            with self.subTest(fixture=fixture["id"]):
                result = self._generate_fixture(fixture)
                self.assertEqual(decode_svg(result.svg), fixture["expected"])

    def test_all_six_payload_types_decode_at_all_requested_levels(self) -> None:
        representative: dict[str, dict[str, object]] = {}
        for fixture in self.catalog["payloads"]:
            representative.setdefault(fixture["payloadType"], fixture)
        self.assertEqual(set(representative), {"text", "url", "email", "phone", "wifi", "sms"})

        for payload_type, fixture in representative.items():
            for level in "LMQH":
                with self.subTest(payload_type=payload_type, level=level):
                    result = self._generate_fixture(fixture, level)
                    self.assertEqual(result.requested_error_correction, level)
                    self.assertEqual(decode_svg(result.svg), fixture["expected"])

    def test_capacity_boundaries_decode_at_the_exact_declared_limit(self) -> None:
        for boundary in self.catalog["capacityBoundaries"]:
            level = boundary["errorCorrection"]
            payload = boundary["value"] * boundary["atLimit"]
            with self.subTest(level=level):
                result = generate(
                    GenerationRequest(
                        "text", {"text": payload}, requested_error_correction=level
                    )
                )
                self.assertEqual(result.version, 40)
                self.assertEqual(decode_svg(result.svg), payload)

    def test_version_32_alignment_pattern_output_decodes(self) -> None:
        payload = "a" * 1850
        result = generate(
            GenerationRequest("text", {"text": payload}, requested_error_correction="L")
        )
        self.assertEqual(result.version, 32)
        self.assertEqual(decode_svg(result.svg), payload)

    def test_evidence_matrix_for_contrast_polarity_and_quiet_zone(self) -> None:
        cases = [
            ({}, ()),
            ({"foreground": "#777777"}, ("low_contrast",)),
            (
                {"foreground": "#FFFFFF", "background": "#000000"},
                ("reversed_polarity",),
            ),
            ({"border": 2}, ("reduced_quiet_zone",)),
        ]
        fixture = self.catalog["payloads"][0]
        for overrides, expected_warning_codes in cases:
            with self.subTest(overrides=overrides):
                result = self._generate_fixture(fixture, **overrides)
                self.assertEqual(warning_codes(result.warnings), expected_warning_codes)
                self.assertEqual(decode_svg(result.svg), fixture["expected"])


if __name__ == "__main__":
    unittest.main()
