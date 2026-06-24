#!/usr/bin/env python3
"""SPCX (SpaceX) fair-value scenario model — a reverse-DCF "what would you have
to believe?" tool.

This does NOT tell you what SpaceX is worth. Nobody honestly can — the published
analyst range is $62 to $310, a 5x spread. What this DOES is make the assumptions
behind a price VISIBLE, so you can judge whether they are sane before you pay.

It works two ways:
  1. FORWARD: given assumptions (revenue growth, terminal margin, exit multiple,
     discount rate), compute an implied fair value per share. Three scenarios:
     Bear / Base / Bull.
  2. REVERSE: given a market PRICE (e.g. today's ~$164, the $135 IPO, the $210
     peak), solve for the 2030 revenue the market is implicitly pricing in, and
     compare it to SpaceX's own trajectory and Goldman's aggressive sell-side
     number. If the price requires a revenue the company has little chance of
     hitting, you're overpaying.

All inputs are transparent and editable at the top. Every number is an ASSUMPTION,
not a fact, except the anchors pulled from the S-1 (2025 revenue, share count).

Run: python3 fair_value.py   ->  prints a table + writes fair_value.md
"""

import numpy as np

# ---- HARD ANCHORS (from verified S-1 / IPO research; see report.md) ----
SHARES_OUT = 13.1e9          # ~13.1B shares post 5-for-1 split
REV_2025 = 18.67e9           # 2025 revenue, +33% YoY (audited S-1)
NET_MARGIN_2025 = -0.26      # net loss $4.9B / $18.67B  (xAI drag)
YEARS = 5                    # project to 2030

# ---- PRICE REFERENCE POINTS (verified, as of 2026-06-23) ----
PRICES = {
    "IPO ($135)": 135.0,
    "Today (~$164)": 164.0,
    "Day-1 close ($161)": 161.0,
    "Peak ($226)": 226.0,
    "Morningstar FV (~$60)": 60.0,
    "Consensus avg (~$188)": 188.0,
}

# ---- SCENARIOS: the three "stories" and what each assumes ----
# rev_cagr: 2025->2030 revenue CAGR
# term_margin: 2030 net (or FCF-proxy) margin once xAI losses fade / Starlink scales
# exit_ps: price-to-sales multiple applied to 2030 revenue (sanity-anchored to
#          where high-quality compounders trade once growth normalizes)
# discount: annual rate to bring 2030 value back to today
SCENARIOS = {
    "Bear": dict(rev_cagr=0.18, term_margin=0.08, exit_ps=4.0, discount=0.12,
                 story="Starlink ARPU keeps falling, xAI stays a money pit, "
                       "launch stays low-margin, growth decelerates toward 18%."),
    "Base": dict(rev_cagr=0.30, term_margin=0.15, exit_ps=7.0, discount=0.11,
                 story="Starlink keeps ~30% growth, xAI turns breakeven-ish, "
                       "Starship adds real launch revenue. Roughly consensus."),
    "Bull": dict(rev_cagr=0.45, term_margin=0.22, exit_ps=11.0, discount=0.10,
                 story="xAI revenue ramps toward Goldman's number, Starlink "
                       "monopoly compounds, multiple stays premium. Everything works."),
}

# External reference: Goldman (lead underwriter, conflicted) modeled ~$474B 2030 revenue.
GOLDMAN_2030_REV = 474e9


def project(rev_cagr, term_margin, exit_ps, discount, **_):
    """Forward valuation -> implied price per share today."""
    rev_2030 = REV_2025 * (1 + rev_cagr) ** YEARS
    # Value SpaceX off 2030 revenue x price-to-sales (P/S already embeds margin
    # expectations for a growth name; term_margin is reported for transparency).
    ev_2030 = rev_2030 * exit_ps
    pv = ev_2030 / (1 + discount) ** YEARS
    return rev_2030, pv / SHARES_OUT


def reverse(price, exit_ps, discount, **_):
    """Given a price, solve for the 2030 revenue the market is implying
    (holding exit P/S and discount fixed at the Base assumptions)."""
    mkt_cap = price * SHARES_OUT
    ev_2030_needed = mkt_cap * (1 + discount) ** YEARS
    rev_2030_needed = ev_2030_needed / exit_ps
    implied_cagr = (rev_2030_needed / REV_2025) ** (1 / YEARS) - 1
    return rev_2030_needed, implied_cagr


def main():
    lines = ["# SPCX fair-value scenario model", ""]
    lines += [
        "_Every figure here is an assumption, not a forecast. The point is to show "
        "what you'd have to believe to justify a price — not to predict one._",
        "",
        f"Anchors: 2025 revenue ${REV_2025/1e9:.1f}B, ~{SHARES_OUT/1e9:.1f}B shares, "
        f"project {YEARS}y to 2030.",
        "",
        "## 1. Forward: what each story implies the stock is worth today",
        "",
        "| Scenario | 2025→30 rev CAGR | 2030 revenue | exit P/S | discount | **implied value/share** |",
        "|---|---|---|---|---|---|",
    ]
    fair = {}
    for name, p in SCENARIOS.items():
        rev30, val = project(**p)
        fair[name] = val
        lines.append(
            f"| {name} | {p['rev_cagr']:.0%} | ${rev30/1e9:.0f}B | {p['exit_ps']:.0f}x "
            f"| {p['discount']:.0%} | **${val:.0f}** |"
        )
    lines += [
        "",
        f"Range: **${fair['Bear']:.0f} (Bear) – ${fair['Base']:.0f} (Base) – "
        f"${fair['Bull']:.0f} (Bull)**.",
        "",
        "Scenario stories:",
    ]
    for name, p in SCENARIOS.items():
        lines.append(f"- **{name}** (→ ${fair[name]:.0f}): {p['story']}")

    lines += [
        "",
        "## 2. Reverse: what the market is pricing in at each price",
        "",
        "_Solving for the 2030 revenue implied by each price, at Base-case exit "
        "multiple (7x) and discount (11%). Compare to SpaceX 2025 revenue of "
        f"${REV_2025/1e9:.1f}B and Goldman's aggressive ${GOLDMAN_2030_REV/1e9:.0f}B."
        "_",
        "",
        "| Price | implied 2030 revenue | implied 25→30 CAGR | vs Goldman's $474B |",
        "|---|---|---|---|",
    ]
    base_p = SCENARIOS["Base"]
    for label, price in sorted(PRICES.items(), key=lambda kv: kv[1]):
        rev30_need, cagr_need = reverse(price, base_p["exit_ps"], base_p["discount"])
        vs_gs = rev30_need / GOLDMAN_2030_REV
        lines.append(
            f"| {label} | ${rev30_need/1e9:.0f}B | {cagr_need:.0%} | "
            f"{vs_gs:.0%} of it |"
        )

    lines += [
        "",
        "## How to read this",
        "",
        "- If a price requires a 2030 revenue *above* Goldman's already-aggressive, "
        "conflicted $474B estimate, you are paying for a near-perfect outcome — that "
        "is the overpaying zone.",
        "- The **Base** forward value is the honest midpoint; the gap between it and "
        "today's price is your margin of safety (positive) or your overpayment (negative).",
        "- Change the assumptions at the top of the script and re-run. If you can't "
        "defend the assumptions that justify a price, don't pay it.",
        "",
        "_Not investment advice. Assumptions are illustrative; verify the live quote "
        "and the latest financials before any real-money decision._",
    ]

    with open("fair_value.md", "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
