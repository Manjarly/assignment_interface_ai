"""
Contract definitions for the knowledge system.
Imports directly from harness.contract if available, or provides fallback dataclasses.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable

try:
    for parent in Path(__file__).resolve().parents:
        harness_path = parent / "harness"
        if (harness_path / "contract.py").exists():
            if str(harness_path) not in sys.path:
                sys.path.insert(0, str(harness_path))
            break
    from contract import Answer, Conflict, KnowledgeSystem, Page, Snapshot, Source  # type: ignore
except Exception:
    @dataclass(frozen=True)
    class Page:
        url: str
        title: str
        markdown: str
        fetched_at: str

    @dataclass(frozen=True)
    class Snapshot:
        snapshot_id: str
        taken_on: str
        pages: list[Page]

    @dataclass
    class Source:
        url: str
        snapshot_id: Optional[str] = None
        quote: Optional[str] = None

    @dataclass
    class Answer:
        text: str
        sources: list[Source] = field(default_factory=list)
        confident: bool = True
        conflict_note: Optional[str] = None

    @dataclass
    class Conflict:
        topic: str
        values: list[str]
        sources: list[Source]
        resolution: Optional[str] = None
        reason: Optional[str] = None

    @runtime_checkable
    class KnowledgeSystem(Protocol):
        def ingest(self, snapshot: Snapshot) -> None:
            ...

        def answer(self, question: str, as_of: Optional[str] = None) -> Answer:
            ...

        def conflicts(self) -> list[Conflict]:
            ...
