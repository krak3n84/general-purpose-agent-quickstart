#!/usr/bin/env python3
"""SPCX (SpaceX) IPO backtest.

SpaceX listed on NASDAQ as SPCX on 2026-06-12, so there is no two-year
exchange price history to backtest directly. Instead this script tests the
hypothesis against the two real datasets that DO exist:

  1. data/spacex_private_marks.csv — every verifiable pre-IPO per-share mark
     (insider tender offers, secondary-market marks, fund NAV marks) from
     2023-2026, used to establish the private-market price trend and where
     the $135 IPO price sits relative to it.

  2. data/mega_ipo_comparables.csv — the reference class of the largest /
     most-hyped US IPOs, used to backtest how stocks like this behave after
     listing (returns from offer price and from first-day close at 1m/6m/12m,
     and whether the first-day pop predicts subsequent returns).

Hypothesis under test (formed from known data, see report.md):
  H1: SpaceX private-market marks compounded at a high rate into the IPO and
      the $135 offer was priced BELOW the last private marks (a deliberate
      discount), implying near-term support.
  H2: For the mega-IPO reference class, buying at the FIRST-DAY CLOSE (what a
      public buyer can actually do) has historically produced poor median
      6-12 month returns relative to buying at the offer, and larger
      first-day pops predict worse subsequent returns.

Run: python3 backtest.py
Outputs: results.md, charts/*.png
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
CHARTS = os.path.join(HERE, "charts")
os.makedirs(CHARTS, exist_ok=True)

IPO_PRICE = 135.0
IPO_DATE = pd.Timestamp("2026-06-12")


def cagr(p0, p1, years):
    return (p1 / p0) ** (1 / years) - 1 if years > 0 else np.nan


def private_marks_analysis():
    df = pd.read_csv(os.path.join(DATA, "spacex_private_marks.csv"), parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Trend fit on log price vs time
    t_years = (df["date"] - df["date"].min()).dt.days / 365.25
    coeffs = np.polyfit(t_years, np.log(df["price_per_share"]), 1)
    trend_cagr = np.exp(coeffs[0]) - 1

    first, last = df.iloc[0], df.iloc[-1]
    years_span = (last["date"] - first["date"]).days / 365.25
    realized_cagr = cagr(first["price_per_share"], last["price_per_share"], years_span)

    # Where does $135 sit vs the trend extrapolated to IPO date?
    t_ipo = (IPO_DATE - df["date"].min()).days / 365.25
    trend_at_ipo = np.exp(np.polyval(coeffs, t_ipo))
    ipo_vs_trend = IPO_PRICE / trend_at_ipo - 1
    ipo_vs_last_mark = IPO_PRICE / last["price_per_share"] - 1

    # 2-year window stats (the "last two years" the user asked about)
    two_yr = df[df["date"] >= IPO_DATE - pd.DateOffset(years=2)]
    two_yr_ret = (
        two_yr.iloc[-1]["price_per_share"] / two_yr.iloc[0]["price_per_share"] - 1
        if len(two_yr) >= 2
        else np.nan
    )

    fig, ax = plt.subplots(figsize=(11, 6))
    for ev, g in df.groupby("event_type"):
        ax.scatter(g["date"], g["price_per_share"], label=ev, s=60, zorder=3)
    span = pd.date_range(df["date"].min(), IPO_DATE, freq="ME")
    tt = (span - df["date"].min()).days / 365.25
    ax.plot(span, np.exp(np.polyval(coeffs, tt)), "k--", alpha=0.6,
            label=f"log-linear trend ({trend_cagr:.0%}/yr)")
    ax.scatter([IPO_DATE], [IPO_PRICE], marker="*", s=400, color="red", zorder=4,
               label=f"IPO price ${IPO_PRICE:.0f}")
    ax.set_yscale("log")
    ax.set_ylabel("$/share (log scale)")
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
        "last_mark": f"${last['price_per_share']:.2f} ({last['date'].date()})",
        "realized_cagr": realized_cagr,
        "trend_cagr": trend_cagr,
        "trend_at_ipo": trend_at_ipo,
        "ipo_vs_trend": ipo_vs_trend,
        "ipo_vs_last_mark": ipo_vs_last_mark,
        "two_year_return_of_marks": two_yr_ret,
        "df": df,
    }


def comparables_analysis():
    df = pd.read_csv(os.path.join(DATA, "mega_ipo_comparables.csv"), parse_dates=["ipo_date"])

    df["day1_pop"] = df["day1_close"] / df["offer_price"] - 1
    for m in (1, 6, 12):
        df[f"ret_offer_{m}m"] = df[f"price_{m}m"] / df["offer_price"] - 1
        df[f"ret_d1close_{m}m"] = df[f"price_{m}m"] / df["day1_close"] - 1

    # Does the size of the first-day pop predict 6m return from day-1 close?
    sub = df.dropna(subset=["day1_pop", "ret_d1close_6m"])
    corr = sub["day1_pop"].corr(sub["ret_d1close_6m"], method="spearman")

    summary = {}
    for m in (1, 6, 12):
        summary[m] = {
            "median_from_offer": df[f"ret_offer_{m}m"].median(),
            "median_from_d1close": df[f"ret_d1close_{m}m"].median(),
            "pct_negative_from_d1close": (df[f"ret_d1close_{m}m"] < 0).mean(),
        }

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
    axes[1].set_title(f"Pop vs 6m return (Spearman ρ = {corr:.2f})")
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "comparables.png"), dpi=130)
    plt.close(fig)

    return {"df": df, "summary": summary, "pop_vs_6m_spearman": corr}


def main():
    pm = private_marks_analysis()
    cmp_ = comparables_analysis()

    lines = ["# SPCX backtest results", ""]
    lines += [
        "## Private-market price trend (real pre-IPO marks)",
        f"- Marks used: {pm['n_marks']} dated points, {pm['span']}",
        f"- First mark: {pm['first_mark']}; last mark before IPO: {pm['last_mark']}",
        f"- Realized CAGR of marks: **{pm['realized_cagr']:.1%}/yr**; "
        f"log-linear trend CAGR: **{pm['trend_cagr']:.1%}/yr**",
        f"- Return of marks over the final two years: **{pm['two_year_return_of_marks']:.1%}**",
        f"- Trend extrapolated to IPO date: ${pm['trend_at_ipo']:.0f}/share; "
        f"IPO priced at $135 → **{pm['ipo_vs_trend']:+.1%} vs trend**, "
        f"**{pm['ipo_vs_last_mark']:+.1%} vs last private mark** (H1 test)",
        "",
        "## Mega-IPO reference class (H2 test)",
    ]
    for m, s in cmp_["summary"].items():
        lines.append(
            f"- {m}m: median return from offer **{s['median_from_offer']:+.1%}**, "
            f"from day-1 close **{s['median_from_d1close']:+.1%}**, "
            f"negative from day-1 close in **{s['pct_negative_from_d1close']:.0%}** of cases"
        )
    lines += [
        f"- Spearman correlation, first-day pop vs 6m return from day-1 close: "
        f"**{cmp_['pop_vs_6m_spearman']:.2f}**",
        "",
        "Charts: `charts/private_marks.png`, `charts/comparables.png`",
    ]

    out = os.path.join(HERE, "results.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
