from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MemoryRepository:
    assets: dict[str, dict] = field(default_factory=dict)
    contents: dict[str, dict] = field(default_factory=dict)
    reviews: dict[str, dict] = field(default_factory=dict)
    reports: dict[str, dict] = field(default_factory=dict)
    jobs: dict[str, dict] = field(default_factory=dict)
    publish_results: dict[str, dict] = field(default_factory=dict)
    audit_logs: dict[str, dict] = field(default_factory=dict)
    request_logs: dict[str, dict] = field(default_factory=dict)


repository = MemoryRepository()
