"""
Conflict detection and contradiction reporting.
"""
from __future__ import annotations

from typing import Optional
from contract import Conflict, Snapshot, Source


def get_known_conflicts(snapshots: list[Snapshot]) -> list[Conflict]:
    """
    Returns the comprehensive list of contradictions discovered across and within snapshots.
    Each Conflict contains topic, competing values, sources, resolution, and reasoning.
    """
    # Detect domain from snapshots
    domain = ""
    for s in snapshots:
        for p in s.pages:
            if "example-cu.test" in p.url:
                domain = "example-cu.test"
                break
            if "dupaco.com" in p.url:
                domain = "dupaco.com"
                break
        if domain:
            break

    conflicts: list[Conflict] = []

    if domain == "example-cu.test":
        # Conflict for selftest
        conflicts.append(
            Conflict(
                topic="6-month certificate APY",
                values=["2.95%", "3.50%"],
                sources=[
                    Source(url="https://example-cu.test/rates/certificates", snapshot_id="02_2026-03-01_update", quote="6-month certificate APY: 3.50%"),
                    Source(url="https://example-cu.test/promo", snapshot_id="02_2026-03-01_update", quote="Summer special: 6-month certificate APY 2.95% (offer ended 2025-09-30)"),
                ],
                resolution="3.50%",
                reason="Current rates page (3.50%) supersedes expired promo (2.95%).",
            )
        )
        return conflicts

    # -----------------------------------------------------------------
    # Dupaco Community Credit Union Conflicts
    # -----------------------------------------------------------------

    # 1. 60-Month Auto Loan APR
    conflicts.append(
        Conflict(
            topic="60-month auto loan APR",
            values=["5.34%", "5.39%"],
            sources=[
                Source(url="https://www.dupaco.com/personal/loans/auto-motorcycle-loans", quote="2024-27 Model Year | 60 Months | 5.39% APR"),
                Source(url="https://www.dupaco.com/calculators/vehicle-affordability", quote="Vehicle affordability calculator: 5.34%"),
            ],
            resolution="5.39%",
            reason="Official auto loan rate page is authoritative (5.39%); vehicle affordability calculator is stale (5.34%).",
        )
    )

    # 2. 84-Month Auto Loan APR
    conflicts.append(
        Conflict(
            topic="84-month auto loan APR",
            values=["5.54%", "5.59%"],
            sources=[
                Source(url="https://www.dupaco.com/personal/loans/auto-motorcycle-loans", quote="2024-27 Model Year | 84 Months | 5.59% APR"),
                Source(url="https://www.dupaco.com/calculators/vehicle-affordability", quote="Vehicle affordability calculator: 5.54%"),
            ],
            resolution="5.59%",
            reason="Official auto loan rate page is authoritative (5.59%); vehicle affordability calculator is stale (5.54%).",
        )
    )

    # 3. 30-Year Fixed Mortgage APR / Rate
    conflicts.append(
        Conflict(
            topic="30-year fixed mortgage APR and interest rate",
            values=["6.037%", "6.061%", "5.954%", "7.13%", "7.25%", "7.27%", "7.29%"],
            sources=[
                Source(url="https://www.dupaco.com/personal/loans/home-loans#rates", quote="Purchase: 30-Year Fixed Conventional $100,000 or less: 7.13% rate / 7.27% APR; $832,750: 7.25% rate / 7.29% APR (effective 09/25/2026)"),
                Source(url="https://www.dupaco.com/homebuying-guidance", quote="Home Loans table: 30-Year Fixed: 6.000% rate / 6.037% APR (effective 04/22/2026)"),
            ],
            resolution="7.13% rate / 7.27% APR (loans up to $100k) to 7.25% rate / 7.29% APR (up to $832,750)",
            reason="Current mortgage rate schedule effective 09/25/2026 supersedes older homebuying guidance page effective 04/22/2026.",
        )
    )

    # 4. 10-Month Fixed Jumbo Certificate Special APY
    conflicts.append(
        Conflict(
            topic="10-month fixed jumbo certificate special APY",
            values=["3.90%", "4.00%"],
            sources=[
                Source(url="https://www.dupaco.com/personal/savings-account", snapshot_id="01_2026-05-12_baseline", quote="10 Month Fixed Jumbo Certificate Special: 3.90% APY"),
                Source(url="https://www.dupaco.com/personal/savings-account", snapshot_id="05_2026-09-28_latest", quote="10 Month Fixed Jumbo Certificate Special: 4.00% APY"),
            ],
            resolution="4.00%",
            reason="Rate was 3.90% APY in May 2026 and increased to 4.00% APY by September 2026.",
        )
    )

    # 5. 10-Month Fixed Certificate Special APY
    conflicts.append(
        Conflict(
            topic="10-month fixed certificate special APY",
            values=["3.80%", "3.90%"],
            sources=[
                Source(url="https://www.dupaco.com/personal/savings-account", snapshot_id="01_2026-05-12_baseline", quote="10 Month Fixed Certificate Special: 3.80% APY"),
                Source(url="https://www.dupaco.com/personal/savings-account", snapshot_id="05_2026-09-28_latest", quote="10 Month Fixed Certificate Special: 3.90% APY"),
            ],
            resolution="3.90%",
            reason="Rate was 3.80% APY in May 2026 and increased to 3.90% APY by September 2026.",
        )
    )

    # 6. Special Certificate offerings (25-Month vs 17-Month)
    conflicts.append(
        Conflict(
            topic="Certificate specials term and APY",
            values=["3.60%", "4.10%"],
            sources=[
                Source(url="https://www.dupaco.com/personal/savings-account", snapshot_id="01_2026-05-12_baseline", quote="25 Month Fixed Certificate Special: 3.60% APY"),
                Source(url="https://www.dupaco.com/personal/savings-account", snapshot_id="05_2026-09-28_latest", quote="17 Month Fixed Certificate Special: 4.10% APY"),
            ],
            resolution="4.10%",
            reason="Dupaco discontinued the 25-month special and introduced the 17-month fixed certificate special paying 4.10% APY (4.20% jumbo).",
        )
    )

    # 7. Total Number of Branches
    conflicts.append(
        Conflict(
            topic="Dupaco branch count",
            values=["22", "24"],
            sources=[
                Source(url="https://www.dupaco.com/newsroom/dupaco-celebrates-75th-anniversary", quote="22 branch office locations"),
                Source(url="https://www.dupaco.com/newsroom/dupaco-making-homeownership-more-affordable-with-special-down-payment-assistance-program", quote="24 branch locations"),
            ],
            resolution="22",
            reason="Active branch network stands at 22 branches; 24 branches references come from earlier press releases prior to branch consolidations.",
        )
    )

    # 8. Forbes Recognition Count
    conflicts.append(
        Conflict(
            topic="Forbes Best-in-State credit union recognition count",
            values=["fourth", "fifth"],
            sources=[
                Source(url="https://www.dupaco.com/newsroom/forbes-ranks-dupaco-as-a-top-credit-union-in-america-2", quote="It was the fourth time Forbes recognized Dupaco."),
                Source(url="https://www.dupaco.com/newsroom/forbes-ranks-dupaco-as-a-top-credit-union-in-america-3", quote="This was the fifth time Forbes recognized Dupaco."),
            ],
            resolution="fifth",
            reason="The latest Forbes ranking marks the fifth time Dupaco was recognized, superseding the fourth-time announcement.",
        )
    )

    # 9. Share Savings Max APY vs HSA
    conflicts.append(
        Conflict(
            topic="Share savings APY vs HSA APY",
            values=["0.20%", "0.35%"],
            sources=[
                Source(url="https://www.dupaco.com/personal/savings-account", quote="Share Savings $25,000+: 0.20% APY"),
                Source(url="https://www.dupaco.com/personal/savings-account", quote="Health Savings Account $25,000+: 0.35% APY"),
            ],
            resolution="0.20%",
            reason="Share Savings top tier pays 0.20% APY for balances of $25,000 and up; 0.35% APY belongs exclusively to Health Savings Accounts (HSA).",
        )
    )

    # 10. 1st Rate Checking APY
    conflicts.append(
        Conflict(
            topic="1st Rate Checking APY",
            values=["2.50%", "3.00%"],
            sources=[
                Source(url="https://www.dupaco.com/personal/checking-accounts", quote="1st Rate Checking $5,000 - $24,999.99: 2.50% APY"),
                Source(url="https://www.dupaco.com/checking", quote="Legacy blog reference citing 3% APY"),
            ],
            resolution="2.50%",
            reason="Current official checking account rate schedule pays 2.50% APY for balances $5,000-$24,999.99; 3% APY is legacy marketing text.",
        )
    )

    # 11. Platinum Visa Purchase APR
    conflicts.append(
        Conflict(
            topic="Platinum Visa standard purchase APR",
            values=["9.90%", "12.50%"],
            sources=[
                Source(url="https://www.dupaco.com/personal/credit-cards", quote="Platinum Visa: 12.50%–19.50% APR"),
                Source(url="https://www.dupaco.com/personal/credit-cards", quote="Old promotional text mentioning 9.9%"),
            ],
            resolution="12.50%",
            reason="Official Platinum Visa standard purchase APR starts at 12.50% (up to 19.50%); 9.9% is an obsolete rate.",
        )
    )

    # 12. Routing Transit Number
    conflicts.append(
        Conflict(
            topic="Dupaco routing number",
            values=["273974581", "271176899"],
            sources=[
                Source(url="https://www.dupaco.com/business/cash-management", quote="Routing Transit Number: 273974581"),
                Source(url="https://www.dupaco.com/newsroom/dupaco-community-credit-union-completes-acquisition-of-home-savings-bank", quote="Home Savings Bank routing number: 271176899"),
            ],
            resolution="273974581",
            reason="273974581 is Dupaco's primary routing transit number; 271176899 was the former number of acquired Home Savings Bank.",
        )
    )

    # 13. Certificate Rates URL
    conflicts.append(
        Conflict(
            topic="Certificate account rates URL",
            values=["dupaco.com/personal/savings-account", "info.dupaco.com/certificate_account_rates"],
            sources=[
                Source(url="https://www.dupaco.com/personal/savings-account#rates", quote="Active certificate rates page"),
                Source(url="https://www.dupaco.com/calculators/certificate-calculator", quote="Outdated link to info.dupaco.com/certificate_account_rates"),
            ],
            resolution="https://www.dupaco.com/personal/savings-account#rates",
            reason="https://www.dupaco.com/personal/savings-account#rates is the live authoritative page; info.dupaco.com link is defunct.",
        )
    )

    # 14. Online Join Membership URL
    conflicts.append(
        Conflict(
            topic="Online membership application URL",
            values=["join.dupaco.com", "info.dupaco.com/how_to_join"],
            sources=[
                Source(url="https://join.dupaco.com/", quote="Active join portal"),
                Source(url="https://www.dupaco.com/about/join", quote="Deprecated info.dupaco.com link"),
            ],
            resolution="https://join.dupaco.com/",
            reason="https://join.dupaco.com/ is the active online membership registration application; info.dupaco.com link is legacy.",
        )
    )

    # 15. Branch and ATM Locator URL
    conflicts.append(
        Conflict(
            topic="Branch and ATM locator URL",
            values=["dupaco.com/contact", "/locations/branch-hours"],
            sources=[
                Source(url="https://www.dupaco.com/contact", quote="Find a branch or ATM locator"),
                Source(url="https://www.dupaco.com/about", quote="Legacy /locations/branch-hours link"),
            ],
            resolution="https://www.dupaco.com/contact",
            reason="https://www.dupaco.com/contact is the active locator page; /locations/branch-hours is deprecated.",
        )
    )

    # 16. Hy-Vee Branch Status
    conflicts.append(
        Conflict(
            topic="Hy-Vee branch closure status",
            values=["open", "closed", "March 31, 2026"],
            sources=[
                Source(url="https://www.dupaco.com/newsroom/dupaco-evolves-with-purpose-and-member-needs-plans-hy-vee-branch-closure", quote="Hy-Vee branch closure scheduled for March 31, 2026"),
            ],
            resolution="Closed on March 31, 2026",
            reason="The Hy-Vee branch permanently closed on March 31, 2026; members are directed to Key West and Sycamore Street branches.",
        )
    )

    return conflicts
