"""Plain-value request, result, warning, and error contracts for QR generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


class QrGenerationError(Exception):
    """A deterministic, payload-safe error suitable for an adapter to present."""

    http_status = 422

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ValidationError(QrGenerationError):
    """The request is structurally valid but contains an invalid value."""


class UnsupportedPayloadTypeError(QrGenerationError):
    """The requested structured payload type is not supported."""


class CapacityError(QrGenerationError):
    """The valid encoded payload cannot fit under the declared QR limits."""


@dataclass(frozen=True)
class GenerationWarning:
    """A stable warning code plus a public message that never contains payload data."""

    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class GenerationRequest:
    """Canonical framework-independent QR generation request."""

    payload_type: str
    fields: Mapping[str, object]
    requested_error_correction: str = "M"
    foreground: str = "#000000"
    background: str = "#FFFFFF"
    border: int = 4
    output_name: str | None = None


@dataclass(frozen=True)
class ScanabilityAssessment:
    """Evidence-based guardrail metadata, not a guarantee or accessibility score."""

    status: str
    contrast_ratio: float
    polarity: str
    recommended_minimum_pixels: int


@dataclass(frozen=True)
class GenerationResult:
    """Canonical result shared by terminal, Flask, and tests."""

    payload_type: str
    encoded_payload: str
    payload_bytes: int
    summary: str
    sensitive: bool
    svg: str
    matrix: tuple[tuple[bool, ...], ...]
    version: int
    module_count: int
    mask: int
    requested_error_correction: str
    actual_error_correction: str
    foreground: str
    background: str
    border: int
    output_filename: str
    scanability: ScanabilityAssessment
    warnings: tuple[GenerationWarning, ...] = field(default_factory=tuple)

    def to_public_dict(self) -> dict[str, object]:
        """Return the payload-safe API representation.

        The exact payload intentionally stays on the in-process result so parity
        and decode tests can compare it. It is not copied into the HTTP metadata.
        """

        return {
            "svg": self.svg,
            "summary": self.summary,
            "warnings": [warning.to_dict() for warning in self.warnings],
            "metadata": {
                "payloadType": self.payload_type,
                "payloadBytes": self.payload_bytes,
                "version": self.version,
                "moduleCount": self.module_count,
                "mask": self.mask,
                "requestedErrorCorrection": self.requested_error_correction,
                "actualErrorCorrection": self.actual_error_correction,
                "foreground": self.foreground,
                "background": self.background,
                "border": self.border,
                "contrastRatio": self.scanability.contrast_ratio,
                "polarity": self.scanability.polarity,
                "scanability": self.scanability.status,
                "recommendedMinimumPixels": (
                    self.scanability.recommended_minimum_pixels
                ),
                "fileName": self.output_filename,
            },
        }
