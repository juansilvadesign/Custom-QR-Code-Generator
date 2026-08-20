from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from qr_contract import ValidationError
from qr_files import sanitize_filename, save_svg_exclusive


class SafeOutputTests(unittest.TestCase):
    def test_filename_sanitization_preserves_meaningful_dots_and_forces_svg(self) -> None:
        cases = {
            None: "custom_qr.svg",
            "": "custom_qr.svg",
            "report.v1.svg": "report.v1.svg",
            "archive.tar.gz": "archive.tar.gz.svg",
            "../../outside.svg": "outside.svg",
            r"C:\\temp\\outside.svg": "outside.svg",
            ".env": "env.svg",
            "name...": "name.svg",
            "CON.txt": "_CON.txt.svg",
            "a:b?c*d.svg": "a_b_c_d.svg",
        }
        for requested, expected in cases.items():
            with self.subTest(requested=requested):
                self.assertEqual(sanitize_filename(requested), expected)

    def test_repeated_svg_extensions_do_not_gain_another_suffix(self) -> None:
        self.assertEqual(sanitize_filename("name.svg.svg"), "name.svg")

    def test_unicode_names_are_bounded_by_encoded_bytes(self) -> None:
        filename = sanitize_filename("界" * 200)
        self.assertTrue(filename.endswith(".svg"))
        self.assertLessEqual(len(filename[:-4].encode("utf-8")), 160)

    def test_exclusive_creation_handles_collisions_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = save_svg_exclusive("first", "release.v1", directory)
            second = save_svg_exclusive("second", "release.v1.svg", directory)
            self.assertEqual(first.name, "release.v1.svg")
            self.assertEqual(second.name, "release.v1 (1).svg")
            self.assertEqual(first.read_text(encoding="utf-8"), "first")
            self.assertEqual(second.read_text(encoding="utf-8"), "second")

    def test_traversal_and_absolute_names_stay_inside_resolved_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            output = root / "saved"
            for requested in ("../../../escape", "/tmp/escape", r"..\\..\\escape"):
                with self.subTest(requested=requested):
                    path = save_svg_exclusive("safe", requested, output)
                    self.assertEqual(path.parent, output.resolve())
                    self.assertTrue(path.name.startswith("escape"))
            self.assertFalse((root / "escape.svg").exists())

    def test_filesystem_errors_propagate_to_the_adapter_without_fallback_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch(
            "qr_files.os.open", side_effect=PermissionError("private path")
        ):
            with self.assertRaises(PermissionError):
                save_svg_exclusive("svg", "file", directory)

    @unittest.skipIf(os.name == "nt", "Symlink privileges vary on Windows")
    def test_output_directory_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            real_directory = root / "real"
            real_directory.mkdir()
            linked_directory = root / "saved"
            linked_directory.symlink_to(real_directory, target_is_directory=True)
            with self.assertRaises(ValidationError) as raised:
                save_svg_exclusive("svg", "file", linked_directory)
            self.assertEqual(raised.exception.code, "unsafe_output_path")
            self.assertEqual(list(real_directory.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
