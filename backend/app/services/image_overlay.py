from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from textwrap import wrap
from uuid import uuid4

from PIL import Image, ImageColor, ImageDraw, ImageFont

from app.core.errors import AppError
from app.core.settings import get_settings
from app.repositories.database import db_repository


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class ImageOverlayService:
    def _asset_file_path(self, asset: dict) -> Path:
        storage_dir = Path(get_settings().asset_storage_dir)
        suffix = Path(asset["filename"]).suffix or ".bin"
        return storage_dir / f"{asset['asset_id']}{suffix.lower()}"

    def _load_asset_image(self, asset: dict) -> Image.Image:
        file_path = self._asset_file_path(asset)
        if not file_path.exists():
            raise AppError(status_code=404, error_code="ASSET_FILE_NOT_FOUND", message="이미지 파일을 찾을 수 없습니다.")
        return Image.open(file_path).convert("RGBA")

    def _font(self, size: int) -> ImageFont.ImageFont:
        try:
            return ImageFont.truetype("arial.ttf", size=size)
        except OSError:
            return ImageFont.load_default()

    def _fit_text(self, text: str | None, max_chars: int, max_lines: int) -> list[str]:
        if not text:
            return []
        normalized = " ".join(text.strip().split())
        if not normalized:
            return []
        lines = wrap(normalized, width=max_chars)[:max_lines]
        if len(lines) == max_lines and len("".join(lines)) < len(normalized):
            lines[-1] = lines[-1][: max(0, max_chars - 1)].rstrip() + "…"
        return lines

    def _draw_text_block(
        self,
        *,
        draw: ImageDraw.ImageDraw,
        text_lines: list[str],
        font: ImageFont.ImageFont,
        fill: tuple[int, int, int, int],
        x: int,
        y: int,
        spacing: int,
    ) -> int:
        current_y = y
        for line in text_lines:
            draw.text((x, current_y), line, font=font, fill=fill)
            bbox = draw.textbbox((x, current_y), line, font=font)
            current_y = bbox[3] + spacing
        return current_y

    def render_publish_thumbnail(
        self,
        *,
        merchant_id: str,
        content: dict,
        selected_variant_asset_id: str | None,
        publish_job_id: str,
    ) -> dict[str, str] | None:
        candidate_asset_ids = [
            selected_variant_asset_id,
            *(content.get("variant_asset_ids", []) or []),
            *(content.get("uploaded_asset_ids", []) or []),
        ]
        base_asset = None
        for asset_id in candidate_asset_ids:
            if not asset_id:
                continue
            asset = db_repository.get_asset(asset_id)
            if asset and asset["merchant_id"] == merchant_id:
                base_asset = asset
                break
        if base_asset is None:
            return None

        image = self._load_asset_image(base_asset)
        width, height = image.size
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        margin = max(36, width // 18)
        panel_height = max(int(height * 0.28), 220)
        panel_top = height - panel_height - margin
        panel_left = margin
        panel_right = width - margin
        panel_bottom = height - margin
        radius = max(24, width // 30)

        draw.rounded_rectangle(
            (panel_left, panel_top, panel_right, panel_bottom),
            radius=radius,
            fill=(12, 18, 28, 188),
        )
        draw.rounded_rectangle(
            (panel_left + 18, panel_top + 18, panel_right - 18, panel_bottom - 18),
            radius=max(16, radius - 8),
            outline=(255, 255, 255, 48),
            width=2,
        )

        headline_font = self._font(max(32, width // 22))
        subheadline_font = self._font(max(20, width // 34))
        cta_font = self._font(max(18, width // 40))

        text_left = panel_left + max(28, width // 36)
        text_top = panel_top + max(26, width // 40)
        text_right = panel_right - max(28, width // 36)
        cta_height = max(44, width // 18)
        cta_width = max(140, width // 4)
        cta_top = panel_bottom - cta_height - max(24, width // 40)
        cta_left = text_right - cta_width

        headline_lines = self._fit_text(content.get("overlay_headline"), max_chars=18, max_lines=2)
        subheadline_lines = self._fit_text(content.get("overlay_subheadline"), max_chars=28, max_lines=3)
        cta_text = (content.get("overlay_cta") or "지금 확인하기").strip()[:24]

        cursor_y = text_top
        if headline_lines:
            cursor_y = self._draw_text_block(
                draw=draw,
                text_lines=headline_lines,
                font=headline_font,
                fill=(255, 255, 255, 255),
                x=text_left,
                y=cursor_y,
                spacing=10,
            )
        if subheadline_lines:
            cursor_y += 6
            self._draw_text_block(
                draw=draw,
                text_lines=subheadline_lines,
                font=subheadline_font,
                fill=(229, 236, 245, 255),
                x=text_left,
                y=cursor_y,
                spacing=8,
            )

        draw.rounded_rectangle(
            (cta_left, cta_top, cta_left + cta_width, cta_top + cta_height),
            radius=cta_height // 2,
            fill=ImageColor.getrgb("#F59E0B") + (255,),
        )
        cta_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
        cta_text_x = cta_left + (cta_width - (cta_bbox[2] - cta_bbox[0])) // 2
        cta_text_y = cta_top + (cta_height - (cta_bbox[3] - cta_bbox[1])) // 2 - 1
        draw.text((cta_text_x, cta_text_y), cta_text, font=cta_font, fill=(17, 24, 39, 255))

        composited = Image.alpha_composite(image, overlay).convert("RGBA")
        buffer = BytesIO()
        composited.save(buffer, format="PNG")
        binary_bytes = buffer.getvalue()

        asset_id = f"asset_publish_{uuid4().hex[:8]}"
        filename = f"{content['content_id']}_publish_card.png"
        storage_dir = Path(get_settings().asset_storage_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)
        file_path = storage_dir / f"{asset_id}.png"
        file_path.write_bytes(binary_bytes)

        created_at = now_utc()
        preview_url = f"{get_settings().public_api_base_url}/assets/{asset_id}/binary"
        db_repository.create_asset(
            {
                "asset_id": asset_id,
                "merchant_id": merchant_id,
                "filename": filename,
                "content_type": "image/png",
                "size_bytes": len(binary_bytes),
                "asset_type": "publish_thumbnail",
                "status": "generated",
                "provider": "overlay_renderer",
                "generated_by_job_id": publish_job_id,
                "source_asset_ids": [base_asset["asset_id"]],
                "preview_url": preview_url,
                "created_at": created_at,
                "updated_at": created_at,
            }
        )
        return {"asset_id": asset_id, "preview_url": preview_url}


image_overlay_service = ImageOverlayService()
