# SPCX (SpaceX) Deep Research & Backtest — June 12, 2026

## 0. The most important fact

**SPCX has no two-year price history.** SPCX is Space Exploration Technologies Corp. (SpaceX),
which priced its IPO on **June 11, 2026 at a fixed $135/share** (no bookbuild range ever existed)
and began trading on Nasdaq **today, June 12, 2026**. It sold 555,555,555 Class A shares for
**$75.0B gross** — the largest IPO in history — at an implied valuation of **~$1.77T**
(~13.1B shares post the May 4, 2026 5-for-1 split). As of the latest indexed coverage there is
no confirmed first trade; crypto perpetual futures implied a +22–36% open ($165–$183).

Per the task instruction ("form a hypothesis from known data"), the hypothesis was formed and
backtested against the two real datasets that DO exist:
1. **Two years of real pre-IPO per-share marks** — insider tender offers, Forge/NPM secondary
   prices, company FMV (17 dated, sourced points, split-adjusted).
2. **The mega-IPO reference class** — 12 of the largest/most-hyped US listings, 2008–2025.

## 1. Verified IPO facts

| Item | Value |
|---|---|
| Offer price | $135.00, fixed take-it-or-leave-it (S-1/A June 3; locked June 11) |
| Shares / raise | 555,555,555 Class A / $75.0B gross ($74.4B net) |
| Greenshoe | 83.3M shares, 30 days (~$11.25B; $85.7B net if exercised) |
| Valuation | ~$1.77T (~13.1B shares post-split) |
| Free float | **~4.3%** (4.9% with greenshoe) — far below the 10% S&P 500 minimum |
| Retail allocation | ~30% of the deal (vs typical 5–10%) |
| Lockups | Staggered: 20% of insider shares ~2 days after Q2 earnings (late July); **+10% early if stock holds ≥30% above $135 ($175.50) for 5 of 10 sessions**; 7% tranches to day 135; 28% after Q3 earnings; rest at 180 days. Musk (~42% equity, ~85% voting power): 366 days |
| Oversubscription | 3.3x (earlier report ~2x — conflict flagged) |
| Demand signals | Crypto perps $165→$183 (+22–36%); Oppenheimer Outperform $190; Polymarket ~even odds on a 22% pop |

The "22% cryptocurrency premium" in some headlines = pre-IPO SPCX perpetual futures on crypto
exchanges trading ~$165 vs the $135 offer. Holders own no shares; it is a sentiment gauge only.

## 2. The two years of known data (in lieu of price history)

**Private marks (split-adjusted to post-split $/share):** Dec 2023 tender $19.40 ($180B) →
Jun 2024 tender $22.40 ($210B) → Dec 2024 tender $37.00 ($350B) → Jul 2025 tender $42.40 ($400B)
→ Dec 2025 tender $84.20 ($800B) → Forge Apr 2026 ~$121 → Forge Jun 11, 2026 **$128.84**.
Full series: `data/spacex_private_marks.csv`.

**Corporate events:** 5-for-1 split May 4, 2026; **xAI acquired in an all-stock merger
(~Jan–Feb 2026, $1.25T combined)** — SPCX is now a space + Starlink + AI conglomerate, and marks
before/after the merger price different companies.

**Fundamentals (audited S-1):** 2025 revenue **$18.67B (+33%)**, net loss **$4.9B**; Starlink =
61% of revenue and effectively all EBITDA ($7.17B, 63% margin); launch EBITDA just $653M;
xAI operating loss **$6.36B**. **Q1 2026 growth decelerated to +15% YoY**; Starlink ARPU fell
$99 → $66/mo while subscribers doubled yearly to >10M. ~20% of revenue is US government.
At $1.77T the stock trades at **~94x trailing sales** (Nvidia ~23x trailing with faster growth;
Palantir ~67x is the highest in the S&P 500). Analyst consensus 12m target **$139.33**
(Morningstar fair value $780B ≈ $60; Oppenheimer $190).

## 3. The hypothesis (formed from the data above)

> **H: $135 is roughly full price — the offer sits at a slight premium to SpaceX's own private
> market (+4.8% vs the last Forge mark, +12–18% above the 2-year trend of marks) and at ~94x
> sales with decelerating growth. The expected large first-day pop is froth: in the mega-IPO
> reference class, a buyer at the first-day close suffered median returns of roughly −4% (1m),
> −17% (6m), −28% (12m), negative in ~60–75% of cases. Therefore: do not chase the pop; the
> probability-weighted edge is to wait — the first supply catalyst is the late-July lockup wave.**

## 4. Backtest results (post-audit; full numbers in `results.md`)

- **Pricing vs private market:** $135 = **+4.8%** above the final Forge mark ($128.84, Jun 11),
  **+12.4% to +18.0%** above the fitted 2-year trend (with/without the Nov-25 outlier). The
  original idea that IPOs price at a discount to private marks is **rejected** for SPCX — there
  is no discount cushion. Marks compounded ~113%/yr over 2.5 years (+181% to +475% over the
  final two years depending on anchor) — an extraordinary run INTO the IPO.
- **Reference class (n=12; COIN direct listing excluded from offer-based stats):** buyer at
  first-day close: median **−3.5% (1m), −17.2% (6m), −27.6% (12m)**; negative in 58%/67%/75% of
  cases. Restricting to verified/training-quality rows makes it *worse* (−24.5% at 6m, −31.0% at
  12m). Buying at the *offer* was fine at 1–6m (medians +19% to +35%) — but the public cannot
  buy at the offer.
- **Crucial nuance:** pop size does **not** predict subsequent return (Spearman ρ = −0.15,
  p = 0.67). The medians are a base rate, not a timing signal, and n is small.

## 5. Adversarial round — how the agents challenged the findings

Two independent challenger agents attacked the work; material findings and resolutions:

| Challenge | Resolution |
|---|---|
| **Fatal:** headline "implied valuations" (Forge $1.03T Apr-26 vs $1.51T May-26) imply share counts differing by ~3.4B, only ~0.6B explained by xAI merger | Accepted — inconsistent valuation bases dropped from dataset; analysis uses transaction prices only |
| **Fatal:** H1 docstring said "priced below private marks" while data shows +4.8% above | Accepted — H1 reframed; verdict inverted to "no discount cushion" |
| COIN's $250 "offer" was a non-buyable reference price | Accepted — excluded from offer-based stats |
| RIVN 1m price: auditor claimed ~$93, original $109.70 (pre- vs post-earnings Dec 2021) | Disputed between agents — both run as sensitivities; conclusions unchanged |
| CRCL 1m $200 unsourced; approx rows mixed into medians | Accepted — re-flagged; quality-filtered sensitivity added (results got MORE bearish) |
| ρ = −0.09 reported without significance | Accepted — p-value added; mechanism claim withdrawn |
| 475% "two-year return" anchored at a trough | Accepted — reported as 181%–475% range |
| **Thesis-breaking risk (red team):** 4.3% float + ~30% retail + likely fast-track index inclusion (July) could force tens of billions of passive buying against a float of the same order — a 60–90 day squeeze window where fading the pop is lethal (cf. TSLA Dec-2020 inclusion +60%; CRCL +140% in month 1; SNOW ground higher for months) | Accepted as a mandatory modification — see final verdict |
| Reference class is heterogeneous, n=12; only directional | Accepted — claims downgraded to base-rate prior |
| Macro (Iran de-escalation rally on a hot-CPI tape, gold $4,200) cuts both ways | Noted — debut window is sentiment-driven and fragile |

## 6. Final verdict (hypothesis, as modified by the adversarial round)

1. **$135 is full price, not a bargain:** priced slightly above the private market, ~94x sales,
   growth decelerating, consensus target ($139) at par. Every dollar of day-one pop is paid to
   the most informed sellers' reference class.
2. **Don't chase the pop — but don't short it either.** The 6–12 month base rate from the
   first-day close is clearly negative (median −17% to −31%, two-thirds-plus of cases negative),
   but pop size has no predictive power (p≈0.7) and the 4.3% float + index-inclusion mechanics
   create a real 1–3 month squeeze scenario. The two closest structural analogs (CRCL, SNOW)
   both ran for months before fading.
3. **The calendar is the catalyst map:** ~$175.50 held for 5 of 10 sessions = +10% early insider
   unlock (a structural rally cap); late-July Q2 earnings + 2 days = first 20% unlock wave —
   also the first test of the Q1-2026 growth-deceleration narrative; day 135 and 180 unlocks
   follow. Supply arrives in waves against a tiny float in both directions.
4. **Fastest falsifiers:** S&P/Nasdaq-100 fast-track inclusion announcement; the $175 unlock
   trigger firing; Q2 Starlink re-acceleration; CRCL's 12m print turning clearly positive.

## 7. Data quality & limitations

- No SPCX exchange prices exist yet; first-day open/close were unconfirmed at write-up time.
- Private marks are thin, irregular, and straddle the xAI merger (regime change mid-series).
- Comparables n=12 (n=8 at 12m); several rows flagged `approx`; 2025 cohort lacks 12m data.
  Findings are directional base rates, not statistically significant estimates.
- Sub-agent budget was exhausted mid-research (org spend limit); Dec-2023 tender and parts of
  the comparables rely on training data rather than fresh web verification, as flagged in CSVs.
- This is research, not investment advice.

## 8. Key sources

- IPO terms: [CNBC](https://www.cnbc.com/2026/06/11/spacex-raises-75-billion-in-record-setting-ipo-ahead-of-nasdaq-debut.html) · [TechCrunch](https://techcrunch.com/2026/06/11/spacex-officially-prices-shares-at-135-in-the-largest-ipo-ever/) · [NBC](https://www.nbcnews.com/business/business-news/spacex-ipo-trading-price-rcna349225) · [SEC S-1](https://www.sec.gov/Archives/edgar/data/1181412/000162828026036936/spaceexplorationtechnologi.htm) · [SpaceNews](https://spacenews.com/spacex-to-raise-at-least-75-billion-in-ipo/)
- Lockups/float: [CNBC](https://www.cnbc.com/2026/05/21/spacex-insiders-will-get-to-sell-shares-earlier-than-usual-after-the-ipo.html) · [Motley Fool](https://www.fool.com/investing/2026/06/11/spacex-lockup-period-what-you-need-to-know-about-p/)
- Tenders: [Bloomberg Jun-24](https://www.bloomberg.com/news/articles/2024-06-27/spacex-tender-offer-said-to-value-company-at-record-210-billion) · [CNBC Dec-24](https://www.cnbc.com/2024/12/11/spacex-valuation-surges-to-350-billion-as-company-buys-back-stock.html) · [SatNews Dec-25](https://news.satnews.com/2025/12/06/spacex-targets-800-billion-valuation-in-secondary-sale-eyes-2026-ipo/)
- Secondary marks: [Forge](https://forgeglobal.com/spacex_stock/) · [Forge Apr-26 update](https://forgeglobal.com/insights/private-market-updates/spacex-ipo-market-dynamics-april-2026/) · split: [Yahoo](https://finance.yahoo.com/markets/stocks/article/spacex-reportedly-issues-5-for-1-stock-split-as-ipo-timeline-accelerates-121128655.html)
- Fundamentals/valuation: [Mostly Metrics S-1 breakdown](https://www.mostlymetrics.com/p/spacex-ipo-s1-breakdown) · [CNBC Starlink](https://www.cnbc.com/2026/05/21/spacex-starlink-growth-profit-nasdaq-ipo.html) · [Morningstar bear case](https://www.morningstar.com/stocks/why-we-think-spacex-ipo-is-overvalued) · [Oppenheimer $190](https://finance.yahoo.com/markets/stocks/article/oppenheimer-slaps-outperform-rating-on-spacex-190-price-target-ahead-of-market-debut-163237327.html) · xAI merger: [Motley Fool](https://www.fool.com/investing/2026/02/22/what-you-need-to-know-about-the-spacex-xai-merger/)
- Crypto premium: [Benzinga](https://www.benzinga.com/markets/prediction-markets/26/06/53152727/crypto-perps-say-spacex-pops-22-on-launch-but-prediction-markets-disagree) · [CoinDesk](https://www.coindesk.com/markets/2026/06/12/spacex-s-crypto-traded-ipo-was-sharply-falling-it-now-points-upward-to-a-usd2-4-trillion-valuation)
- 2025 IPO comps: [Motley Fool CRCL](https://www.fool.com/investing/2025/12/22/down-nearly-70-from-its-high-is-circle-internet-gr/) · [Nasdaq FIG](https://www.nasdaq.com/articles/why-figma-stock-lost-31-january) · [InvestorPlace FIG](https://investorplace.com/dailylive/2026/02/why-figma-stock-crashed-81-the-ipo-mechanics-retail-never-saw-coming-2/)
