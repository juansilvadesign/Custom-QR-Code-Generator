"""Safe output-name and exclusive SVG file helpers."""

from __future__ import annotations

import os
import re
from pathlib import Path

from qr_contract import ValidationError


_INVALID_FILENAME_RE = re.compile(r'[<>:"/\\|?*\x00-\x1F\x7F]')
_WINDOWS_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}
_MAX_BASENAME_BYTES = 160


def _truncate_utf8(value: str, maximum_bytes: int) -> str:
    while len(value.encode("utf-8")) > maximum_bytes:
        value = value[:-1]
    return value


def sanitize_filename(requested_name: str | None) -> str:
    """Return a portable basename ending in exactly one enforced `.svg` suffix."""

    if requested_name is None:
        requested_name = "custom_qr"
    if not isinstance(requested_name, str):
        raise ValidationError(
            "invalid_output_name", "Output name must be a string when provided."
        )

    # Treat both slash families as separators on every operating system, then keep
    # only the final component. This is sanitization, never a filesystem lookup.
    basename = re.split(r"[/\\]", requested_name.strip())[-1]
    while basename.lower().endswith(".svg"):
        basename = basename[:-4]
    basename = _INVALID_FILENAME_RE.sub("_", basename)
    basename = re.sub(r"\s+", " ", basename).strip(" .")
    if basename.startswith("."):
        basename = "_" + basename.lstrip(".")
    if not basename:
        basename = "custom_qr"

    reserved_stem = basename.split(".", 1)[0].upper()
    if reserved_stem in _WINDOWS_RESERVED:
        basename = "_" + basename

    basename = _truncate_utf8(basename, _MAX_BASENAME_BYTES)
    if not basename:
        basename = "custom_qr"
    return basename + ".svg"


def _collision_name(filename: str, counter: int) -> str:
    if counter == 0:
        return filename
    return f"{filename[:-4]} ({counter}).svg"


def save_svg_exclusive(
    svg: str,
    requested_name: str | None,
    directory: str | os.PathLike[str] = "saved",
) -> Path:
    """Create a complete SVG with an atomic exclusive path allocation.

    `O_EXCL` makes collision selection race-safe and prevents overwriting an
    existing path. A failed write removes only the new incomplete file.
    """

    filename = sanitize_filename(requested_name)
    output_directory = Path(directory)
    output_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if output_directory.is_symlink():
        raise ValidationError(
            "unsafe_output_path", "The saved directory cannot be a symbolic link."
        )
    resolved_directory = output_directory.resolve()

    counter = 0
    while True:
        candidate = resolved_directory / _collision_name(filename, counter)
        if candidate.parent.resolve() != resolved_directory:
            raise ValidationError(
                "unsafe_output_path", "The output path must stay inside the saved directory."
            )
        try:
            descriptor = os.open(
                candidate,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
        except FileExistsError:
            counter += 1
            continue

        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as file:
                file.write(svg)
                file.flush()
                os.fsync(file.fileno())
        except BaseException:
            try:
                os.close(descriptor)
            except OSError:
                pass
            try:
                candidate.unlink()
            except OSError:
                pass
            raise
        return candidate
