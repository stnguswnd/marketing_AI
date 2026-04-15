from __future__ import annotations

from uuid import uuid4


class BlogPublishAdapter:
    adapter_name = "blog_stub"

    def publish_post(self, *, content_id: str, title: str, body: str, hashtags: list[str]) -> dict[str, str]:
        external_post_id = f"blog_{uuid4().hex[:10]}"
        slug = title.lower().replace(" ", "-")[:48] or content_id
        return {
            "adapter_name": self.adapter_name,
            "external_post_id": external_post_id,
            "external_url": f"https://blog.example.com/posts/{slug}",
            "status": "queued",
        }


blog_publish_adapter = BlogPublishAdapter()
