from __future__ import annotations

import unittest

from qr_contract import QrGenerationError
from qr_payloads import build_payload
from tests.helpers import load_fixture_catalog


class PayloadFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_fixture_catalog()

    def test_catalog_declares_exact_unicode_and_utf8_comparison(self) -> None:
        self.assertIn("Exact Unicode", self.catalog["comparison"])
        self.assertIn("exact UTF-8", self.catalog["comparison"])

    def test_every_valid_fixture_builds_exact_expected_payload(self) -> None:
        for fixture in self.catalog["payloads"]:
            with self.subTest(fixture=fixture["id"]):
                result = build_payload(fixture["payloadType"], fixture["fields"])
                self.assertEqual(result.text, fixture["expected"])
                self.assertEqual(
                    result.text.encode("utf-8"), fixture["expected"].encode("utf-8")
                )
                self.assertEqual(
                    [warning.code for warning in result.warnings],
                    fixture.get("warningCodes", []),
                )

    def test_every_invalid_fixture_uses_its_stable_error_code(self) -> None:
        for fixture in self.catalog["invalid"]:
            with self.subTest(fixture=fixture["id"]):
                with self.assertRaises(QrGenerationError) as raised:
                    build_payload(fixture["payloadType"], fixture["fields"])
                self.assertEqual(raised.exception.code, fixture["errorCode"])

    def test_unknown_type_is_distinct_from_invalid_fields(self) -> None:
        with self.assertRaises(QrGenerationError) as raised:
            build_payload("vcard", {"name": "Ada"})
        self.assertEqual(raised.exception.code, "unsupported_payload_type")

    def test_missing_and_unknown_fields_are_rejected(self) -> None:
        cases = [
            ("text", {}, "missing_payload_field"),
            ("text", {"text": "ok", "extra": "no"}, "unknown_payload_field"),
            ("sms", {"phone": 55119999}, "invalid_payload_field_type"),
            (
                "wifi",
                {"ssid": "Guest", "security": "nopass", "hidden": "false"},
                "invalid_payload_field_type",
            ),
        ]
        for payload_type, fields, error_code in cases:
            with self.subTest(error_code=error_code):
                with self.assertRaises(QrGenerationError) as raised:
                    build_payload(payload_type, fields)
                self.assertEqual(raised.exception.code, error_code)
        with self.assertRaises(QrGenerationError) as raised:
            build_payload("text", {1: "not a valid JSON field name"})
        self.assertEqual(raised.exception.code, "invalid_payload_field_name")

    def test_url_only_normalizes_an_absent_http_scheme(self) -> None:
        self.assertEqual(
            build_payload("url", {"url": "//example.com/a"}).text,
            "https://example.com/a",
        )
        self.assertEqual(
            build_payload("url", {"url": "http://example.com/A?x=1"}).text,
            "http://example.com/A?x=1",
        )
        self.assertEqual(
            build_payload("url", {"url": "example.com:8443/A?x=1"}).text,
            "https://example.com:8443/A?x=1",
        )
        for value, error_code in [
            ("https://example.com/a path", "invalid_url"),
            ("https:///missing-host", "invalid_url"),
            ("https://example.com:bad", "invalid_url"),
            ("https://[invalid", "invalid_url"),
        ]:
            with self.subTest(value=value):
                with self.assertRaises(QrGenerationError) as raised:
                    build_payload("url", {"url": value})
                self.assertEqual(raised.exception.code, error_code)

    def test_optional_email_and_sms_fields_are_omitted_when_empty(self) -> None:
        self.assertEqual(
            build_payload(
                "email", {"address": "user@example.com", "subject": "", "body": ""}
            ).text,
            "mailto:user@example.com",
        )
        self.assertEqual(
            build_payload("sms", {"phone": "+1 202 555 0100", "body": ""}).text,
            "sms:+12025550100",
        )
        self.assertEqual(
            build_payload("email", {"address": "user?tag@example.com"}).text,
            "mailto:user%3Ftag@example.com",
        )

    def test_structured_percent_encoding_rejects_invalid_unicode_safely(self) -> None:
        with self.assertRaises(QrGenerationError) as raised:
            build_payload(
                "email",
                {"address": "user@example.com", "body": "bad\ud800value"},
            )
        self.assertEqual(raised.exception.code, "invalid_unicode")


if __name__ == "__main__":
    unittest.main()
