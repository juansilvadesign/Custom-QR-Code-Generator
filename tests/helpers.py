"""Release-test helpers that stay independent from the production renderer."""

from __future__ import annotations

import json
import re
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "payloads.json"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
MODULE_COMMAND_RE = re.compile(r"M(\d+),(\d+)h1v1h-1z")


def load_fixture_catalog() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def parse_svg(svg: str) -> tuple[ElementTree.Element, ElementTree.Element, ElementTree.Element]:
    root = ElementTree.fromstring(svg)
    rectangle = root.find(f"{{{SVG_NAMESPACE}}}rect")
    path = root.find(f"{{{SVG_NAMESPACE}}}path")
    if rectangle is None or path is None:
        raise AssertionError("SVG must contain one background rectangle and module path")
    return root, rectangle, path


def svg_module_coordinates(svg: str) -> set[tuple[int, int]]:
    _root, _rectangle, path = parse_svg(svg)
    commands = path.attrib.get("d", "")
    matches = MODULE_COMMAND_RE.findall(commands)
    rebuilt = " ".join(f"M{x},{y}h1v1h-1z" for x, y in matches)
    if rebuilt != commands:
        raise AssertionError("SVG path contains an unexpected command")
    return {(int(x), int(y)) for x, y in matches}


def rasterize_svg_modules(svg: str, scale: int = 8):
    """Rasterize the emitted SVG geometry for an independent decoder.

    This parser reads the serialized SVG rather than the production QR matrix, so
    missing/moved SVG modules remain observable to ZXing. Pillow is imported here
    to keep it a development-only dependency.
    """

    from PIL import Image, ImageColor, ImageDraw

    root, rectangle, path = parse_svg(svg)
    view_box = [int(value) for value in root.attrib["viewBox"].split()]
    if view_box[:2] != [0, 0] or view_box[2] != view_box[3]:
        raise AssertionError("Expected a square zero-origin viewBox")
    dimension = view_box[2]
    background = ImageColor.getrgb(rectangle.attrib["fill"])
    foreground = ImageColor.getrgb(path.attrib["fill"])
    image = Image.new("RGB", (dimension * scale, dimension * scale), background)
    draw = ImageDraw.Draw(image)
    for x, y in svg_module_coordinates(svg):
        draw.rectangle(
            (x * scale, y * scale, (x + 1) * scale - 1, (y + 1) * scale - 1),
            fill=foreground,
        )
    return image


def decode_svg(svg: str) -> str:
    import zxingcpp

    barcode = zxingcpp.read_barcode(rasterize_svg_modules(svg))
    if barcode is None:
        raise AssertionError("ZXing-C++ could not decode generated SVG geometry")
    return barcode.text
