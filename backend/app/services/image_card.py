from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.schemas.common import ImageVariantProvider


@dataclass(frozen=True)
class InstagramCardSpec:
    aspect_ratio: str
    width: int
    height: int
    visual_style: str
    text_mode: str
    composition: str
    safe_margin_pct: int
    headline: str | None
    subheadline: str | None
    cta_hint: str | None
    avoid_tokens: list[str]


@dataclass(frozen=True)
class CardVariantPlan:
    card_spec: InstagramCardSpec
    prompt: str
    negative_prompt: str
    variant_count: int
    output_format: str


class ImageCardService:
    def build_instagram_card_plan(self, content: dict[str, Any]) -> CardVariantPlan:
        must_include = [str(item).strip() for item in content.get("must_include", []) if str(item).strip()]
        must_avoid = [str(item).strip() for item in content.get("must_avoid", []) if str(item).strip()]
        goal = str(content.get("goal", "store_visit"))
        tone = self._infer_tone(content)

        card_spec = InstagramCardSpec(
            aspect_ratio="4:5",
            width=1080,
            height=1350,
            visual_style=self._visual_style_for_goal(goal),
            text_mode="text-free",
            composition=self._composition_for_goal(goal),
            safe_margin_pct=10,
            headline=self._headline_for_content(content),
            subheadline=self._subheadline_for_content(content),
            cta_hint=self._cta_for_goal(goal),
            avoid_tokens=must_avoid,
        )
        prompt = self._build_prompt(content, card_spec, tone, must_include)
        negative_prompt = self._build_negative_prompt(card_spec, must_avoid)

        return CardVariantPlan(
            card_spec=card_spec,
            prompt=prompt,
            negative_prompt=negative_prompt,
            variant_count=3,
            output_format="jpeg",
        )

    def build_nano_banana_request(
        self,
        *,
        content: dict[str, Any],
        source_assets: list[dict[str, Any]],
    ) -> dict[str, Any]:
        plan = self.build_instagram_card_plan(content)
        return {
            "provider": ImageVariantProvider.NANO_BANANA.value,
            "source_assets": [
                {
                    "asset_id": asset["asset_id"],
                    "filename": asset["filename"],
                    "content_type": asset["content_type"],
                    "preview_url": asset.get("preview_url"),
                }
                for asset in source_assets
            ],
            "card_spec": {
                "aspect_ratio": plan.card_spec.aspect_ratio,
                "width": plan.card_spec.width,
                "height": plan.card_spec.height,
                "visual_style": plan.card_spec.visual_style,
                "text_mode": plan.card_spec.text_mode,
                "composition": plan.card_spec.composition,
                "safe_margin_pct": plan.card_spec.safe_margin_pct,
                "headline": plan.card_spec.headline,
                "subheadline": plan.card_spec.subheadline,
                "cta_hint": plan.card_spec.cta_hint,
                "avoid_tokens": plan.card_spec.avoid_tokens,
            },
            "prompt": plan.prompt,
            "negative_prompt": plan.negative_prompt,
            "variant_count": plan.variant_count,
            "output_format": plan.output_format,
        }

    def _visual_style_for_goal(self, goal: str) -> str:
        if goal == "seasonal_promotion":
            return "editorial"
        if goal == "awareness":
            return "brand-forward"
        return "product-focus"

    def _composition_for_goal(self, goal: str) -> str:
        if goal == "seasonal_promotion":
            return "top-focus"
        if goal == "awareness":
            return "center-focus"
        return "bottom-product"

    def _cta_for_goal(self, goal: str) -> str | None:
        if goal == "store_visit":
            return "visit-store"
        if goal == "seasonal_promotion":
            return "limited-season"
        if goal == "awareness":
            return "brand-discovery"
        return None

    def _headline_for_content(self, content: dict[str, Any]) -> str | None:
        title = str(content.get("title") or "").strip()
        return title[:40] if title else None

    def _subheadline_for_content(self, content: dict[str, Any]) -> str | None:
        body = str(content.get("body") or "").strip()
        return body[:80] if body else None

    def _infer_tone(self, content: dict[str, Any]) -> str:
        hashtags = [str(item).lower() for item in content.get("hashtags", [])]
        if any("trend" in tag for tag in hashtags):
            return "trendy"
        return "friendly"

    def _build_prompt(
        self,
        content: dict[str, Any],
        card_spec: InstagramCardSpec,
        tone: str,
        must_include: list[str],
    ) -> str:
        segments = [
            "Transform the source image into a polished Instagram feed card.",
            "Keep the original subject identity, menu realism, and store context.",
            f"Target size: {card_spec.width}x{card_spec.height}, portrait {card_spec.aspect_ratio}.",
            f"Visual style: {card_spec.visual_style}.",
            f"Composition: {card_spec.composition}.",
            f"Tone: {tone}.",
            f"Leave a clean safe area around the subject by {card_spec.safe_margin_pct} percent.",
            "Prefer text-free card imagery suitable for later UI overlay.",
        ]
        if content.get("goal"):
            segments.append(f"Primary campaign goal: {content['goal']}.")
        if must_include:
            segments.append(f"Must include cues: {', '.join(must_include)}.")
        if content.get("title"):
            segments.append(f"Reference title: {content['title']}.")
        return " ".join(segments)

    def _build_negative_prompt(self, card_spec: InstagramCardSpec, must_avoid: list[str]) -> str:
        segments = [
            "Avoid distorted hands, duplicated objects, broken geometry, fake typography, unreadable text, over-saturated neon colors, and unrelated subjects.",
            "Do not change the product category or store identity.",
            f"Avoid violating the {card_spec.aspect_ratio} portrait framing.",
        ]
        if must_avoid:
            segments.append(f"Additional forbidden cues: {', '.join(must_avoid)}.")
        return " ".join(segments)


image_card_service = ImageCardService()
