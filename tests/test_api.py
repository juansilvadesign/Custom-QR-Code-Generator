from __future__ import annotations

import json
import unittest
from unittest.mock import patch

import app as web_app


def valid_request(content: str = "Hello, API") -> dict[str, object]:
    return {
        "payloadType": "text",
        "fields": {"text": content},
        "errorCorrection": "M",
        "foreground": "#000000",
        "background": "#FFFFFF",
        "border": 4,
        "outputName": "api.qr.svg",
    }


class GenerateApiTests(unittest.TestCase):
    def setUp(self) -> None:
        web_app.app.config.update(TESTING=True)
        self.client = web_app.app.test_client()

    def assert_error(
        self, response, status: int, code: str
    ) -> dict[str, object]:
        self.assertEqual(response.status_code, status)
        data = response.get_json()
        self.assertEqual(data["error"]["code"], code)
        self.assertIsInstance(data["error"]["message"], str)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        return data

    def test_success_returns_svg_redacted_summary_metadata_and_warnings(self) -> None:
        secret = "api-private-793ad1"
        response = self.client.post("/api/generate", json=valid_request(secret))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(set(data), {"svg", "summary", "metadata", "warnings"})
        self.assertNotIn(secret, response.get_data(as_text=True))
        self.assertEqual(data["metadata"]["payloadType"], "text")
        self.assertEqual(data["metadata"]["fileName"], "api.qr.svg")
        self.assertIn(data["metadata"]["actualErrorCorrection"], "LMQH")
        self.assertEqual(data["metadata"]["scanability"], "pass")
        self.assertTrue(data["svg"].startswith("<?xml"))
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertNotIn("Access-Control-Allow-Origin", response.headers)

    def test_wifi_credentials_are_absent_from_http_body_and_success_logs(self) -> None:
        password = "wifi-private-b1dd5"
        request_data = {
            "payloadType": "wifi",
            "fields": {
                "ssid": "Synthetic network",
                "password": password,
                "security": "WPA",
                "hidden": True,
            },
        }
        with self.assertNoLogs(web_app.app.logger, level="INFO"):
            response = self.client.post("/api/generate", json=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(password, response.get_data(as_text=True))
        self.assertNotIn("Synthetic network", response.get_data(as_text=True))

    def test_content_type_is_required_even_for_valid_json_bytes(self) -> None:
        body = json.dumps(valid_request()).encode()
        for content_type in (None, "text/plain", "application/x-www-form-urlencoded"):
            with self.subTest(content_type=content_type):
                response = self.client.post(
                    "/api/generate", data=body, content_type=content_type
                )
                self.assert_error(response, 415, "unsupported_media_type")

    def test_malformed_and_non_object_json_have_distinct_errors(self) -> None:
        malformed = self.client.post(
            "/api/generate", data=b'{"payloadType":', content_type="application/json"
        )
        self.assert_error(malformed, 400, "invalid_json")

        for value in ([], [valid_request()], "text", 42):
            with self.subTest(value=value):
                response = self.client.post("/api/generate", json=value)
                self.assert_error(response, 400, "invalid_request_shape")
        null_response = self.client.post(
            "/api/generate", data="null", content_type="application/json"
        )
        self.assert_error(null_response, 400, "invalid_request_shape")

    def test_missing_and_unknown_root_fields_are_rejected(self) -> None:
        missing = self.client.post(
            "/api/generate", json={"payloadType": "text"}
        )
        self.assert_error(missing, 400, "missing_request_field")

        secret_field_name = "secret-root-field-9f23"
        request_data = valid_request()
        request_data[secret_field_name] = True
        unknown = self.client.post("/api/generate", json=request_data)
        data = self.assert_error(unknown, 400, "unknown_request_field")
        self.assertNotIn(secret_field_name, repr(data))

    def test_nested_payload_fields_and_all_core_values_are_strict(self) -> None:
        cases = [
            ({"fields": {"text": "ok", "extra": "bad"}}, "unknown_payload_field"),
            ({"fields": []}, "invalid_fields"),
            ({"payloadType": "vcard"}, "unsupported_payload_type"),
            ({"errorCorrection": "medium"}, "invalid_error_correction"),
            ({"foreground": "black"}, "invalid_color"),
            ({"border": "4"}, "invalid_border"),
            ({"border": 0}, "unsafe_border"),
        ]
        for overrides, code in cases:
            with self.subTest(code=code):
                request_data = valid_request()
                request_data.update(overrides)
                response = self.client.post("/api/generate", json=request_data)
                self.assert_error(response, 422, code)

    def test_empty_and_capacity_failures_are_stable_client_errors(self) -> None:
        empty = self.client.post("/api/generate", json=valid_request(""))
        self.assert_error(empty, 422, "empty_payload_field")

        request_data = valid_request("a" * 1274)
        request_data["errorCorrection"] = "H"
        too_large = self.client.post("/api/generate", json=request_data)
        data = self.assert_error(too_large, 422, "payload_too_large")
        self.assertNotIn("a" * 20, repr(data))

    def test_request_body_limit_is_applied_before_json_parsing(self) -> None:
        oversized = b"{" + b"x" * web_app.MAX_REQUEST_BYTES + b"}"
        response = self.client.post(
            "/api/generate", data=oversized, content_type="application/json"
        )
        self.assert_error(response, 413, "request_too_large")

    def test_unexpected_errors_do_not_leak_exception_or_payload_to_body_or_logs(self) -> None:
        secret = "do-not-log-f7ae"
        with patch.object(
            web_app, "generate", side_effect=RuntimeError(secret)
        ), self.assertLogs(web_app.app.logger, level="ERROR") as captured:
            response = self.client.post("/api/generate", json=valid_request(secret))
        data = self.assert_error(response, 500, "internal_error")
        combined = response.get_data(as_text=True) + repr(data) + "\n".join(captured.output)
        self.assertNotIn(secret, combined)
        self.assertNotIn("Traceback", combined)
        self.assertIn("RuntimeError", combined)


if __name__ == "__main__":
    unittest.main()
