from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import app as web_app
import main
from qr_contract import GenerationRequest
from qr_core import generate
from tests.helpers import decode_svg, svg_module_coordinates


class SurfaceParityTests(unittest.TestCase):
    def test_cli_and_web_use_exact_core_payload_svg_and_metadata_semantics(self) -> None:
        request = GenerationRequest(
            payload_type="url",
            fields={"url": "example.com/a?x=1&y=%25"},
            requested_error_correction="Q",
            foreground="#112233",
            background="#FFFFFF",
            border=4,
            output_name="parity.v1.svg",
        )
        expected = generate(request)

        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory, patch.object(
            main, "collect_request", return_value=request
        ), patch("builtins.input", side_effect=["n", "n"]), redirect_stdout(output):
            self.assertEqual(main.run_interactive(directory), 0)
            cli_svg = (Path(directory) / "parity.v1.svg").read_text(encoding="utf-8")

        web_app.app.config.update(TESTING=True)
        response = web_app.app.test_client().post(
            "/api/generate",
            json={
                "payloadType": request.payload_type,
                "fields": request.fields,
                "errorCorrection": request.requested_error_correction,
                "foreground": request.foreground,
                "background": request.background,
                "border": request.border,
                "outputName": request.output_name,
            },
        )
        self.assertEqual(response.status_code, 200)
        web = response.get_json()

        self.assertEqual(cli_svg, expected.svg)
        self.assertEqual(web["svg"], expected.svg)
        expected_coordinates = {
            (x + expected.border, y + expected.border)
            for y, row in enumerate(expected.matrix)
            for x, dark in enumerate(row)
            if dark
        }
        self.assertEqual(svg_module_coordinates(cli_svg), expected_coordinates)
        self.assertEqual(svg_module_coordinates(web["svg"]), expected_coordinates)
        self.assertEqual(decode_svg(cli_svg), expected.encoded_payload)
        self.assertEqual(decode_svg(web["svg"]), expected.encoded_payload)
        self.assertEqual(web["metadata"], expected.to_public_dict()["metadata"])
        self.assertEqual(web["warnings"], expected.to_public_dict()["warnings"])


if __name__ == "__main__":
    unittest.main()
