#!/usr/bin/env python3
"""Interactive terminal adapter for the shared QR generation core."""

from __future__ import annotations

import re
import sys
from getpass import getpass
from pathlib import Path
from typing import Mapping

from qr_contract import GenerationRequest, GenerationResult, QrGenerationError
from qr_core import generate
from qr_files import save_svg_exclusive


COLOR_NAMES = {
    "black": "#000000",
    "white": "#FFFFFF",
    "red": "#FF0000",
    "green": "#00FF00",
    "blue": "#0000FF",
    "yellow": "#FFFF00",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "orange": "#FFA500",
    "purple": "#800080",
    "pink": "#FFC0CB",
    "brown": "#A52A2A",
    "gray": "#808080",
    "grey": "#808080",
    "navy": "#000080",
    "darkblue": "#00008B",
    "darkgreen": "#006400",
    "darkred": "#8B0000",
}
CONTENT_TYPES = {
    "1": "text",
    "2": "url",
    "3": "email",
    "4": "phone",
    "5": "wifi",
    "6": "sms",
}


def get_color_input(prompt: str, default_color: str) -> str:
    """Collect a friendly color and convert it to the strict core syntax."""

    print(f"\n{prompt}")
    print("Use #RRGGBB, RRGGBB, rgb(r,g,b), or a common color name.")
    print(f"Press Enter for {default_color}.")
    while True:
        color = input("Enter color: ").strip()
        if not color:
            return default_color.upper()
        if re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
            return color.upper()
        if re.fullmatch(r"[0-9A-Fa-f]{6}", color):
            return ("#" + color).upper()

        rgb_match = re.fullmatch(
            r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)",
            color,
            flags=re.IGNORECASE,
        )
        if rgb_match:
            channels = tuple(int(channel) for channel in rgb_match.groups())
            if all(0 <= channel <= 255 for channel in channels):
                return "#{:02X}{:02X}{:02X}".format(*channels)
            print("RGB values must be between 0 and 255.")
            continue

        named = COLOR_NAMES.get(color.lower())
        if named:
            return named
        print("Invalid color. Use a six-digit color or a listed color name.")


def get_error_correction_level() -> str:
    print("\nChoose error correction: 1 Low, 2 Medium, 3 Quartile, 4 High.")
    choices = {"1": "L", "2": "M", "3": "Q", "4": "H"}
    while True:
        choice = input("Choice (1-4) [2]: ").strip() or "2"
        if choice in choices:
            return choices[choice]
        print("Invalid choice. Enter 1, 2, 3, or 4.")


def get_content_type() -> str:
    print("\nWhat type of content do you want to encode?")
    print("1 Text  2 URL  3 Email  4 Phone  5 WiFi  6 SMS")
    while True:
        choice = input("Choice (1-6): ").strip()
        if choice in CONTENT_TYPES:
            return CONTENT_TYPES[choice]
        print("Invalid choice. Enter a number from 1 to 6.")


def get_content_fields(payload_type: str) -> Mapping[str, object]:
    if payload_type == "text":
        return {"text": input("Text: ")}
    if payload_type == "url":
        return {"url": input("URL (http/https may be omitted): ")}
    if payload_type == "email":
        return {
            "address": input("Email address: "),
            "subject": input("Subject (optional): "),
            "body": input("Body (optional): "),
        }
    if payload_type == "phone":
        return {"phone": input("Phone number: ")}
    if payload_type == "wifi":
        fields: dict[str, object] = {
            "ssid": input("Network name (SSID): "),
        }
        security = input("Security (WPA/WEP/nopass) [WPA]: ").strip() or "WPA"
        fields["security"] = security
        if security.lower() != "nopass":
            fields["password"] = getpass("Password (input hidden): ")
        hidden = input("Hidden network? (y/n) [n]: ").strip().lower()
        fields["hidden"] = hidden == "y"
        return fields
    if payload_type == "sms":
        return {
            "phone": input("Phone number: "),
            "body": input("Message (optional): "),
        }
    raise ValueError("Unsupported terminal payload type")


def get_border() -> int:
    while True:
        raw_value = input("\nBorder in modules (2-16) [4]: ").strip()
        if not raw_value:
            return 4
        try:
            border = int(raw_value)
        except ValueError:
            print("Border must be a whole number from 2 to 16.")
            continue
        if 2 <= border <= 16:
            return border
        print("Border must be between 2 and 16.")


def collect_request() -> GenerationRequest:
    payload_type = get_content_type()
    fields = get_content_fields(payload_type)
    error_correction = get_error_correction_level()
    background = get_color_input("Choose background color:", "#FFFFFF")
    foreground = get_color_input("Choose foreground module color:", "#000000")
    border = get_border()
    output_name = input("\nOutput filename [custom_qr.svg]: ").strip() or None
    return GenerationRequest(
        payload_type=payload_type,
        fields=fields,
        requested_error_correction=error_correction,
        foreground=foreground,
        background=background,
        border=border,
        output_name=output_name,
    )


def print_qr_terminal(
    matrix: tuple[tuple[bool, ...], ...], border: int = 2
) -> None:
    print("\nQR preview:")
    size = len(matrix)
    for y in range(-border, size + border):
        line = []
        for x in range(-border, size + border):
            dark = 0 <= x < size and 0 <= y < size and matrix[y][x]
            line.append("██" if dark else "  ")
        print("".join(line))
    print()


def _show_result(result: GenerationResult, path: Path) -> None:
    print("\nQR code created.")
    print(f"Summary: {result.summary}")
    print(
        "QR: version "
        f"{result.version}, {result.module_count} modules, mask {result.mask}, "
        f"ECL {result.requested_error_correction}→{result.actual_error_correction}"
    )
    print(
        f"Scanability guard: {result.scanability.status}; "
        f"contrast {result.scanability.contrast_ratio}:1; "
        f"recommended at least {result.scanability.recommended_minimum_pixels}px"
    )
    for warning in result.warnings:
        print(f"Warning [{warning.code}]: {warning.message}")
    print(f"Saved: {path}")


def run_interactive(output_directory: str | Path = "saved") -> int:
    print("=" * 60)
    print("Custom QR Code Generator")
    print("=" * 60)
    print("Payload content stays hidden unless you explicitly reveal it.")

    while True:
        try:
            request = collect_request()
            result = generate(request)
            path = save_svg_exclusive(
                result.svg, request.output_name, directory=output_directory
            )
        except QrGenerationError as error:
            print(f"\nError [{error.code}]: {error.message}")
        except OSError:
            print("\nError [filesystem_error]: The SVG could not be saved safely.")
        else:
            _show_result(result, path)
            if input("\nShow terminal preview? (y/n) [y]: ").strip().lower() != "n":
                print_qr_terminal(result.matrix)
            if result.sensitive:
                reveal = input(
                    "Reveal exact encoded payload? This may expose private content (y/n) [n]: "
                ).strip().lower()
                if reveal == "y":
                    print(f"Encoded payload: {result.encoded_payload}")

        if input("Create another QR code? (y/n) [n]: ").strip().lower() != "y":
            return 0
        print("\n" + "=" * 60)


def main() -> int:
    try:
        return run_interactive()
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.")
        return 130
    except Exception as error:  # Deliberately safe unexpected-error boundary.
        print(f"\nError [internal_error]: Unexpected {type(error).__name__}.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
