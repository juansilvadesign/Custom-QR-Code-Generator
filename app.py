"""Flask adapter for the shared QR generation core."""

from __future__ import annotations

import os
from typing import Any

from flask import Flask, Response, jsonify, render_template, request
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge

from qr_contract import GenerationRequest, QrGenerationError
from qr_core import generate


MAX_REQUEST_BYTES = 16_384
API_FIELDS = frozenset(
    {
        "payloadType",
        "fields",
        "errorCorrection",
        "foreground",
        "background",
        "border",
        "outputName",
    }
)
REQUIRED_API_FIELDS = frozenset({"payloadType", "fields"})

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BYTES


class ApiContractError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _error_response(code: str, message: str, status: int) -> tuple[Response, int]:
    return jsonify({"error": {"code": code, "message": message}}), status


def _parse_api_request(data: dict[str, Any]) -> GenerationRequest:
    unknown = sorted(set(data) - API_FIELDS)
    if unknown:
        raise ApiContractError(
            "unknown_request_field", "Request contains an unknown root field."
        )

    missing = sorted(REQUIRED_API_FIELDS - set(data))
    if missing:
        raise ApiContractError(
            "missing_request_field", f"Missing request field: {missing[0]}."
        )

    return GenerationRequest(
        payload_type=data["payloadType"],
        fields=data["fields"],
        requested_error_correction=data.get("errorCorrection", "M"),
        foreground=data.get("foreground", "#000000"),
        background=data.get("background", "#FFFFFF"),
        border=data.get("border", 4),
        output_name=data.get("outputName"),
    )


@app.after_request
def protect_api_response(response: Response) -> Response:
    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.errorhandler(RequestEntityTooLarge)
def request_too_large(_error: RequestEntityTooLarge) -> tuple[Response, int]:
    return _error_response(
        "request_too_large",
        f"JSON request bodies cannot exceed {MAX_REQUEST_BYTES} bytes.",
        413,
    )


@app.post("/api/generate")
def generate_qr() -> tuple[Response, int] | Response:
    if request.mimetype != "application/json":
        return _error_response(
            "unsupported_media_type",
            "Content-Type must be application/json.",
            415,
        )

    if request.content_length is not None and request.content_length > MAX_REQUEST_BYTES:
        return request_too_large(RequestEntityTooLarge())

    try:
        data = request.get_json(cache=False, silent=False)
    except BadRequest:
        return _error_response(
            "invalid_json", "Request body must contain valid JSON.", 400
        )

    if not isinstance(data, dict):
        return _error_response(
            "invalid_request_shape", "JSON request body must be an object.", 400
        )

    try:
        canonical_request = _parse_api_request(data)
        result = generate(canonical_request)
    except ApiContractError as error:
        return _error_response(error.code, error.message, 400)
    except QrGenerationError as error:
        return _error_response(error.code, error.message, error.http_status)
    except Exception as error:  # Deliberately safe unexpected-error boundary.
        app.logger.error(
            "Unexpected QR generation failure (type=%s)", type(error).__name__
        )
        return _error_response(
            "internal_error", "QR generation failed unexpectedly.", 500
        )

    return jsonify(result.to_public_dict())


@app.get("/")
def index() -> str:
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
