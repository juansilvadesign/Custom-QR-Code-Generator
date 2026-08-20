from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main
from qr_contract import GenerationRequest


class InteractiveCliTests(unittest.TestCase):
    def test_wifi_password_collection_uses_hidden_input(self) -> None:
        with patch(
            "builtins.input", side_effect=["Synthetic SSID", "WPA", "y"]
        ), patch.object(main, "getpass", return_value="hidden-password") as hidden:
            fields = main.get_content_fields("wifi")
        hidden.assert_called_once_with("Password (input hidden): ")
        self.assertEqual(fields["password"], "hidden-password")
        self.assertTrue(fields["hidden"])

    def test_sensitive_payload_is_absent_from_stdout_and_filename_by_default(self) -> None:
        secret = "terminal-secret-8cf31"
        answers = iter(
            [
                "1", secret, "2", "", "", "", "../../safe.name.svg",
                "n", "n", "n",
            ]
        )
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory, patch(
            "builtins.input", side_effect=lambda _prompt="": next(answers)
        ), redirect_stdout(output):
            status = main.run_interactive(directory)

            files = list(Path(directory).glob("*.svg"))
            self.assertEqual(status, 0)
            self.assertEqual([path.name for path in files], ["safe.name.svg"])
            self.assertNotIn(secret, output.getvalue())
            self.assertNotIn(secret, files[0].name)
            self.assertNotIn(secret, files[0].read_text(encoding="utf-8"))

    def test_explicit_reveal_prints_the_exact_payload(self) -> None:
        secret = "explicit-secret-33a9"
        request = GenerationRequest("text", {"text": secret})
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory, patch.object(
            main, "collect_request", return_value=request
        ), patch("builtins.input", side_effect=["n", "y", "n"]), redirect_stdout(output):
            status = main.run_interactive(directory)
        self.assertEqual(status, 0)
        self.assertIn(f"Encoded payload: {secret}", output.getvalue())

    def test_wifi_password_stays_hidden_without_explicit_reveal(self) -> None:
        password = "wifi-terminal-private-a914"
        request = GenerationRequest(
            "wifi",
            {
                "ssid": "Synthetic SSID",
                "password": password,
                "security": "WPA",
                "hidden": False,
            },
            output_name="wifi-test",
        )
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory, patch.object(
            main, "collect_request", return_value=request
        ), patch("builtins.input", side_effect=["n", "n", "n"]), redirect_stdout(output):
            status = main.run_interactive(directory)
        self.assertEqual(status, 0)
        self.assertNotIn(password, output.getvalue())
        self.assertNotIn("Synthetic SSID", output.getvalue())

    def test_create_another_uses_an_iterative_loop(self) -> None:
        requests = [
            GenerationRequest("text", {"text": "first"}, output_name="first"),
            GenerationRequest("text", {"text": "second"}, output_name="second"),
        ]
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory, patch.object(
            main, "collect_request", side_effect=requests
        ) as collect, patch(
            "builtins.input", side_effect=["n", "n", "y", "n", "n", "n"]
        ), redirect_stdout(output):
            status = main.run_interactive(directory)
            self.assertEqual(status, 0)
            self.assertEqual(collect.call_count, 2)
            self.assertEqual(
                sorted(path.name for path in Path(directory).glob("*.svg")),
                ["first.svg", "second.svg"],
            )

    def test_filesystem_error_is_safe_and_does_not_print_raw_exception(self) -> None:
        request = GenerationRequest("text", {"text": "private"})
        output = io.StringIO()
        with patch.object(main, "collect_request", return_value=request), patch.object(
            main, "save_svg_exclusive", side_effect=OSError("/secret/system/path")
        ), patch("builtins.input", side_effect=["n"]), redirect_stdout(output):
            status = main.run_interactive()
        self.assertEqual(status, 0)
        self.assertIn("filesystem_error", output.getvalue())
        self.assertNotIn("/secret/system/path", output.getvalue())

    def test_cancellation_has_a_specific_exit_status(self) -> None:
        output = io.StringIO()
        with patch.object(main, "run_interactive", side_effect=KeyboardInterrupt), redirect_stdout(output):
            self.assertEqual(main.main(), 130)
        self.assertIn("cancelled", output.getvalue())


if __name__ == "__main__":
    unittest.main()
