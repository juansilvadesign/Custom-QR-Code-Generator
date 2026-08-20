"""Validated, import-safe shared QR generation core."""

from __future__ import annotations

import re
from typing import Iterable

from qrcodegen import DataTooLongError, QrCode, QrSegment

from qr_contract import (
    CapacityError,
    GenerationRequest,
    GenerationResult,
    GenerationWarning,
    ScanabilityAssessment,
    ValidationError,
)
from qr_files import sanitize_filename
from qr_payloads import build_payload


DEFAULT_BORDER = 4
MIN_BORDER = 0
MAX_BORDER = 16
SAFE_BORDER = 4
MIN_ACCEPTED_BORDER = 2
MIN_CONTRAST = 3.0
RECOMMENDED_CONTRAST = 4.5
PIXELS_PER_MODULE_GUIDANCE = 8

# Conservative byte-mode maxima for a version-40 QR. Numeric/alphanumeric text
# could theoretically fit more characters, but a UTF-8 byte ceiling is stable
# across payload kinds and prevents input-dependent surprises.
MAX_PAYLOAD_BYTES = {"L": 2953, "M": 2331, "Q": 1663, "H": 1273}

_HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
_ECL_BY_CODE = {
    "L": QrCode.Ecc.LOW,
    "M": QrCode.Ecc.MEDIUM,
    "Q": QrCode.Ecc.QUARTILE,
    "H": QrCode.Ecc.HIGH,
}
_ECL_CODE_BY_ORDINAL = {
    QrCode.Ecc.LOW.ordinal: "L",
    QrCode.Ecc.MEDIUM.ordinal: "M",
    QrCode.Ecc.QUARTILE.ordinal: "Q",
    QrCode.Ecc.HIGH.ordinal: "H",
}


def _normalize_color(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not _HEX_COLOR_RE.fullmatch(value):
        raise ValidationError(
            "invalid_color",
            f"{field_name} must be a six-digit color in #RRGGBB format.",
        )
    return value.upper()


def _relative_luminance(color: str) -> float:
    channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]

    def linearize(channel: float) -> float:
        if channel <= 0.04045:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    red, green, blue = (linearize(channel) for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _assess_scanability(
    foreground: str,
    background: str,
    border: int,
    module_count: int,
) -> tuple[ScanabilityAssessment, tuple[GenerationWarning, ...]]:
    if isinstance(border, bool) or not isinstance(border, int):
        raise ValidationError("invalid_border", "Border must be an integer.")
    if not MIN_BORDER <= border <= MAX_BORDER:
        raise ValidationError(
            "invalid_border", f"Border must be between {MIN_BORDER} and {MAX_BORDER}."
        )
    if border < MIN_ACCEPTED_BORDER:
        raise ValidationError(
            "unsafe_border",
            f"A border of at least {MIN_ACCEPTED_BORDER} modules is required for scanability.",
        )

    foreground_luminance = _relative_luminance(foreground)
    background_luminance = _relative_luminance(background)
    lighter = max(foreground_luminance, background_luminance)
    darker = min(foreground_luminance, background_luminance)
    contrast_ratio = (lighter + 0.05) / (darker + 0.05)
    if contrast_ratio < MIN_CONTRAST:
        raise ValidationError(
            "unsafe_contrast",
            f"Foreground/background contrast must be at least {MIN_CONTRAST:.1f}:1.",
        )

    warnings: list[GenerationWarning] = []
    if border < SAFE_BORDER:
        warnings.append(
            GenerationWarning(
                "reduced_quiet_zone",
                "The quiet zone is below the four-module recommendation; test the final size and medium carefully.",
            )
        )
    if contrast_ratio < RECOMMENDED_CONTRAST:
        warnings.append(
            GenerationWarning(
                "low_contrast",
                "Contrast is below the 4.5:1 scanability recommendation; use darker modules or a lighter background.",
            )
        )

    polarity = "normal" if foreground_luminance < background_luminance else "reversed"
    if polarity == "reversed":
        warnings.append(
            GenerationWarning(
                "reversed_polarity",
                "Light modules on a dark background are not supported by every scanner; verify the final artifact.",
            )
        )

    dimension = module_count + border * 2
    assessment = ScanabilityAssessment(
        status="warning" if warnings else "pass",
        contrast_ratio=round(contrast_ratio, 2),
        polarity=polarity,
        recommended_minimum_pixels=dimension * PIXELS_PER_MODULE_GUIDANCE,
    )
    return assessment, tuple(warnings)


def render_svg(
    matrix: tuple[tuple[bool, ...], ...],
    border: int,
    background: str,
    foreground: str,
) -> str:
    """Render a deterministic minimal SVG from a validated module matrix."""

    size = len(matrix)
    dimension = size + border * 2
    path = " ".join(
        f"M{x + border},{y + border}h1v1h-1z"
        for y, row in enumerate(matrix)
        for x, dark in enumerate(row)
        if dark
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {dimension} {dimension}" '
        'shape-rendering="crispEdges">\n'
        f'  <rect width="100%" height="100%" fill="{background}"/>\n'
        f'  <path fill="{foreground}" d="{path}"/>\n'
        "</svg>\n"
    )


def _matrix_from_qr(qr: QrCode) -> tuple[tuple[bool, ...], ...]:
    return tuple(
        tuple(qr.get_module(x, y) for x in range(qr.get_size()))
        for y in range(qr.get_size())
    )


def _validate_error_correction(value: object) -> str:
    if not isinstance(value, str) or value not in _ECL_BY_CODE:
        raise ValidationError(
            "invalid_error_correction",
            "Error correction must be one of L, M, Q, or H.",
        )
    return value


def _encoded_utf8(payload: str) -> bytes:
    try:
        return payload.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValidationError(
            "invalid_unicode",
            "Payload text must contain valid Unicode scalar values.",
        ) from exc


def generate(request: GenerationRequest) -> GenerationResult:
    """Validate, build, encode, assess, and render one canonical request."""

    if not isinstance(request, GenerationRequest):
        raise TypeError("generate() requires a GenerationRequest")

    try:
        built = build_payload(request.payload_type, request.fields)
    except UnicodeError as exc:
        raise ValidationError(
            "invalid_unicode",
            "Payload text must contain valid Unicode scalar values.",
        ) from exc
    requested_ecl = _validate_error_correction(request.requested_error_correction)
    foreground = _normalize_color(request.foreground, "Foreground")
    background = _normalize_color(request.background, "Background")
    output_filename = sanitize_filename(request.output_name)
    # Reject unsafe/invalid presentation choices before the comparatively costly
    # version/mask search. The final call below fills dimension guidance once the
    # actual module count is known.
    _assess_scanability(foreground, background, request.border, 0)
    payload_bytes = _encoded_utf8(built.text)

    maximum = MAX_PAYLOAD_BYTES[requested_ecl]
    if len(payload_bytes) > maximum:
        raise CapacityError(
            "payload_too_large",
            f"Payload exceeds the {maximum}-byte limit for error correction {requested_ecl}.",
        )

    segments = QrSegment.make_segments(built.text)
    try:
        # Boosting is intentional: Nayuki may raise the actual ECL without growing
        # the QR version. Both requested and actual values are returned.
        qr = QrCode.encode_segments(
            segments,
            _ECL_BY_CODE[requested_ecl],
            boostecl=True,
        )
    except DataTooLongError as exc:
        raise CapacityError(
            "encoder_capacity_exceeded",
            "The valid payload cannot fit in a version-40 QR at the requested error correction.",
        ) from exc

    matrix = _matrix_from_qr(qr)
    scanability, scan_warnings = _assess_scanability(
        foreground, background, request.border, qr.get_size()
    )
    warnings = tuple((*built.warnings, *scan_warnings))
    actual_ecl = _ECL_CODE_BY_ORDINAL[qr.get_error_correction_level().ordinal]
    svg = render_svg(matrix, request.border, background, foreground)

    return GenerationResult(
        payload_type=request.payload_type,
        encoded_payload=built.text,
        payload_bytes=len(payload_bytes),
        summary=f"{built.summary} • {len(payload_bytes)} UTF-8 bytes",
        sensitive=built.sensitive,
        svg=svg,
        matrix=matrix,
        version=qr.get_version(),
        module_count=qr.get_size(),
        mask=qr.get_mask(),
        requested_error_correction=requested_ecl,
        actual_error_correction=actual_ecl,
        foreground=foreground,
        background=background,
        border=request.border,
        output_filename=output_filename,
        scanability=scanability,
        warnings=warnings,
    )


def warning_codes(warnings: Iterable[GenerationWarning]) -> tuple[str, ...]:
    """Small adapter/test helper that avoids coupling callers to warning text."""

    return tuple(warning.code for warning in warnings)
