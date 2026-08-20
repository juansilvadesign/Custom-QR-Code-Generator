"""Canonical structured-payload builders for Custom QR Code Generator."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import quote, urlsplit

from qr_contract import (
    GenerationWarning,
    UnsupportedPayloadTypeError,
    ValidationError,
)


SUPPORTED_PAYLOAD_TYPES = ("text", "url", "email", "phone", "wifi", "sms")

_FIELD_SETS: dict[str, tuple[frozenset[str], frozenset[str]]] = {
    "text": (frozenset({"text"}), frozenset()),
    "url": (frozenset({"url"}), frozenset()),
    "email": (frozenset({"address"}), frozenset({"subject", "body"})),
    "phone": (frozenset({"phone"}), frozenset()),
    "wifi": (
        frozenset({"ssid", "security"}),
        frozenset({"password", "hidden"}),
    ),
    "sms": (frozenset({"phone"}), frozenset({"body"})),
}

_PHONE_FORMATTING_RE = re.compile(r"[\s().-]")
_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_HOST_PORT_RE = re.compile(r"^[^/?#:\s]+:\d+(?:[/?#]|$)")
_STRUCTURAL_CONTROL_RE = re.compile(r"[\x00-\x1F\x7F]")
_WIFI_ESCAPE_RE = re.compile(r'([\\;,:\"])')


@dataclass(frozen=True)
class BuiltPayload:
    text: str
    summary: str
    sensitive: bool
    warnings: tuple[GenerationWarning, ...] = ()


def _validate_fields(payload_type: str, fields: Mapping[str, object]) -> None:
    if not isinstance(fields, Mapping):
        raise ValidationError("invalid_fields", "Fields must be a JSON object.")
    if any(not isinstance(key, str) for key in fields):
        raise ValidationError(
            "invalid_payload_field_name", "Payload field names must be strings."
        )

    required, optional = _FIELD_SETS[payload_type]
    keys = set(fields)
    missing = sorted(required - keys)
    if missing:
        raise ValidationError(
            "missing_payload_field",
            f"Missing required field: {missing[0]}.",
        )

    unknown = sorted(keys - required - optional)
    if unknown:
        raise ValidationError(
            "unknown_payload_field",
            f"The {payload_type} payload contains an unknown field.",
        )


def _string_field(
    fields: Mapping[str, object],
    name: str,
    *,
    required: bool = True,
    preserve_empty: bool = False,
) -> str:
    value = fields.get(name, "")
    if not isinstance(value, str):
        raise ValidationError(
            "invalid_payload_field_type", f"Field '{name}' must be a string."
        )
    if required and not preserve_empty and not value:
        raise ValidationError(
            "empty_payload_field", f"Field '{name}' cannot be empty."
        )
    return value


def _reject_structural_controls(value: str, field_name: str) -> None:
    if _STRUCTURAL_CONTROL_RE.search(value):
        raise ValidationError(
            "invalid_control_character",
            f"Field '{field_name}' cannot contain control characters.",
        )


def _normalize_phone(value: str) -> str:
    phone = value.strip()
    _reject_structural_controls(phone, "phone")
    normalized = _PHONE_FORMATTING_RE.sub("", phone)
    if not re.fullmatch(r"\+?[0-9]+", normalized):
        raise ValidationError(
            "invalid_phone",
            "Phone numbers may contain one leading plus, digits, spaces, parentheses, dots, or hyphens.",
        )
    digit_count = len(normalized.lstrip("+"))
    if not 3 <= digit_count <= 15:
        raise ValidationError(
            "invalid_phone_length", "Phone numbers must contain 3 to 15 digits."
        )
    return normalized


def _build_text(fields: Mapping[str, object]) -> BuiltPayload:
    text = _string_field(fields, "text")
    return BuiltPayload(text, "Text payload (content hidden)", True)


def _build_url(fields: Mapping[str, object]) -> BuiltPayload:
    raw_url = _string_field(fields, "url").strip()
    if not raw_url:
        raise ValidationError("empty_payload_field", "Field 'url' cannot be empty.")
    _reject_structural_controls(raw_url, "url")
    if any(character.isspace() for character in raw_url):
        raise ValidationError(
            "invalid_url", "URLs cannot contain unescaped whitespace."
        )

    if raw_url.startswith("//"):
        normalized = "https:" + raw_url
    elif _HOST_PORT_RE.match(raw_url):
        normalized = "https://" + raw_url
    elif not _SCHEME_RE.match(raw_url):
        normalized = "https://" + raw_url
    else:
        normalized = raw_url

    try:
        parsed = urlsplit(normalized)
        scheme = parsed.scheme.lower()
        hostname = parsed.hostname
        parsed.port
    except (UnicodeError, ValueError) as exc:
        raise ValidationError("invalid_url", "The URL is malformed.") from exc
    if scheme not in {"http", "https"}:
        raise ValidationError(
            "unsupported_url_scheme", "Only http and https URLs are supported."
        )
    if not parsed.netloc or hostname is None:
        raise ValidationError("invalid_url", "The URL must include a host.")

    return BuiltPayload(normalized, "URL payload (destination hidden)", False)


def _build_email(fields: Mapping[str, object]) -> BuiltPayload:
    address = _string_field(fields, "address").strip()
    _reject_structural_controls(address, "address")
    if (
        address.count("@") != 1
        or any(character.isspace() for character in address)
        or any(not part for part in address.split("@", 1))
    ):
        raise ValidationError(
            "invalid_email", "Email must contain one address with a local part and domain."
        )

    subject = _string_field(fields, "subject", required=False, preserve_empty=True)
    body = _string_field(fields, "body", required=False, preserve_empty=True)
    query: list[str] = []
    if subject:
        query.append("subject=" + quote(subject, safe=""))
    if body:
        query.append("body=" + quote(body, safe=""))

    # Preserve URI-safe addr-spec characters and percent-encode delimiters such
    # as ?, #, %, &, =, and ; so they cannot become query/fragment syntax.
    recipient = quote(address, safe="@!$'()*+-._~")
    payload = "mailto:" + recipient
    if query:
        payload += "?" + "&".join(query)
    return BuiltPayload(payload, "Email payload (address and message hidden)", bool(query))


def _build_phone(fields: Mapping[str, object]) -> BuiltPayload:
    phone = _normalize_phone(_string_field(fields, "phone"))
    return BuiltPayload("tel:" + phone, "Phone payload (number hidden)", True)


def _escape_wifi(value: str) -> str:
    return _WIFI_ESCAPE_RE.sub(r"\\\1", value)


def _build_wifi(fields: Mapping[str, object]) -> BuiltPayload:
    ssid = _string_field(fields, "ssid")
    password = _string_field(
        fields, "password", required=False, preserve_empty=True
    )
    security_value = _string_field(fields, "security").strip().lower()
    security_map = {"wpa": "WPA", "wep": "WEP", "nopass": "nopass"}
    if security_value not in security_map:
        raise ValidationError(
            "invalid_wifi_security", "WiFi security must be WPA, WEP, or nopass."
        )
    security = security_map[security_value]

    hidden = fields.get("hidden", False)
    if not isinstance(hidden, bool):
        raise ValidationError(
            "invalid_payload_field_type", "Field 'hidden' must be a boolean."
        )
    _reject_structural_controls(ssid, "ssid")
    _reject_structural_controls(password, "password")

    warnings: list[GenerationWarning] = []
    if security in {"WPA", "WEP"} and not password:
        raise ValidationError(
            "missing_wifi_password",
            f"A password is required for {security} WiFi networks.",
        )
    if security == "nopass" and password:
        warnings.append(
            GenerationWarning(
                "ignored_wifi_password",
                "The password was omitted because nopass networks do not use credentials.",
            )
        )

    parts = [f"WIFI:T:{security}", f"S:{_escape_wifi(ssid)}"]
    if security != "nopass":
        parts.append(f"P:{_escape_wifi(password)}")
    parts.append(f"H:{'true' if hidden else 'false'}")
    payload = ";".join(parts) + ";;"
    return BuiltPayload(
        payload,
        "WiFi payload (network name and credentials hidden)",
        True,
        tuple(warnings),
    )


def _build_sms(fields: Mapping[str, object]) -> BuiltPayload:
    phone = _normalize_phone(_string_field(fields, "phone"))
    body = _string_field(fields, "body", required=False, preserve_empty=True)
    payload = "sms:" + phone
    if body:
        payload += "?body=" + quote(body, safe="")
    return BuiltPayload(payload, "SMS payload (number and message hidden)", True)


_BUILDERS = {
    "text": _build_text,
    "url": _build_url,
    "email": _build_email,
    "phone": _build_phone,
    "wifi": _build_wifi,
    "sms": _build_sms,
}


def build_payload(payload_type: str, fields: Mapping[str, object]) -> BuiltPayload:
    """Build a payload without Unicode normalization or lossy text conversion."""

    if not isinstance(payload_type, str) or payload_type not in _BUILDERS:
        raise UnsupportedPayloadTypeError(
            "unsupported_payload_type",
            "Payload type must be one of: " + ", ".join(SUPPORTED_PAYLOAD_TYPES) + ".",
        )
    _validate_fields(payload_type, fields)
    try:
        return _BUILDERS[payload_type](fields)
    except UnicodeError as exc:
        raise ValidationError(
            "invalid_unicode",
            "Payload text must contain valid Unicode scalar values.",
        ) from exc
