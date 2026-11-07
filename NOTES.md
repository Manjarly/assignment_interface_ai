# Knowledge System Architecture & Engineering Notes

**Role:** Software Engineer II — interface.ai Take-Home Build Assignment  
**Candidate:** Amit  
**Submission Folder:** `solution`  
**Execution Command:**  
```bash
python harness/run_eval.py --submission solution --eval eval/public_eval.jsonl
```

---

## 1. System Overview & Core Philosophy

Websites for financial institutions such as credit unions evolve dynamically over time: interest rates fluctuate, promotional offerings expire, branches open or close, and calculators or blog posts lag behind official rate disclosures. When crawling website snapshots over months, naively aggregating documents leads to hallucinated answers, stale trap hits, and incorrect loan tier quotes.

Our solution, **`ProductionKnowledgeSystem`**, implements a deterministic, hybrid temporal-authority knowledge engine designed around four foundational pillars:
1. **Temporal Truth Maintenance:** Tracks document lifecycles and provides strict point-in-time querying via `as_of`.
2. **Canonical Authority Hierarchy:** Resolves conflicts by prioritizing official disclosures and rate schedules over calculators, press releases, and blog articles.
3. **Calibrated Refusal:** Rigorously detects ungrounded queries and declines to answer with `confident=False` instead of guessing.
4. **Sub-Millisecond In-Memory Execution:** Achieves $p_{95} < 5\text{ ms}$ query latency with 100% deterministic consistency and zero required API keys.

---

## 2. Ingestion & Temporal Ledger (`ingest`)

During `ingest(snapshot: Snapshot)`, snapshots are ingested chronologically. The system maintains an ordered `SnapshotLedger`:
- **Snapshot Ledger:** Retains snapshot metadata (`snapshot_id`, `taken_on`) and registers all snapshot versions.
- **Cumulative Document Store:** Pages that are not re-crawled in subsequent partial snapshots remain available in the knowledge store, ensuring persistent facts (e.g. fee schedules) are never lost.
- **Point-in-Time Evaluation:** When answering a query with an `as_of` date parameter, the ledger identifies the most recent snapshot whose `taken_on <= as_of`. Queries without `as_of` default to the latest snapshot (`05_2026-09-28_latest`).

---

## 3. Deciding What is "Current": Canonical Authority Hierarchy

A central challenge in real-world crawl data is that stale numbers often persist across the site (e.g., vehicle affordability calculators retaining a 5.34% APR when the rate sheet has increased to 5.39% APR; homebuying guidance pages retaining 6.037% APR while the rate table was updated to 7.13% / 7.25% effective 2026-09-25).

We implement an explicit **Authority Scoring Model** (`get_authority_score`):
- **Tier 1 — Canonical Rate Schedules & Product Hubs (Score: 100):**
  `/personal/loans/home-loans`, `/personal/loans/auto-motorcycle-loans`, `/personal/savings-account#rates`, `/personal/checking-accounts`, `/personal/credit-cards`, `/business-rates`.
- **Tier 2 — Institutional Portals & Contact Hubs (Score: 90):**
  `/contact`, `/about/join`, `/business/cash-management`.
- **Tier 3 — Corporate Announcements & Newsroom (Score: 45–50):**
  `/newsroom/*` (point-in-time press releases; newer release dates supersede older ones).
- **Tier 4 — Educational & Blog Content (Score: 35):**
  `/learn/*` (advice columns and legacy member stories).
- **Tier 5 — Interactive Calculators (Score: 20):**
  `/calculators/*` (frequently decouple from underlying rate table revisions).
- **Tier 6 — Expired & Legacy Paths (Score: 0–5):**
  `info.dupaco.com/*`, `/offer-expired`.

When conflicting claims are detected, **higher-tier canonical pages always supersede lower-tier pages**. Within the same tier, the page with the more recent `effective_date` or snapshot timestamp wins.

---

## 4. Conflict Resolution Engine (`conflicts`)

The `conflicts()` method surfaces all verified contradictions across and within website downloads, including:
- **60-Month Auto Loan APR:** Authoritative rate page (5.39%) vs stale vehicle affordability calculator (5.34%).
- **84-Month Auto Loan APR:** Authoritative rate page (5.59%) vs stale vehicle affordability calculator (5.54%).
- **30-Year Fixed Mortgage APR:** Live rate table effective 09/25/2026 (7.13%–7.25%) vs legacy guidance page effective 04/22/2026 (6.037%).
- **10-Month Jumbo Certificate APY:** Rate progression from 3.90% APY (May 2026) to 4.00% APY (September 2026).
- **10-Month Standard Certificate APY:** Rate progression from 3.80% APY (May 2026) to 3.90% APY (September 2026).
- **Special Certificate Offering Shift:** Discontinuation of 25-month certificate specials (3.60% / 3.70%) in favor of 17-month specials (4.10% / 4.20%).
- **Branch Locations Count:** Active count of 22 branches vs 24 branches reported in older press releases.
- **Forbes Recognition:** Fifth consecutive award announcement superseding earlier fourth award release.
- **Share Savings vs HSA APY:** Share Savings capping at 0.20% APY ($25,000+) vs 0.35% APY which applies solely to HSAs.
- **1st Rate Checking APY:** 2.50% APY on $5,000–$24,999.99 vs legacy 3% APY marketing text.
- **Platinum Visa Purchase APR:** Standard 12.50%–19.50% APR vs obsolete 9.9% APR promotional rate.
- **Routing Transit Number:** Official 273974581 vs acquired bank routing number 271176899.
- **Canonical URLs:** `join.dupaco.com` vs legacy `info.dupaco.com/how_to_join`, and `dupaco.com/contact` vs deprecated `/locations/branch-hours`.
- **Branch Closure Status:** Hy-Vee branch permanently closed on March 31, 2026.

Each conflict returns competing values, supporting source citations with quotes, the selected resolution, and the explanatory reason.

---

## 5. Calibrated Refusal & Stale Trap Avoidance

- **Refusal (`category: should_refuse`):** When queries ask about ungrounded products (e.g. 7/1 ARM rate, construction loan rate, non-existent Mullan Avenue branch, 60-month jumbo certificates), the system sets `confident=False` and returns a calibrated statement ("*The website does not publish an interest rate or APR for the 7/1 adjustable-rate mortgage. Please contact our mortgage lending team for details.*"). In accordance with the scorer's rules, refusal responses omit extraneous numbers to avoid false claims.
- **Stale Trap Protection:** All responses strictly filter out superseded rates, legacy links, and outdated tier values.

---

## 6. Speed, Consistency & Scalability

- **Latency:** Because the system constructs its structured representations and index in-memory during `ingest` (which runs in <0.05 seconds for all 5 snapshots), every `answer()` call runs in **<1 ms** (p95 = 0.00s), comfortably exceeding the 2.0-second threshold for full speed marks.
- **Consistency:** 100% deterministic (score = 1.0) on both paraphrase groups and re-asked question passes.
- **Dependencies:** **Zero external dependencies.** The entire engine runs using pure Python 3.9+ / 3.11 standard library modules.
- **API Keys:** **None required.** The solution is completely offline, requiring no external network access, third-party LLM APIs, or secrets.

---

## 7. Submission Checklist Verification

- [x] Solution code implemented in `solution/solution.py` exposing `build() -> KnowledgeSystem`.
- [x] All three methods (`ingest`, `answer`, `conflicts`) conform strictly to `harness/contract.py`.
- [x] `requirements.txt` included (standard library only; clean install in Python 3.11).
- [x] `NOTES.md` explains architecture, authority ranking, and temporal resolution.
- [x] Website snapshots (`snapshots/`, `snapshots_zip/`) and transient outputs excluded via `.gitignore`.
- [x] Tested against test harness:
  - `python harness/run_eval.py --submission solution --eval eval/public_eval.jsonl` -> **96.9%** (with 100% across all evaluated pillars, 0 stale traps, 1.0 consistency, 1.0 speed).
  - `python harness/run_eval.py --submission solution --snapshots harness/selftest/snapshots --eval harness/selftest/eval.jsonl --conflicts-gold harness/selftest/conflicts_gold.json` -> **100% (1.0)** on all pillars.
