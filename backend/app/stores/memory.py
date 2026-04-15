from dataclasses import dataclass, field
from threading import RLock
from typing import Dict


@dataclass
class MemoryStore:
    lock: RLock = field(default_factory=RLock)
    contents: Dict[str, object] = field(default_factory=dict)
    reviews: Dict[str, object] = field(default_factory=dict)
    reports: Dict[str, object] = field(default_factory=dict)
    jobs: Dict[str, object] = field(default_factory=dict)

