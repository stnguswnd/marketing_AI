from __future__ import annotations

import base64
import json
import mimetypes
from dataclasses import dataclass
from typing import Any
from urllib import error, request
from uuid import uuid4

from app.core.errors import AppError
from app.core.settings import get_settings


@dataclass(frozen=True)
class NanoBananaHttpRequest:
    url: str
    headers: dict[str, str]
    body: dict[str, Any]
    timeout_seconds: float


class NanoBananaAdapter:
    provider_name = "nano_banana"

    def create_variant(
        self,
        *,
        api_key: str,
        source_asset_ids: list[str],
        source_images: list[dict[str, str]],
        card_request: dict[str, object],
    ) -> dict[str, object]:
        settings = get_settings()
        if settings.app_env == "test":
            return self._mock_response(source_asset_ids=source_asset_ids, card_request=card_request)

        http_request = self._build_http_request(
            api_key=api_key,
            source_asset_ids=source_asset_ids,
            source_images=source_images,
            card_request=card_request,
        )
        try:
            response_body = self._send_request(http_request)
        except AppError as exc:
            # Some uploaded inputs can be rejected by Gemini image editing.
            # Fall back to text-only generation so draft creation does not fail hard.
            if source_images and exc.error_code == "NANO_BANANA_HTTP_ERROR" and "Unable to process input image" in exc.message:
                fallback_request = self._build_http_request(
                    api_key=api_key,
                    source_asset_ids=source_asset_ids,
                    source_images=[],
                    card_request=card_request,
                )
                response_body = self._send_request(fallback_request)
                http_request = fallback_request
            else:
                raise
        outputs = self._normalize_outputs(response_body, expected_count=int(card_request.get("variant_count", 1) or 1))
        return {
            "provider": self.provider_name,
            "variant_asset_ids": [item["asset_id"] for item in outputs],
            "outputs": outputs,
            "request_payload": http_request.body,
            "api_key_present": bool(api_key),
            "raw_response": response_body,
        }

    def _build_http_request(
        self,
        *,
        api_key: str,
        source_asset_ids: list[str],
        source_images: list[dict[str, str]],
        card_request: dict[str, object],
    ) -> NanoBananaHttpRequest:
        settings = get_settings()
        parts: list[dict[str, Any]] = [{"text": card_request.get("prompt", "")}]
        for image in source_images:
            mime_type = image.get("mime_type", "").strip()
            data = image.get("data", "").strip()
            if not mime_type or not data:
                continue
            parts.append(
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": data,
                    }
                }
            )
        body = {
            "contents": [
                {
                    "parts": parts,
                }
            ],
            "generationConfig": {
                "responseModalities": ["Image"],
                "imageConfig": {
                    "aspectRatio": str(card_request.get("card_spec", {}).get("aspect_ratio", "1:1")),
                },
            },
        }
        return NanoBananaHttpRequest(
            url=f"{settings.nano_banana_api_base_url.rstrip('/')}/models/{settings.nano_banana_model}:generateContent",
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body=body,
            timeout_seconds=settings.nano_banana_timeout_ms / 1000,
        )

    def _send_request(self, http_request: NanoBananaHttpRequest) -> dict[str, Any]:
        payload = json.dumps(http_request.body).encode("utf-8")
        req = request.Request(
            http_request.url,
            data=payload,
            headers=http_request.headers,
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=http_request.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            raw_body = exc.read().decode("utf-8", errors="replace")
            raise AppError(
                status_code=502,
                error_code="NANO_BANANA_HTTP_ERROR",
                message=f"Nano Banana API HTTP error: {exc.code}. {raw_body[:200]}",
            ) from exc
        except error.URLError as exc:
            raise AppError(
                status_code=502,
                error_code="NANO_BANANA_CONNECTION_ERROR",
                message=f"Nano Banana API connection error: {exc.reason}",
            ) from exc
        except TimeoutError as exc:
            raise AppError(
                status_code=504,
                error_code="NANO_BANANA_TIMEOUT",
                message="Nano Banana API request timed out.",
            ) from exc

        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise AppError(
                status_code=502,
                error_code="NANO_BANANA_INVALID_RESPONSE",
                message="Nano Banana API returned invalid JSON.",
            ) from exc

        if not isinstance(body, dict):
            raise AppError(
                status_code=502,
                error_code="NANO_BANANA_INVALID_RESPONSE",
                message="Nano Banana API returned an unexpected payload.",
            )
        return body

    def _normalize_outputs(self, response_body: dict[str, Any], expected_count: int) -> list[dict[str, Any]]:
        candidates = response_body.get("candidates")
        if isinstance(candidates, list):
            normalized_outputs: list[dict[str, Any]] = []
            for candidate in candidates:
                if not isinstance(candidate, dict):
                    continue
                content = candidate.get("content")
                if not isinstance(content, dict):
                    continue
                parts = content.get("parts")
                if not isinstance(parts, list):
                    continue
                for part in parts:
                    if not isinstance(part, dict):
                        continue
                    inline_data = part.get("inline_data") or part.get("inlineData")
                    if not isinstance(inline_data, dict):
                        continue
                    data = inline_data.get("data")
                    mime_type = str(inline_data.get("mime_type") or inline_data.get("mimeType") or "image/png")
                    if not isinstance(data, str) or not data.strip():
                        continue
                    asset_id = f"variant_{uuid4().hex[:8]}"
                    extension = mimetypes.guess_extension(mime_type) or ".png"
                    normalized_outputs.append(
                        {
                            "asset_id": asset_id,
                            "filename": f"{asset_id}{extension}",
                            "content_type": mime_type,
                            "binary_bytes": base64.b64decode(data),
                            "remote_url": None,
                        }
                    )
            if normalized_outputs:
                return normalized_outputs

        outputs = response_body.get("outputs")
        if isinstance(outputs, list):
            normalized_outputs: list[dict[str, Any]] = []
            for item in outputs:
                if not isinstance(item, dict):
                    continue
                asset_id = self._resolve_asset_id(item)
                filename = self._resolve_filename(item, asset_id)
                content_type = self._resolve_content_type(item, filename)
                binary_bytes = self._resolve_binary_bytes(item)
                normalized_outputs.append(
                    {
                        "asset_id": asset_id,
                        "filename": filename,
                        "content_type": content_type,
                        "binary_bytes": binary_bytes,
                        "remote_url": item.get("image_url") or item.get("download_url") or item.get("url"),
                    }
                )
            if normalized_outputs:
                return normalized_outputs

        return [
            {
                "asset_id": f"variant_{uuid4().hex[:8]}",
                "filename": f"variant_{index + 1}.png",
                "content_type": "image/png",
                "binary_bytes": self._placeholder_png_bytes(),
                "remote_url": None,
            }
            for index in range(expected_count)
        ]

    def _resolve_asset_id(self, item: dict[str, Any]) -> str:
        asset_id = item.get("asset_id") or item.get("id")
        if isinstance(asset_id, str) and asset_id.strip():
            return asset_id.strip()
        return f"variant_{uuid4().hex[:8]}"

    def _resolve_filename(self, item: dict[str, Any], asset_id: str) -> str:
        filename = item.get("filename")
        if isinstance(filename, str) and filename.strip():
            return filename.strip()
        content_type = item.get("content_type") or item.get("mime_type")
        extension = mimetypes.guess_extension(str(content_type)) if content_type else None
        return f"{asset_id}{extension or '.png'}"

    def _resolve_content_type(self, item: dict[str, Any], filename: str) -> str:
        content_type = item.get("content_type") or item.get("mime_type")
        if isinstance(content_type, str) and content_type.strip():
            return content_type.strip()
        guessed, _ = mimetypes.guess_type(filename)
        return guessed or "image/png"

    def _resolve_binary_bytes(self, item: dict[str, Any]) -> bytes:
        base64_value = item.get("image_base64") or item.get("b64_json") or item.get("data_base64")
        if isinstance(base64_value, str) and base64_value.strip():
            try:
                return base64.b64decode(base64_value)
            except ValueError as exc:
                raise AppError(
                    status_code=502,
                    error_code="NANO_BANANA_INVALID_RESPONSE",
                    message="Nano Banana API returned invalid base64 image data.",
                ) from exc

        image_url = item.get("image_url") or item.get("download_url") or item.get("url")
        if isinstance(image_url, str) and image_url.strip():
            return self._download_binary(image_url.strip())

        return self._placeholder_png_bytes()

    def _download_binary(self, url: str) -> bytes:
        settings = get_settings()
        req = request.Request(url, headers={"Accept": "*/*"}, method="GET")
        try:
            with request.urlopen(req, timeout=settings.nano_banana_timeout_ms / 1000) as response:
                return response.read()
        except error.HTTPError as exc:
            raise AppError(
                status_code=502,
                error_code="NANO_BANANA_DOWNLOAD_HTTP_ERROR",
                message=f"Nano Banana image download HTTP error: {exc.code}",
            ) from exc
        except error.URLError as exc:
            raise AppError(
                status_code=502,
                error_code="NANO_BANANA_DOWNLOAD_CONNECTION_ERROR",
                message=f"Nano Banana image download connection error: {exc.reason}",
            ) from exc

    def _placeholder_png_bytes(self) -> bytes:
        return base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a7U8AAAAASUVORK5CYII=")

    def _mock_response(
        self,
        *,
        source_asset_ids: list[str],
        card_request: dict[str, object],
    ) -> dict[str, object]:
        variant_count = int(card_request.get("variant_count", 1) or 1)
        outputs = [
            {
                "asset_id": f"variant_{uuid4().hex[:8]}",
                "filename": f"mock_variant_{index + 1}.png",
                "content_type": "image/png",
                "binary_bytes": self._placeholder_png_bytes(),
                "remote_url": None,
            }
            for index in range(variant_count)
        ]
        return {
            "provider": self.provider_name,
            "variant_asset_ids": [item["asset_id"] for item in outputs],
            "outputs": outputs,
            "request_payload": card_request,
            "api_key_present": True,
            "raw_response": {
                "candidates": [],
            },
        }


nano_banana_adapter = NanoBananaAdapter()
