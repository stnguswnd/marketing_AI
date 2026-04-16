from app.services.image_card import image_card_service


def test_build_instagram_card_plan_returns_expected_defaults():
    plan = image_card_service.build_instagram_card_plan(
        {
            "goal": "store_visit",
            "title": "벚꽃 시즌 시그니처",
            "body": "대표 메뉴를 강조하는 카드가 필요합니다.",
            "must_include": ["대표 메뉴", "시즌 무드"],
            "must_avoid": ["허위 할인", "과장 표현"],
            "hashtags": ["#spring", "#store"],
        }
    )

    assert plan.card_spec.aspect_ratio == "4:5"
    assert plan.card_spec.width == 1080
    assert plan.card_spec.height == 1350
    assert plan.card_spec.text_mode == "text-free"
    assert plan.variant_count == 3
    assert "Instagram feed card" in plan.prompt
    assert "허위 할인" in plan.negative_prompt
