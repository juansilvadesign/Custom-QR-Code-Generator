from __future__ import annotations

import unittest
from unittest.mock import patch

from qrcodegen import DataTooLongError
from qr_contract import CapacityError, GenerationRequest, QrGenerationError
from qr_core import MAX_PAYLOAD_BYTES, generate, warning_codes
from tests.helpers import load_fixture_catalog


def text_request(text: str = "hello", **overrides: object) -> GenerationRequest:
    values: dict[str, object] = {
        "payload_type": "text",
        "fields": {"text": text},
        "requested_error_correction": "M",
        "foreground": "#000000",
        "background": "#FFFFFF",
        "border": 4,
        "output_name": None,
    }
    values.update(overrides)
    return GenerationRequest(**values)


class SharedCoreTests(unittest.TestCase):
    def test_result_exposes_encoder_and_scanability_metadata(self) -> None:
        result = generate(text_request("Hello, 世界", output_name="release.v1.svg"))
        self.assertEqual(result.encoded_payload, "Hello, 世界")
        self.assertEqual(result.payload_bytes, len("Hello, 世界".encode("utf-8")))
        self.assertEqual(result.module_count, result.version * 4 + 17)
        self.assertIn(result.mask, range(8))
        self.assertEqual(result.output_filename, "release.v1.svg")
        self.assertEqual(result.scanability.status, "pass")
        self.assertEqual(result.scanability.polarity, "normal")
        self.assertEqual(result.scanability.contrast_ratio, 21.0)
        self.assertEqual(len(result.matrix), result.module_count)
        self.assertTrue(all(len(row) == result.module_count for row in result.matrix))

    def test_encoder_boost_is_intentional_and_visible(self) -> None:
        result = generate(
            text_request("boost me", requested_error_correction="L")
        )
        self.assertEqual(result.requested_error_correction, "L")
        self.assertIn(result.actual_error_correction, ("M", "Q", "H"))

    def test_public_result_omits_exact_payload_and_sensitive_flag(self) -> None:
        secret = "private-message-4d9037"
        result = generate(text_request(secret))
        public = result.to_public_dict()
        self.assertNotIn(secret, repr(public))
        self.assertNotIn("encodedPayload", public)
        self.assertNotIn("sensitive", public)

    def test_svg_is_deterministic_for_the_same_request(self) -> None:
        request = text_request("same request")
        first = generate(request)
        second = generate(request)
        self.assertEqual(first.svg, second.svg)
        self.assertEqual(first.matrix, second.matrix)
        self.assertEqual(first.mask, second.mask)

    def test_invalid_error_correction_and_colors_are_stable_errors(self) -> None:
        cases = [
            ({"requested_error_correction": "Z"}, "invalid_error_correction"),
            ({"requested_error_correction": "m"}, "invalid_error_correction"),
            ({"foreground": "black"}, "invalid_color"),
            ({"foreground": "#000"}, "invalid_color"),
            ({"background": "#GGGGGG"}, "invalid_color"),
            ({"foreground": 0}, "invalid_color"),
        ]
        for overrides, code in cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(QrGenerationError) as raised:
                    generate(text_request(**overrides))
                self.assertEqual(raised.exception.code, code)

    def test_border_policy_rejects_unsafe_and_warns_reduced_values(self) -> None:
        for border in (0, 1):
            with self.subTest(border=border):
                with self.assertRaises(QrGenerationError) as raised:
                    generate(text_request(border=border))
                self.assertEqual(raised.exception.code, "unsafe_border")

        for border in (2, 3):
            with self.subTest(border=border):
                result = generate(text_request(border=border))
                self.assertIn("reduced_quiet_zone", warning_codes(result.warnings))
                self.assertEqual(result.scanability.status, "warning")

        for border in (-1, 17, 4.5, True):
            with self.subTest(border=border):
                with self.assertRaises(QrGenerationError) as raised:
                    generate(text_request(border=border))
                self.assertEqual(raised.exception.code, "invalid_border")

    def test_contrast_policy_rejects_or_warns_without_claiming_accessibility(self) -> None:
        with self.assertRaises(QrGenerationError) as raised:
            generate(text_request(foreground="#AAAAAA"))
        self.assertEqual(raised.exception.code, "unsafe_contrast")

        low_contrast = generate(text_request(foreground="#777777"))
        self.assertIn("low_contrast", warning_codes(low_contrast.warnings))
        self.assertEqual(low_contrast.scanability.status, "warning")

        reversed_result = generate(
            text_request(foreground="#FFFFFF", background="#000000")
        )
        self.assertIn("reversed_polarity", warning_codes(reversed_result.warnings))
        self.assertEqual(reversed_result.scanability.polarity, "reversed")

    def test_byte_limits_are_declared_per_requested_error_level(self) -> None:
        catalog = load_fixture_catalog()
        self.assertEqual(
            MAX_PAYLOAD_BYTES,
            {
                item["errorCorrection"]: item["atLimit"]
                for item in catalog["capacityBoundaries"]
            },
        )
        for boundary in catalog["capacityBoundaries"]:
            level = boundary["errorCorrection"]
            with self.subTest(level=level):
                at_limit = boundary["value"] * boundary["atLimit"]
                result = generate(
                    text_request(at_limit, requested_error_correction=level)
                )
                self.assertEqual(result.payload_bytes, boundary["atLimit"])
                self.assertEqual(result.version, 40)

                over_limit = boundary["value"] * boundary["overLimit"]
                with self.assertRaises(CapacityError) as raised:
                    generate(
                        text_request(over_limit, requested_error_correction=level)
                    )
                self.assertEqual(raised.exception.code, "payload_too_large")

    def test_encoder_capacity_failure_has_a_safe_distinct_code(self) -> None:
        with patch(
            "qr_core.QrCode.encode_segments",
            side_effect=DataTooLongError("raw encoder detail with private data"),
        ), self.assertRaises(CapacityError) as raised:
            generate(text_request("valid request"))
        self.assertEqual(raised.exception.code, "encoder_capacity_exceeded")
        self.assertNotIn("private data", raised.exception.message)

    def test_unpaired_surrogate_is_rejected_without_normalization(self) -> None:
        requests = [
            text_request("bad\ud800value"),
            GenerationRequest(
                "email",
                {"address": "test@example.com", "subject": "bad\ud800value"},
            ),
            GenerationRequest(
                "sms", {"phone": "+12025550100", "body": "bad\ud800value"}
            ),
        ]
        for request in requests:
            with self.subTest(payload_type=request.payload_type):
                with self.assertRaises(QrGenerationError) as raised:
                    generate(request)
                self.assertEqual(raised.exception.code, "invalid_unicode")


if __name__ == "__main__":
    unittest.main()
