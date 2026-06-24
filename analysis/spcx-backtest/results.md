# SPCX backtest results (post-audit)

## Private-market price trend (real pre-IPO marks, split-adjusted)
- Marks used: 17 dated points, 2023-12-12 → 2026-06-11
- First mark: $19.40 (2023-12-12); last mark before IPO: $128.84 (2026-06-11)
- Realized CAGR of marks: **113.5%/yr** (trend fit 118.9%/yr; reflects an IPO-prep cycle, NOT a forward projection)
- Return of marks over the final two years: **181% to 475%** depending on anchor
- IPO $135 vs trend at IPO date: **+18.0%** (excl. Nov-25 outlier: **+12.4%**); vs last Forge mark: **+4.8%**
- H1 verdict: the offer was priced AT-TO-SLIGHTLY-ABOVE the private market — **no discount cushion exists**. Original 'priced below private marks' framing is rejected.
- Caveat: marks before ~Feb 2026 price SpaceX standalone; later marks price SpaceX+xAI. Single-trend fit across the merger is directional only.

## Mega-IPO reference class (H2)
### All rows (n=12; COIN excluded from offer-based stats)
- 1m: median from offer **+30.4%**, from day-1 close **-3.5%**, negative from day-1 close in **58%** of 12 cases
- 6m: median from offer **+24.3%**, from day-1 close **-17.2%**, negative from day-1 close in **67%** of 12 cases
- 12m: median from offer **-4.8%**, from day-1 close **-27.6%**, negative from day-1 close in **75%** of 8 cases
### Sensitivity A — verified/training-quality rows only
- 1m: median from offer **+35.5%**, from day-1 close **-5.5%**, negative from day-1 close in **67%** of 9 cases
- 6m: median from offer **-5.3%**, from day-1 close **-24.5%**, negative from day-1 close in **78%** of 9 cases
- 12m: median from offer **-17.4%**, from day-1 close **-31.0%**, negative from day-1 close in **71%** of 7 cases
### Sensitivity B — RIVN 1m at auditor's $93
- 1m: median from offer **+19.2%**, from day-1 close **-6.6%**, negative from day-1 close in **67%** of 12 cases
- 6m: median from offer **+24.3%**, from day-1 close **-17.2%**, negative from day-1 close in **67%** of 12 cases
- 12m: median from offer **-4.8%**, from day-1 close **-27.6%**, negative from day-1 close in **75%** of 8 cases

- First-day pop vs 6m return from day-1 close: Spearman ρ = **-0.15**, p = **0.67** (n=11) — **statistically indistinguishable from zero**. Pop size does not predict subsequent returns in this sample; only the unconditional medians carry information, and n is small (directional prior, not a significant edge).

Charts: `charts/private_marks.png`, `charts/comparables.png`
