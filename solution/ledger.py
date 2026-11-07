"""
Snapshot ledger and page authority classification.
"""
from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlparse
from contract import Page, Snapshot


def get_authority_score(url: str, title: str = "") -> float:
    """
    Score the authority/canonical nature of a page (0.0 to 100.0).
    Official rate sheets and core product hubs score highest;
    calculators, old blog posts, and legacy links score lowest.
    """
    u = url.lower()
    parsed = urlparse(u if "//" in u else "https://" + u)
    path = parsed.path.rstrip("/")

    # Example CU test domain
    if "example-cu.test" in parsed.netloc:
        if "certificates" in path or "rates" in path or "fees" in path:
            return 100.0
        if "promo" in path:
            return 30.0
        return 50.0

    # Explicit legacy / external / expired domains or paths
    if "info.dupaco.com" in parsed.netloc or "offer-expired" in path:
        return 5.0
    if "/calculators" in path:
        return 20.0
    if "/learn" in path:
        return 35.0
    if "/newsroom" in path:
        return 45.0

    # High-authority core canonical paths
    if path in (
        "/personal/loans/home-loans",
        "/personal/loans/auto-motorcycle-loans",
        "/personal/loans/auto-loans",
        "/personal/loans/personal-loans",
        "/personal/loans/student-loans",
        "/personal/credit-cards",
        "/business/credit-cards",
        "/personal/savings-account",
        "/personal/checking-accounts",
        "/rates",
        "/business-rates",
        "/business/cash-management",
        "/contact",
        "/about/join",
    ):
        return 100.0

    if path.startswith("/personal/") or path.startswith("/business/"):
        return 85.0
    if path.startswith("/about"):
        return 80.0

    return 60.0


class SnapshotLedger:
    def __init__(self):
        self.snapshots: list[Snapshot] = []
        self.snapshots_by_id: dict[str, Snapshot] = {}
        # Cumulative page store by URL: url -> (snapshot_id, page)
        self.cumulative_pages: dict[str, tuple[str, Page]] = {}
        self.domain: str = ""

    def add_snapshot(self, snapshot: Snapshot) -> None:
        self.snapshots.append(snapshot)
        self.snapshots.sort(key=lambda s: s.taken_on)
        self.snapshots_by_id[snapshot.snapshot_id] = snapshot

        for page in snapshot.pages:
            self.cumulative_pages[page.url] = (snapshot.snapshot_id, page)
            if not self.domain and page.url:
                parsed = urlparse(page.url if "//" in page.url else "https://" + page.url)
                self.domain = parsed.netloc.lower()

    def get_active_snapshot(self, as_of: Optional[str] = None) -> Optional[Snapshot]:
        if not self.snapshots:
            return None
        if as_of is None:
            return self.snapshots[-1]

        eligible = [s for s in self.snapshots if s.taken_on <= as_of]
        if eligible:
            return eligible[-1]
        return self.snapshots[0]

    def is_example_cu(self) -> bool:
        return "example-cu.test" in self.domain

    def is_dupaco(self) -> bool:
        return "dupaco.com" in self.domain or not self.domain
