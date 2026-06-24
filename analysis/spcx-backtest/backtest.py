#!/usr/bin/env python3
"""SPCX (SpaceX) IPO backtest.

SpaceX listed on NASDAQ as SPCX on 2026-06-12, so there is no two-year
exchange price history to backtest directly. This script tests the
hypothesis against the two real datasets that DO exist:

  1. data/spacex_private_marks.csv — every verifiable pre-IPO per-share mark
     (insider tender offers, secondary-market marks, company FMV), all
     adjusted for the 2026-05-04 5-for-1 split.

  2. data/mega_ipo_comparables.csv — the largest / most-hyped US IPOs,
     used to backtest how a public buyer fares after listing.

Hypothesis under test (formed from known data; see report.md):
  H1 (REJECTED in its original "discount" form — see audit): the $135 offer
      was in fact priced ~5% ABOVE the last Forge secondary mark and above
      the fitted private-mark trend, i.e. there is no built-in private-to-
      public discount cushioning the stock.
  H2: For the mega-IPO reference class, buying at the FIRST-DAY CLOSE (the
      first price actually available to a public buyer) has produced poor
      median 6-12 month returns, while buying at the offer was fine at
      1-6m horizons. NOTE: pop size does NOT predict subsequent returns in
      this sample (Spearman p >> 0.05) — the medians, not the cross-section,
      carry the signal, and n is small.

Adversarial audit corrections incorporated:
  - Headline "implied valuations" with inconsistent share-count bases are
    dropped from the marks CSV; analysis uses transaction prices only.
  - COIN (direct listing) is excluded from offer-based stats.
  - Sensitivity runs: verified+training rows only (excl. approx); RIVN 1m
    disputed value; trend fit excluding the Nov-2025 Forge outlier.
  - Two-year return reported as a range across plausible anchor points.

Run: python3 backtest.py   →  results.md, charts/*.png
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
CHARTS = os.path.join(HERE, "charts")
os.makedirs(CHARTS, exist_ok=True)

IPO_PRICE = 135.0
IPO_DATE = pd.Timestamp("2026-06-12")


def fit_trend(df):
    t = (df["date"] - df["date"].min()).dt.days / 365.25
    coeffs = np.polyfit(t, np.log(df["price_per_share"]), 1)
    t_ipo = (IPO_DATE - df["date"].min()).days / 365.25
    return coeffs, float(np.exp(np.polyval(coeffs, t_ipo)))


def private_marks_analysis():
    df = pd.read_csv(os.path.join(DATA, "spacex_private_marks.csv"), parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)

    coeffs, trend_at_ipo = fit_trend(df)
    trend_cagr = np.exp(coeffs[0]) - 1
    # Sensitivity: drop the Nov-2025 Forge dip the audit flagged as an outlier
    _, trend_at_ipo_noout = fit_trend(df[df["date"] != pd.Timestamp("2025-11-19")])

    first, last = df.iloc[0], df.iloc[-1]
    years_span = (last["date"] - first["date"]).days / 365.25
    realized_cagr = (last["price_per_share"] / first["price_per_share"]) ** (1 / years_span) - 1

    last_price = last["price_per_share"]
    # Two-year return range across plausible anchors (audit finding 9)
    anchors = df[(df["date"] >= IPO_DATE - pd.DateOffset(years=2))
                 & (df["date"] <= IPO_DATE - pd.DateOffset(months=17))]
    two_yr_lo = last_price / anchors["price_per_share"].max() - 1
    two_yr_hi = last_price / anchors["price_per_share"].min() - 1

    fig, ax = plt.subplots(figsize=(11, 6))
    for ev, g in df.groupby("event_type"):
        ax.scatter(g["date"], g["price_per_share"], label=ev, s=60, zorder=3)
    span = pd.date_range(df["date"].min(), IPO_DATE, freq="ME")
    tt = (span - df["date"].min()).days / 365.25
    ax.plot(span, np.exp(np.polyval(coeffs, tt)), "k--", alpha=0.6,
            label=f"log-linear trend ({trend_cagr:.0%}/yr)")
    ax.axvline(pd.Timestamp("2026-02-01"), color="purple", ls=":", alpha=0.7)
    ax.text(pd.Timestamp("2026-02-03"), 21, "xAI merger\n(regime change)", fontsize=8, color="purple")
    ax.scatter([IPO_DATE], [IPO_PRICE], marker="*", s=400, color="red", zorder=4,
               label=f"IPO price ${IPO_PRICE:.0f}")
    ax.set_yscale("log")
    ax.set_ylabel("$/share, split-adjusted (log scale)")
    ax.set_title("SpaceX pre-IPO per-share marks vs $135 IPO price")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "private_marks.png"), dpi=130)
    plt.close(fig)

    return {
        "n_marks": len(df),
        "span": f"{first['date'].date()} → {last['date'].date()}",
        "first_mark": f"${first['price_per_share']:.2f} ({first['date'].date()})",
        "last_mark": f"${last_price:.2f} ({last['date'].date()})",
        "realized_cagr": realized_cagr,
        "trend_cagr": trend_cagr,
        "trend_at_ipo": trend_at_ipo,
        "trend_at_ipo_noout": trend_at_ipo_noout,
        "ipo_vs_trend": IPO_PRICE / trend_at_ipo - 1,
        "ipo_vs_trend_noout": IPO_PRICE / trend_at_ipo_noout - 1,
        "ipo_vs_last_mark": IPO_PRICE / last_price - 1,
        "two_yr_lo": two_yr_lo,
        "two_yr_hi": two_yr_hi,
    }


def add_returns(df):
    df = df.copy()
    df["day1_pop"] = df["day1_close"] / df["offer_price"] - 1  # NaN for COIN
    for m in (1, 6, 12):
        df[f"ret_offer_{m}m"] = df[f"price_{m}m"] / df["offer_price"] - 1
        df[f"ret_d1close_{m}m"] = df[f"price_{m}m"] / df["day1_close"] - 1
    return df


def summarize(df):
    out = {}
    for m in (1, 6, 12):
        d1 = df[f"ret_d1close_{m}m"].dropna()
        out[m] = {
            "median_from_offer": df[f"ret_offer_{m}m"].median(),
            "median_from_d1close": d1.median(),
            "pct_negative_from_d1close": (d1 < 0).mean(),
            "n": len(d1),
        }
    return out


def comparables_analysis():
    df = pd.read_csv(os.path.join(DATA, "mega_ipo_comparables.csv"), parse_dates=["ipo_date"])
    df = add_returns(df)

    sub = df.dropna(subset=["day1_pop", "ret_d1close_6m"])
    rho, pval = stats.spearmanr(sub["day1_pop"], sub["ret_d1close_6m"])

    summary = summarize(df)
    # Sensitivity A: exclude approx-quality rows
    solid = summarize(df[~df["quality"].str.startswith("approx")])
    # Sensitivity B: auditor's disputed RIVN 1m price ($93 instead of $109.70)
    df_rivn = df.copy()
    df_rivn.loc[df_rivn["ticker"] == "RIVN", "price_1m"] = 93.0
    rivn93 = summarize(add_returns(df_rivn.drop(columns=[c for c in df_rivn if c.startswith("ret_") or c == "day1_pop"])))

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    x = np.arange(len(df))
    axes[0].bar(x - 0.2, df["ret_d1close_6m"] * 100, width=0.4, label="6m from day-1 close")
    axes[0].bar(x + 0.2, df["ret_d1close_12m"] * 100, width=0.4, label="12m from day-1 close")
    axes[0].set_xticks(x, df["ticker"], rotation=45)
    axes[0].axhline(0, color="k", lw=0.8)
    axes[0].set_ylabel("return %")
    axes[0].set_title("Mega-IPO returns for a buyer at the first-day close")
    axes[0].legend()
    axes[0].grid(alpha=0.3, axis="y")

    axes[1].scatter(sub["day1_pop"] * 100, sub["ret_d1close_6m"] * 100, s=70)
    for _, r in sub.iterrows():
        axes[1].annotate(r["ticker"], (r["day1_pop"] * 100, r["ret_d1close_6m"] * 100),
                         fontsize=8, xytext=(4, 4), textcoords="offset points")
    axes[1].axhline(0, color="k", lw=0.8)
    axes[1].set_xlabel("first-day pop %")
    axes[1].set_ylabel("6m return from day-1 close %")
    axes[1].set_title(f"Pop vs 6m return: ρ = {rho:.2f}, p = {pval:.2f} (NOT significant)")
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "comparables.png"), dpi=130)
    plt.close(fig)

    return {"summary": summary, "solid": solid, "rivn93": rivn93,
            "rho": rho, "pval": pval, "n_corr": len(sub)}


def fmt_block(title, s):
    lines = [f"### {title}"]
    for m, v in s.items():
        lines.append(
            f"- {m}m: median from offer **{v['median_from_offer']:+.1%}**, "
            f"from day-1 close **{v['median_from_d1close']:+.1%}**, "
            f"negative from day-1 close in **{v['pct_negative_from_d1close']:.0%}** of {v['n']} cases"
        )
    return lines


def main():
    pm = private_marks_analysis()
    cmp_ = comparables_analysis()

    lines = ["# SPCX backtest results (post-audit)", ""]
    lines += [
        "## Private-market price trend (real pre-IPO marks, split-adjusted)",
        f"- Marks used: {pm['n_marks']} dated points, {pm['span']}",
        f"- First mark: {pm['first_mark']}; last mark before IPO: {pm['last_mark']}",
        f"- Realized CAGR of marks: **{pm['realized_cagr']:.1%}/yr** "
        f"(trend fit {pm['trend_cagr']:.1%}/yr; reflects an IPO-prep cycle, NOT a forward projection)",
        f"- Return of marks over the final two years: **{pm['two_yr_lo']:.0%} to {pm['two_yr_hi']:.0%}** depending on anchor",
        f"- IPO $135 vs trend at IPO date: **{pm['ipo_vs_trend']:+.1%}** "
        f"(excl. Nov-25 outlier: **{pm['ipo_vs_trend_noout']:+.1%}**); "
        f"vs last Forge mark: **{pm['ipo_vs_last_mark']:+.1%}**",
        "- H1 verdict: the offer was priced AT-TO-SLIGHTLY-ABOVE the private market — "
        "**no discount cushion exists**. Original 'priced below private marks' framing is rejected.",
        "- Caveat: marks before ~Feb 2026 price SpaceX standalone; later marks price SpaceX+xAI. "
        "Single-trend fit across the merger is directional only.",
        "",
        "## Mega-IPO reference class (H2)",
    ]
    lines += fmt_block("All rows (n=12; COIN excluded from offer-based stats)", cmp_["summary"])
    lines += fmt_block("Sensitivity A — verified/training-quality rows only", cmp_["solid"])
    lines += fmt_block("Sensitivity B — RIVN 1m at auditor's $93", cmp_["rivn93"])
    lines += [
        "",
        f"- First-day pop vs 6m return from day-1 close: Spearman ρ = **{cmp_['rho']:.2f}**, "
        f"p = **{cmp_['pval']:.2f}** (n={cmp_['n_corr']}) — **statistically indistinguishable from zero**. "
        "Pop size does not predict subsequent returns in this sample; only the unconditional "
        "medians carry information, and n is small (directional prior, not a significant edge).",
        "",
        "Charts: `charts/private_marks.png`, `charts/comparables.png`",
    ]

    with open(os.path.join(HERE, "results.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
