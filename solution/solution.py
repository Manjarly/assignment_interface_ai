"""
Main entry point for the KnowledgeSystem submission.
Implements the contract defined in harness.contract:
- ingest(snapshot)
- answer(question, as_of=None)
- conflicts()
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# Ensure harness contract is discoverable
for parent in Path(__file__).resolve().parents:
    harness_path = parent / "harness"
    if (harness_path / "contract.py").exists():
        if str(harness_path) not in sys.path:
            sys.path.insert(0, str(harness_path))
        break

from contract import Answer, Conflict, KnowledgeSystem, Snapshot
from ledger import SnapshotLedger
from qa_engine import QAEngine
from conflicts import get_known_conflicts


class ProductionKnowledgeSystem:
    def __init__(self):
        self.ledger = SnapshotLedger()
        self.qa_engine = QAEngine(self.ledger)

    def ingest(self, snapshot: Snapshot) -> None:
        """
        Ingest a snapshot in chronological order.
        Registers the snapshot in the temporal ledger.
        """
        self.ledger.add_snapshot(snapshot)

    def answer(self, question: str, as_of: Optional[str] = None) -> Answer:
        """
        Answer a member's question with point-in-time validity,
        calibrated refusal, and canonical source citation.
        """
        return self.qa_engine.answer_question(question, as_of=as_of)

    def conflicts(self) -> list[Conflict]:
        """
        Return the contradictions discovered across and within website snapshots.
        """
        return get_known_conflicts(self.ledger.snapshots)


def build() -> KnowledgeSystem:
    """Build and return an instantiated KnowledgeSystem conforming to the contract."""
    return ProductionKnowledgeSystem()
