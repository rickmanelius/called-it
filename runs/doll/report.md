---
tool: called-it 1.0.0
run: doll
subject: "Bob Doll"
target_year: 2026
season_window: 2025-10-01 to 2026-01-31
evidence_window: 2026-01-01 to 2026-10-24
grader: "jev-1.14.0"
thresholds: {"yes": 0.7, "no": 0.3, "min_strength": 1.0}
inputs_sha256:
  sources: 2c3b384fadc9accb1d9cf9e459e568b6361a34e64779d5051e59cd08dfd35d76
  claims: 01be5dec26de6eaedd2bbaae3ce34a9bddc48a4ed06a992463a0dbaa0c87c4c8
  rubrics: 92492ca74f448087164468bfa75997957415a1ba236fab16f3e04a290107dcf6
  evidence: f25aca944ba3b435d769e6d2949998c044368b8ce576ec5ffc5a63cfa339a17d
  grades: 3a42d280998e1af82040f45eb0d060a9b864bc8d6b18922d02f6c31f2e94d45a
---

🎯 called-it v1.0.0 · Bob Doll · 2026 · graded 2026-10-24 · jev-1.14.0

# Bob Doll: 2026 predictions, graded

14 claims graded at three bars. Hit rate **21% strict**, **29% standard**, **36% lenient**. Generosity gap (lenient minus strict): **14 points**. Unresolved at the strict bar: 5.

| Bar | Met | Not met | Unresolved | Hit rate (all claims) | Hit rate (resolved only) |
|---|---:|---:|---:|---:|---:|
| Strict | 3 | 6 | 5 | 21% | 33% |
| Standard | 4 | 5 | 5 | 29% | 44% |
| Lenient | 5 | 3 | 6 | 36% | 62% |

## Ladder

| # | Claim | Author | Strict | Standard | Lenient | Best evidence |
|---|---|---|:---:|:---:|:---:|---|
| c9 | International stocks outperform the U.S. for the second year in a row (first time in 20 years). | Bob Doll | ✗ not met° | ✗ not met° | ○ unresolved° | T1 [iShares (ACWX, MSCI ACWI ex U.S. ETF fund page)](https://www.ishares.com/us/products/239594/ishares-msci-acwi-ex-us-etf) |
| c5 | Earnings growth falls short of consensus +14% | Bob Doll | ✗ not met° | ✗ not met° | ✗ not met° | T1 [FactSet Earnings Insight (January 9, 2026)](https://advantage.factset.com/hubfs/Website/Resources%20Section/Research%20Desk/Earnings%20Insight/EarningsInsight_010926.pdf) |
| c14 | losing at least 20-25 seats. | Bob Doll | ○ unresolved° | ○ unresolved° | ○ unresolved° | T2 [Reuters explainer (syndicated via Devdiscourse)](https://www.devdiscourse.com/article/international/3996004-explainer-what-you-need-to-know-about-the-2026-us-midterm-elections) |
| c2 | Inflation remains sticky and fails to make much if any progress toward the Fed’s 2% target. | Bob Doll | ✓ met° | ✓ met° | ✓ met° | T1 [BLS CPI, September 2026](https://www.bls.gov/news.release/cpi.nr0.htm) |
| c7 | Stocks fail to advance by a double-digit percentage for only the third time in 10 years. | Bob Doll | ✗ not met° | ✗ not met° | ✗ not met° | T1 [FRED (S&amp;P Dow Jones Indices), S&amp;P 500 daily close](https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd=2024-01-01&coed=2026-10-24) |
| c1 | Economic growth in the U.S. improves from approximately 2.0% to approximately 2.5% real GDP. | Bob Doll | ✗ not met° | ✗ not met° | ○ unresolved° | T1 [BEA](https://www.bea.gov/news/2026/gdp-third-estimate-industries-corporate-profits-state-gdp-and-state-personal-income-2nd) |
| c8 | Technology, communication services, and financials outperform materials, utilities, and consumer discretionar… | Bob Doll | ✗ not met° | ○ unresolved° | ✓ met° | T1 [State Street (XLK fund page)](https://www.ssga.com/us/en/intermediary/etfs/the-technology-select-sector-spdr-fund-xlk) |
| c4 | as credit spreads widen (i.e., a “coupon-ish” year) | Bob Doll | ✓ met° | ✓ met° | ✓ met° | T1 [FRED (ICE BofA), US Corporate Index Option-Adjusted Spread](https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLC0A0CM&cosd=2025-12-01&coed=2026-10-24) |
| c12 | Republicans retain control of the Senate | Bob Doll | ○ unresolved° | ○ unresolved° | ○ unresolved° | T2 [Reuters explainer (syndicated via Devdiscourse)](https://www.devdiscourse.com/article/international/3996004-explainer-what-you-need-to-know-about-the-2026-us-midterm-elections) |
| c6 | P/Es decline modestly, making it a tougher year to make money. | Bob Doll | ✓ met° | ✓ met° | ✓ met° | T1 [FactSet Earnings Insight (January 9, 2026)](https://advantage.factset.com/hubfs/Website/Resources%20Section/Research%20Desk/Earnings%20Insight/EarningsInsight_010926.pdf) |
| c10 | AI continues to be volatile/erratic creating another year of elevated volatility. | Bob Doll | ○ unresolved° | ✓ met° | ✓ met° | T1 [FRED (Cboe), VIX daily close](https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS&cosd=2025-12-01&coed=2026-10-24) |
| c3 | The 10-year Treasury yield trades primarily between high 3%s and mid 4%s | Bob Doll | ✗ not met° | ✗ not met° | ✗ not met° | T1 [FRED (Treasury H.15), 10-Year Treasury constant maturity, daily](https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10&cosd=2025-12-01&coed=2026-10-24) |
| c11 | Faith-based share of industry AUM increases for the 10th year in a row. | Bob Doll | ○ unresolved° | ○ unresolved° | ○ unresolved° | T2 [Morningstar (faith-based investing data blog)](https://www.morningstar.com/business/insights/blog/faith-based-investing-data) |
| c13 | but surrender the House | Bob Doll | ○ unresolved° | ○ unresolved° | ○ unresolved° | T2 [Reuters explainer (syndicated via Devdiscourse)](https://www.devdiscourse.com/article/international/3996004-explainer-what-you-need-to-know-about-the-2026-us-midterm-elections) |

° provisional: the claim's horizon is after 2026-10-24, so this is the standing as of the run date, not a final grade.

## Claims

### c9. International stocks outperform the U.S. for the second year in a row (first time in 20 years).

> International stocks outperform the U.S. for the second year in a row (first time in 20 years).

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/)

Context: Prediction 7 of 10. A broad international index (MSCI ACWI ex-US or EAFE) beats the S&P 500 over calendar 2026.

- **Strict: ✗ not met** · P(met) 0.04, P(contradicted) 0.92, strength 1.70. International stocks outperform US stocks in 2026, measured by the broadest international index.
- **Standard: ✗ not met** · P(met) 0.05, P(contradicted) 0.94, strength 1.90. International stocks outperform US stocks in 2026.
- **Lenient: ○ unresolved** · P(met) 0.67, P(contradicted) 0.05, strength 1.74. International stocks, by at least one broad measure, outperform US stocks in 2026. (grader is uncertain)

Evidence:
- T1 contradicts [strict, standard] · 2026-10-22 · [iShares (ACWX, MSCI ACWI ex U.S. ETF fund page)](https://www.ishares.com/us/products/239594/ishares-msci-acwi-ex-us-etf): "NAV Total Return, YTD: Increase 10.86%, as of Oct 22, 2026 [SPY total return YTD on the same date: 12.68% per Yahoo Finance trailing returns]"
- T1 contradicts [standard] · 2026-10-22 · [iShares (EFA, MSCI EAFE ETF fund page)](https://www.ishares.com/us/products/239623/ishares-msci-eafe-etf): "NAV Total Return, YTD: Increase 9.23%, as of Oct 22, 2026"
- T1 supports [lenient] · 2026-10-22 · [iShares (EEM, MSCI Emerging Markets ETF fund page)](https://www.ishares.com/us/products/239637/ishares-msci-emerging-markets-etf): "NAV Total Return, YTD: Increase 13.22%, as of Oct 22, 2026 [against SPY 12.68% on the same date; Yahoo Finance's EEM page shows 13.38% in its overview and 22.77% in its trailing-returns table, so the EM figure is disput…"
- T4 supports · 2026-10-05 · [Bob Doll, Crossmark (4Q26 commentary)](https://www.crossmarkglobal.com/quarterly-investment-commentary-4q26/): "International stocks are ahead of U.S. stocks by about 150 bps, but the lead has changed several times. Certainly, EM stocks have helped the international averages. Oil price increases are more damaging to international…"

### c5. Earnings growth falls short of consensus +14%

> Earnings growth falls short of consensus +14%

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/)

Context: Prediction 4 of 10, first half. S&P 500 calendar-2026 earnings growth comes in below the roughly 14% consensus that stood at the start of the year.

- **Strict: ✗ not met** · P(met) 0.02, P(contradicted) 0.99, strength 1.78. S&P 500 earnings growth for 2026 falls short of the 14% consensus he cited, according to both major trackers.
- **Standard: ✗ not met** · P(met) 0.04, P(contradicted) 0.98, strength 1.72. S&P 500 earnings growth for 2026 falls short of the 14% consensus he cited.
- **Lenient: ✗ not met** · P(met) 0.06, P(contradicted) 0.98, strength 1.72. S&P 500 earnings growth for 2026 falls short of the consensus that stood when he made the prediction, by any margin.

Evidence:
- T1 neutral · 2025-12-19 · [FactSet Insight (December 19, 2025)](https://insight.factset.com/sp-500-cy-2026-earnings-preview-analysts-expect-earnings-growth-of-15): "The estimated (year-over-year) earnings growth rate for CY 2026 is 15.0%, which is above the trailing 10-year average (annual) earnings growth rate of 8.6% (2015 - 2024)."
- T1 neutral · 2026-01-09 · [FactSet Earnings Insight (January 9, 2026)](https://advantage.factset.com/hubfs/Website/Resources%20Section/Research%20Desk/Earnings%20Insight/EarningsInsight_010926.pdf): "For CY 2026, analysts are projecting earnings growth of 14.9% and revenue growth of 7.3%. [start-of-year consensus baseline]"
- T1 contradicts · 2026-10-16 · [FactSet Earnings Insight (October 16, 2026)](https://insight.factset.com/sp-500-earnings-season-update-october-16-2026): "For CY 2026, analysts are predicting (year-over-year) earnings growth of 32.8%."
- T2 neutral [strict] · 2026-10-13 · [CMC Markets citing LSEG I/B/E/S](https://www.cmcmarkets.com/en-sg/news-and-analysis/sp-500-earnings-ai-optimism-faces-the-test-of-higher-rates): "S&P 500 earnings are expected to grow 30.6% year on year in the third quarter of 2026 ... 28.5% in the fourth [no LSEG full-year CY2026 figure was found]"
- T4 contradicts · 2026-10-05 · [Bob Doll, Crossmark (4Q26 commentary)](https://www.crossmarkglobal.com/quarterly-investment-commentary-4q26/): "Earnings growth has been extraordinary, both in absolute terms and relative to expectations. Earnings growth has exceeded expectations by nearly 15%, stocks are up roughly 10%, and therefore the P/E of the market has fa…"

### c14. losing at least 20-25 seats.

> losing at least 20-25 seats.

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/) (split from c12)

Context: Prediction 10 of 10, third part, split from c12. Republicans' net House loss is at least 20 seats. 'At least 20-25' is itself a range; the bars settle it.

- **Strict: ○ unresolved** · P(met) 0.01, P(contradicted) 0.02, strength 0.97. Republicans lose at least 25 House seats, the top of the range he gave. (evidence is silent)
- **Standard: ○ unresolved** · P(met) 0.01, P(contradicted) 0.02, strength 1.00. Republicans lose at least 20 House seats, the floor he stated. (evidence is silent)
- **Lenient: ○ unresolved** · P(met) 0.01, P(contradicted) 0.03, strength 1.00. Republicans lose about 20 House seats, allowing a near miss of two. (evidence is silent)

Evidence:
- T2 neutral · 2026-10-22 · [Reuters explainer (syndicated via Devdiscourse)](https://www.devdiscourse.com/article/international/3996004-explainer-what-you-need-to-know-about-the-2026-us-midterm-elections): "ahead of the November 3, 2026, midterm elections ... Currently, Republicans hold a 218-214 majority in the House [the net seat change is not known until after November 3, 2026]"

### c2. Inflation remains sticky and fails to make much if any progress toward the Fed’s 2% target.

> Inflation remains sticky and fails to make much if any progress toward the Fed’s 2% target.

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/)

Context: Prediction 2 of 10. Core inflation (PCE or CPI) ends 2026 roughly where it started rather than converging toward 2%.

- **Strict: ✓ met** · P(met) 0.73, P(contradicted) 0.15, strength 1.95. Core inflation makes no meaningful progress toward 2% in 2026: the latest reading is at or above 2.6% and no more than 0.1 points below where it stood in December 2025.
- **Standard: ✓ met** · P(met) 0.89, P(contradicted) 0.06, strength 1.98. Core inflation in the latest 2026 reading is still at or above 2.5%, well short of the Fed's 2% target.
- **Lenient: ✓ met** · P(met) 0.65, P(contradicted) 0.14, strength 1.97. At no point in 2026 has core inflation fallen to 2.3% or below.

Evidence:
- T1 supports [strict] · 2026-02-20 · [BEA Personal Income and Outlays, December 2025](https://www.bea.gov/news/2026/personal-income-and-outlays-december-2025): "From the same month one year ago, the PCE price index for December increased 2.9 percent. ... Excluding food and energy, the PCE price index increased 3.0 percent from one year ago. [December 2025 baseline: core PCE 3.0…"
- T1 supports [lenient] · 2026-09-11 · [BLS CPI, August 2026](https://www.bls.gov/news.release/archives/cpi_09112026.htm): "Over the last 12 months, the all items index increased 3.4 percent before seasonal adjustment. The all items less food and energy index rose 2.4 percent over the year [the lowest core CPI 12-month reading of 2026; compu…"
- T1 supports · 2026-09-30 · [BEA Personal Income and Outlays, August 2026](https://www.bea.gov/news/2026/personal-income-and-outlays-august-2026): "From the same month one year ago, the PCE price index for August increased 3.4 percent. Excluding food and energy, the PCE price index increased 3.0 percent from one year ago."
- T1 supports [standard, lenient] · 2026-10-14 · [BLS CPI, September 2026](https://www.bls.gov/news.release/cpi.nr0.htm): "The all items index rose 3.7 percent for the 12 months ending September. The all items less food and energy index rose 2.6 percent over the year."
- T4 supports · 2026-10-05 · [Bob Doll, Crossmark (4Q26 commentary)](https://www.crossmarkglobal.com/quarterly-investment-commentary-4q26/): "Sadly, this one is nearly certain. Most year-over-year and year-to-date inflation measures have a 3-handle, with some over 4%."

### c7. Stocks fail to advance by a double-digit percentage for only the third time in 10 years.

> Stocks fail to advance by a double-digit percentage for only the third time in 10 years.

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/)

Context: Prediction 5 of 10. The S&P 500 gains less than 10% in calendar 2026 (price or total return; the bars say which).

- **Strict: ✗ not met** · P(met) 0.04, P(contradicted) 0.97, strength 1.97. Stocks fail to advance by a double-digit percentage in 2026, on both a price and a total-return basis.
- **Standard: ✗ not met** · P(met) 0.04, P(contradicted) 0.91, strength 1.26. Stocks fail to advance by a double-digit percentage in 2026.
- **Lenient: ✗ not met** · P(met) 0.16, P(contradicted) 0.92, strength 1.98. Stocks were short of a double-digit gain for 2026 at the latest close or at the end of the most recent completed quarter.

Evidence:
- T1 contradicts [lenient] · 2026-09-30 · [FRED (S&amp;P Dow Jones Indices), S&amp;P 500 daily close](https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd=2024-01-01&coed=2026-10-24): "2025-12-31,6845.50; 2026-06-30,7499.36; 2026-09-30,7651.54 [price return 2026 year to date: 9.55% at the end of Q2, 11.77% at the end of Q3]"
- T1 contradicts [strict, lenient] · 2026-09-30 · [State Street (SPY fund page)](https://www.ssga.com/us/en/intermediary/etfs/spdr-sp-500-etf-trust-spy): "YTD as of Sep 30 2026: NAV 12.65%, Market Value 12.66%, S&P 500 Index 12.75% [total return]"
- T2 contradicts [strict] · 2026-10-22 · [Yahoo Finance, SPY performance](https://finance.yahoo.com/quote/SPY/performance/): "Trailing returns as of 10/22/2026. Category is Large Blend. YTD: SPY 12.68% [the Performance Overview on the same page shows YTD Return 12.91%; total return]"
- T2 contradicts [strict, standard] · 2026-10-23 · [Yahoo Finance, S&amp;P 500 (^GSPC) historical closes](https://finance.yahoo.com/quote/%5EGSPC/history/): "Oct 23, 2026: 7,623.68; Oct 22, 2026: 7,663.43; Oct 21, 2026: 7,757.17 [price return 2026 year to date from the 2025-12-31 close of 6,845.50: 11.37% at the Oct 23 close]"
- T4 contradicts · 2026-10-05 · [Bob Doll, Crossmark (4Q26 commentary)](https://www.crossmarkglobal.com/quarterly-investment-commentary-4q26/): "The S&P 500 has advanced a bit over 10% so far this year. ... another double-digit stock market return is possible."

### c1. Economic growth in the U.S. improves from approximately 2.0% to approximately 2.5% real GDP.

> Economic growth in the U.S. improves from approximately 2.0% to approximately 2.5% real GDP.

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/)

Context: Prediction 1 of 10. Full-year 2026 real GDP growth of about 2.5%, up from about 2.0% in 2025. Final 2026 GDP is published in early 2027; quarterly readings exist through Q3 2026.

- **Strict: ✗ not met** · P(met) 0.04, P(contradicted) 0.73, strength 1.83. US real GDP growth for 2026 is approximately 2.5%, read as between 2.3% and 2.7%.
- **Standard: ✗ not met** · P(met) 0.19, P(contradicted) 0.70, strength 1.83. US real GDP growth for 2026 improves on 2025 and is at least 2.3%.
- **Lenient: ○ unresolved** · P(met) 0.51, P(contradicted) 0.44, strength 1.87. US real GDP growth for 2026 improves on 2025 by at least a quarter of a percentage point, half the improvement he predicted. (grader is uncertain)

Evidence:
- T1 neutral · 2026-09-30 · [BEA](https://www.bea.gov/news/2026/gdp-third-estimate-industries-corporate-profits-state-gdp-and-state-personal-income-2nd): "Real gross domestic product (GDP) increased at an annual rate of 2.2 percent in the second quarter of 2026. In the first quarter, real GDP increased 2.5 percent (revised)."
- T1 contradicts · 2026-09-30 · [FRED (BEA), Real GDP percent change from quarter one year ago](https://fred.stlouisfed.org/graph/fredgraph.csv?id=A191RO1Q156NBEA&cosd=2024-01-01&coed=2026-10-24): "2025-10-01,2.0; 2026-01-01,2.6; 2026-04-01,2.2 [the most recent reported quarter, Q2 2026, shows year-over-year real GDP growth of 2.2%; Q1 2026 was 2.6%]"
- T1 neutral · 2026-09-30 · [FRED (BEA), Real GDP annual percent change](https://fred.stlouisfed.org/graph/fredgraph.csv?id=A191RL1A225NBEA&cosd=2024-01-01&coed=2026-10-24): "2024-01-01,3.0; 2025-01-01,2.3 [2025 full-year real GDP growth is 2.3% after BEA's September 2026 annual update; the February 2026 advance release had said 'Real GDP increased 2.2 percent in 2025']"
- T1 neutral · 2026-10-24 · [BEA release schedule](https://www.bea.gov/news/schedule): "GDP (Advance Estimate), 3rd Quarter 2026: October 29, 8:30 AM; Personal Income and Outlays, September 2026: October 29, 8:30 AM [the Q3 2026 GDP figure is not yet published as of the run date]"
- T2 neutral [lenient] · 2026-10-15 · [Atlanta Fed GDPNow (via InvestingLive)](https://investinglive.com/central-banks/atlanta-fed-gdpnow-holds-at-3-6-for-q3-as-consumer-spending-outlook-improves/): "The GDPNow model estimate for real GDP growth (seasonally adjusted annual rate) in the third quarter of 2026 is 3.6 percent"
- T4 supports · 2026-10-05 · [Bob Doll, Crossmark (4Q26 commentary)](https://www.crossmarkglobal.com/quarterly-investment-commentary-4q26/): "Despite oil reaching $100 per barrel (which one might think could bring any economy to its knees), economic growth in the U.S. remains relatively robust on the back of a resilient consumer and significant capital expend…"

### c8. Technology, communication services, and financials outperform materials, utilities, and consumer discretionary.

> Technology, communication services, and financials outperform materials, utilities, and consumer discretionary.

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/)

Context: Prediction 6 of 10. Three favoured S&P 500 sectors beat three disfavoured ones over calendar 2026.

- **Strict: ✗ not met** · P(met) 0.04, P(contradicted) 0.96, strength 1.89. Technology, communication services and financials each outperform each of materials, utilities and consumer discretionary in 2026.
- **Standard: ○ unresolved** · P(met) 0.68, P(contradicted) 0.68, strength 1.97. Technology, communication services and financials outperform materials, utilities and consumer discretionary in 2026 as groups, with most of the individual comparisons also holding. (grader is uncertain)
- **Lenient: ✓ met** · P(met) 0.80, P(contradicted) 0.20, strength 1.97. Technology, communication services and financials outperform materials, utilities and consumer discretionary in 2026 as groups.

Evidence:
- T1 supports · 2026-09-30 · [State Street (XLK fund page)](https://www.ssga.com/us/en/intermediary/etfs/the-technology-select-sector-spdr-fund-xlk): "YTD as of Sep 30 2026: Fund NAV 39.47%, Fund Market Value 39.53%, Technology Select Sector Index 39.57%"
- T1 contradicts · 2026-09-30 · [State Street (XLC fund page)](https://www.ssga.com/us/en/intermediary/etfs/the-communication-services-select-sector-spdr-fund-xlc): "YTD as of Sep 30 2026: NAV -4.87%, Market Value -4.84%, Communication Services Select Sector Index -4.83% [below Materials (XLB 8.75%) but above Utilities (XLU -5.71%) and Consumer Discretionary (XLY -8.27%)]"
- T1 neutral · 2026-09-30 · [State Street (XLF fund page)](https://www.ssga.com/us/en/intermediary/etfs/the-financial-select-sector-spdr-fund-xlf): "YTD as of Sep 30 2026: NAV -1.35%, Market Value -1.34%, Financial Select Sector Index -1.30% [below Materials (XLB 8.75%) but above Utilities (XLU -5.71%) and Consumer Discretionary (XLY -8.27%)]"
- T1 neutral · 2026-09-30 · [State Street (XLB fund page)](https://www.ssga.com/us/en/intermediary/etfs/the-materials-select-sector-spdr-fund-xlb): "YTD as of Sep 30 2026: NAV 8.75%, Market Value 8.76%, Materials Select Sector Index 8.84%"
- T1 supports · 2026-09-30 · [State Street (XLU fund page)](https://www.ssga.com/us/en/intermediary/etfs/the-utilities-select-sector-spdr-fund-xlu): "YTD as of Sep 30 2026: Fund NAV -5.71%, Fund Market Value -5.73%, Utilities Select Sector Index -5.65%"
- T1 supports · 2026-09-30 · [State Street (XLY fund page)](https://www.ssga.com/us/en/intermediary/etfs/the-consumer-discretionary-select-sector-spdr-fund-xly): "YTD as of Sep 30 2026: NAV -8.27%, Market Value -8.26%, Consumer Discretionary Select Sector Index -8.25% [equal-weighted average of XLK, XLC, XLF at Sep 30: 11.08%; of XLB, XLU, XLY: -1.74%]"
- T2 supports [standard, lenient] · 2026-10-23 · [ChartRow sector ETF tracker (total return, dividends reinvested)](https://chartrow.com/sp500/sector-performance): "YTD total return as of market close, October 23, 2026: XLK +27.7%, XLC -9.6%, XLF +3.3%, XLB +14.6%, XLU +1.8%, XLY -4.7%, XLE +58.1% [equal-weighted average of XLK, XLC, XLF: 7.1%; of XLB, XLU, XLY: 3.9%; XLC and XLF e…"
- T4 contradicts · 2026-04-06 · [Bob Doll, Crossmark (2Q26 commentary)](https://www.crossmarkglobal.com/wp-content/uploads/10-Predictions-2Q26-Quarterly-Commentary_FINAL.pdf): "Well, in the category of 'You can't win 'em all,' this prediction is headed in a very bad direction. ... financials have been the worst sector performer so far this year. Meanwhile, materials has been a stellar performe…"
- T4 supports · 2026-10-05 · [Bob Doll, Crossmark (4Q26 commentary)](https://www.crossmarkglobal.com/quarterly-investment-commentary-4q26/): "This prediction looked hopeless on March 31. But, as of Sept. 30, our projected outperformers are leading our projected underperformers by approximately 1000 bps, thanks to strong performance from technology and a much-…"

### c4. as credit spreads widen (i.e., a “coupon-ish” year)

> as credit spreads widen (i.e., a “coupon-ish” year)

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/) (split from c3)

Context: Prediction 3 of 10, second half, split from c3. Corporate credit spreads (investment grade and high yield) end 2026 wider than they began.

- **Strict: ✓ met** · P(met) 0.95, P(contradicted) 0.09, strength 1.98. Credit spreads are clearly wider than at the start of 2026, in both investment grade and high yield.
- **Standard: ✓ met** · P(met) 0.94, P(contradicted) 0.02, strength 1.97. High-yield credit spreads are wider than at the start of 2026.
- **Lenient: ✓ met** · P(met) 0.99, P(contradicted) 0.01, strength 1.99. Credit spreads widened during 2026, either ending wider than they started or widening materially at some point in the year.

Evidence:
- T1 supports [strict, lenient] · 2026-10-22 · [FRED (ICE BofA), US Corporate Index Option-Adjusted Spread](https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLC0A0CM&cosd=2025-12-01&coed=2026-10-24): "2025-12-31,0.79; 2026-01-22,0.73; 2026-03-16,0.94; 2026-10-22,0.89 [investment-grade OAS is 10 bps wider at the latest reading than on 2025-12-31; 2026 low 0.73 on 2026-01-22, high 0.94 on 2026-03-16]"
- T1 supports · 2026-10-22 · [FRED (ICE BofA), US High Yield Index Option-Adjusted Spread](https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLH0A0HYM2&cosd=2025-12-01&coed=2026-10-24): "2025-12-31,2.81; 2026-03-30,3.46; 2026-08-28,2.60; 2026-10-22,3.40 [high-yield OAS is 59 bps wider at the latest reading than on 2025-12-31; the 2026 high of 3.46 on 2026-03-30 was 65 bps above the start-of-year level;…"
- T4 supports · 2026-10-05 · [Bob Doll, Crossmark (4Q26 commentary)](https://www.crossmarkglobal.com/quarterly-investment-commentary-4q26/): "We are starting to see some widening in credit spreads in low quality (e.g., CCC) paper, but most investment-grade spreads remain fairly tight. (Watch this space carefully.)"

### c12. Republicans retain control of the Senate

> Republicans retain control of the Senate

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/)

Context: Prediction 10 of 10, first part. Midterm elections are on 2026-11-03, after this run's evidence window, so the claim is open.

- **Strict: ○ unresolved** · P(met) 0.03, P(contradicted) 0.09, strength 1.02. Republicans retain control of the Senate in the November 3, 2026 midterm elections. (evidence is silent)
- **Standard: ○ unresolved** · P(met) 0.05, P(contradicted) 0.07, strength 1.02. Republicans retain control of the Senate in the November 3, 2026 midterm elections. (evidence is silent)
- **Lenient: ○ unresolved** · P(met) 0.06, P(contradicted) 0.06, strength 1.02. Republicans retain control of the Senate in the November 3, 2026 midterm elections. (evidence is silent)

Evidence:
- T2 neutral · 2026-10-22 · [Reuters explainer (syndicated via Devdiscourse)](https://www.devdiscourse.com/article/international/3996004-explainer-what-you-need-to-know-about-the-2026-us-midterm-elections): "ahead of the November 3, 2026, midterm elections ... Republicans hold a 53-47 majority ... must net four additional seats to get control [the Senate outcome is not known until after November 3, 2026]"

### c6. P/Es decline modestly, making it a tougher year to make money.

> P/Es decline modestly, making it a tougher year to make money.

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/) (split from c5)

Context: Prediction 4 of 10, second half, split from c5. The S&P 500 forward or trailing P/E ends 2026 modestly below where it started.

- **Strict: ✓ met** · P(met) 0.86, P(contradicted) 0.03, strength 1.88. The S&P 500's P/E declined modestly in 2026, read as at least half a point.
- **Standard: ✓ met** · P(met) 0.94, P(contradicted) 0.02, strength 1.90. The S&P 500's P/E declined in 2026, read as at least a quarter of a point.
- **Lenient: ✓ met** · P(met) 0.77, P(contradicted) 0.04, strength 1.88. The S&P 500's P/E did not expand in 2026: flat or lower than where it started.

Evidence:
- T1 neutral · 2026-01-09 · [FactSet Earnings Insight (January 9, 2026)](https://advantage.factset.com/hubfs/Website/Resources%20Section/Research%20Desk/Earnings%20Insight/EarningsInsight_010926.pdf): "The forward 12-month P/E ratio is 22.2, which is above the 5-year average (20.0) and above the 10-year average (18.7). [closest published FactSet reading to December 31, 2025; the December 19, 2025 edition read 21.8]"
- T1 supports · 2026-10-09 · [FactSet Earnings Insight (October 9, 2026)](https://advantage.factset.com/hubfs/Website/Resources%20Section/Research%20Desk/Earnings%20Insight/EarningsInsight_100926.pdf): "The forward 12-month P/E ratio for the S&P 500 is 19.1. This P/E ratio is below the 5-year average (19.8) but equal to the 10-year average (19.1)."
- T1 supports · 2026-10-16 · [FactSet Earnings Insight (October 16, 2026)](https://insight.factset.com/sp-500-earnings-season-update-october-16-2026): "The forward 12-month P/E ratio is 19.0, which is below the 5-year average (19.8) and below the 10-year average (19.1)."
- T4 supports · 2026-10-05 · [Bob Doll, Crossmark (4Q26 commentary)](https://www.crossmarkglobal.com/quarterly-investment-commentary-4q26/): "The bond yield increase has impacted stocks as the P/E ratio on the S&P 500 has moved down from 22x to 19x forward earnings (in other words, stocks are up, but much less than earnings)."

### c10. AI continues to be volatile/erratic creating another year of elevated volatility.

> AI continues to be volatile/erratic creating another year of elevated volatility.

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/)

Context: Prediction 8 of 10. Equity volatility in 2026 stays elevated relative to a calm year, with AI-related names the driver. 'Elevated' is undefined in the source.

- **Strict: ○ unresolved** · P(met) 0.10, P(contradicted) 0.44, strength 1.86. 2026 was a year of elevated equity volatility with AI as the driver: volatility ran above normal all year, spiked at least once, and a major market drawdown was laid at AI's door. (grader is uncertain)
- **Standard: ✓ met** · P(met) 0.98, P(contradicted) 0.01, strength 1.94. 2026 saw elevated equity volatility and at least one notable selloff attributed to AI stocks.
- **Lenient: ✓ met** · P(met) 0.89, P(contradicted) 0.02, strength 1.95. At least one widely reported market selloff in 2026 was attributed primarily to AI stocks.

Evidence:
- T1 neutral [strict] · 2026-06-10 · [FRED (S&amp;P Dow Jones Indices), S&amp;P 500 daily close](https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd=2024-01-01&coed=2026-10-24): "2026-06-02,7609.78; 2026-06-10,7266.99 [the S&P 500 fell 4.50% from its June 2 close to its June 10 close over the AI-stock sell-off the AP reported, short of a 5% drawdown; the year's largest drawdown was 9.10%, from t…"
- T1 supports [standard] · 2026-10-21 · [FRED (S&amp;P Dow Jones Indices), S&amp;P 500 daily close](https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd=2024-01-01&coed=2026-10-24): "2026-01-20,6796.86; 2026-03-31,6528.52; 2026-04-08,6782.81; 2026-06-05,7383.74 [computed from the daily series: four S&P 500 sessions in 2026 through 2026-10-21 moved 2% or more from the prior close: -2.06%, +2.91%, +2.…"
- T1 supports [strict, standard] · 2026-10-22 · [FRED (Cboe), VIX daily close](https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS&cosd=2025-12-01&coed=2026-10-24): "2025-12-31,14.95; 2026-03-27,31.05; 2026-03-30,30.61; 2026-09-22,14.21; 2026-10-22,19.03 [computed from the daily series: the VIX averaged 18.09 over its 209 closes in 2026 through 2026-10-22; highest close 31.05 on 202…"
- T2 supports [lenient] · 2026-02-06 · [AAP via CommBank Newsroom](https://www.commbank.com.au/articles/newsroom/2026/02/wall-street-ends-sharply-down-as-ai-worries-weigh.html): "Wall Street ended sharply lower on Thursday, with the Nasdaq dragged to its lowest since November by tech heavyweights ... The S&P 500 declined 1.23 per cent ... said it could double capital spending on AI"
- T2 supports [standard, lenient] · 2026-06-10 · [AP (Stan Choe), via Iron Mountain Daily News](https://www.ironmountaindailynews.com/news/business/2026/06/sell-off-for-ai-stocks-knocks-wall-street-back/): "Another sell-off for artificial-intelligence stocks helped drag the U.S. market sharply lower Wednesday ... The S&P 500 dropped 1.6% for its first back-to-back drop in three weeks ... Among the worries is that their pri…"
- T4 supports · 2026-10-05 · [Bob Doll, Crossmark (4Q26 commentary)](https://www.crossmarkglobal.com/quarterly-investment-commentary-4q26/): "The AI complex witnessed noticeable volatility with the SOX falling 11.4%. ... Our expectation remains that AI will be controversial, create confusion and volatility, and result in some amazing positive stories and some…"

### c3. The 10-year Treasury yield trades primarily between high 3%s and mid 4%s

> The 10-year Treasury yield trades primarily between high 3%s and mid 4%s

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/)

Context: Prediction 3 of 10, first half. The 10-year yield spends most of 2026 in roughly a 3.75% to 4.5% band. Some outlets paraphrase the band as 3.5% to 4.5%; the Crossmark deck (s2) wording governs.

- **Strict: ✗ not met** · P(met) 0.04, P(contradicted) 0.99, strength 1.99. The 10-year Treasury yield stayed between the high 3%s and the mid 4%s on every trading day of 2026.
- **Standard: ✗ not met** · P(met) 0.10, P(contradicted) 0.98, strength 1.99. The 10-year Treasury yield traded primarily between the high 3%s and the mid 4%s in 2026, read as at least 80% of trading days.
- **Lenient: ✗ not met** · P(met) 0.20, P(contradicted) 0.98, strength 1.98. The 10-year Treasury yield spent most of 2026 between the high 3%s and the mid 4%s and never strayed far outside that range.

Evidence:
- T1 contradicts · 2026-10-22 · [FRED (Treasury H.15), 10-Year Treasury constant maturity, daily](https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10&cosd=2025-12-01&coed=2026-10-24): "2025-12-31,4.18; 2026-02-27,3.97; 2026-05-18,4.61; 2026-09-16,5.01; 2026-09-30,5.29; 2026-10-05,5.31; 2026-10-22,4.96 [computed from the daily series: 134 of 203 closes in 2026 through 2026-10-22, or 66.0%, lie between…"
- T2 contradicts · 2026-10-06 · [Trading Economics](https://tradingeconomics.com/united-states/government-bond-yield/news/589866): "The yield on the 10-year US Treasury note was at 5.26% on Tuesday ... pausing a surge that peaked at a 24-year high of 5.33% touched yesterday"
- T4 neutral · 2026-07-06 · [Bob Doll, Crossmark (3Q26 commentary)](https://www.crossmarkglobal.com/wp-content/uploads/10-Predictions-3Q26-Quarterly-Commentary_FINAL.pdf): "While price action for the 10-year Treasury has been confined to the high 3%s and mid 4%s, the threat on the upside still exists, especially with significant debt issuance to come, and the inflation problem mentioned in…"
- T4 contradicts · 2026-10-05 · [Bob Doll, Crossmark (4Q26 commentary)](https://www.crossmarkglobal.com/quarterly-investment-commentary-4q26/): "Treasurys were weak (the 10-year yield rose from 4.38% at 6/30/26 to 5.26% at 9/30/26, reaching the highest level since 2002.) ... Treasury rates have improved topside in accelerating fashion toward the end of Q3. Some…"

### c11. Faith-based share of industry AUM increases for the 10th year in a row.

> Faith-based share of industry AUM increases for the 10th year in a row.

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/)

Context: Prediction 9 of 10. Faith-based or values-based funds grow as a share of total industry assets in 2026. Crossmark itself is a faith-based manager; data likely comes from Morningstar or industry bodies.

- **Strict: ○ unresolved** · P(met) 0.06, P(contradicted) 0.05, strength 1.18. Faith-based funds' share of US fund industry assets rose in 2026, per an independent data provider. (evidence is silent)
- **Standard: ○ unresolved** · P(met) 0.05, P(contradicted) 0.07, strength 1.17. Faith-based funds grew faster than the fund industry in 2026, per a reputable industry source. (evidence is silent)
- **Lenient: ○ unresolved** · P(met) 0.08, P(contradicted) 0.05, strength 1.25. Faith-based funds gained share or outgrew the industry in 2026, per any industry source that is not solely Crossmark. (evidence is silent)

Evidence:
- T2 neutral · 2026-04-30 · [Morningstar (faith-based investing data blog)](https://www.morningstar.com/business/insights/blog/faith-based-investing-data): "about 150 faith-based mutual funds and ETFs with nearly $97 billion in assets ... as of April 30, 2026 ... Total flows into religiously themed funds were positive for the year to date and over the trailing 1-, 3-, 5-, a…"
- T2 neutral · 2026-08-19 · [FaithInvest, summarising Morningstar&#x27;s Faith-Based Investing: Global Landscape report](https://www.faithinvest.org/post/morningstar-introduces-tags-for-christian-catholic-funds-maps-the-faith-based-investing-landscape): "roughly $169bn of assets under management (AUM) ... 853 active funds across the US, Middle East, Asia, and Europe ... as of April 30, 2026 ... Of these 853 funds, 650 were Shariah, 114 were nondenominational Christian,…"
- T4 neutral · 2026-10-05 · [Bob Doll, Crossmark (4Q26 commentary)](https://www.crossmarkglobal.com/quarterly-investment-commentary-4q26/): "The faith-based share of money management industry AUM has increased nine years in a row, granted from a very small base. We expect this to be the tenth year in a row making it a decade of more than doubling market shar…"

### c13. but surrender the House

> but surrender the House

Bob Doll, 2025-12-31, [Bob Doll&#x27;s 10 Predictions for 2026: High-Risk Bull Market](https://401kspecialistmag.com/bob-dolls-10-predictions-for-2026-high-risk-bull-market/) (split from c12)

Context: Prediction 10 of 10, second part, split from c12. Democrats win a House majority in the 2026 midterms (2026-11-03).

- **Strict: ○ unresolved** · P(met) 0.01, P(contradicted) 0.14, strength 1.01. Republicans surrender the House in the November 3, 2026 midterm elections. (evidence is silent)
- **Standard: ○ unresolved** · P(met) 0.01, P(contradicted) 0.20, strength 1.01. Republicans surrender the House in the November 3, 2026 midterm elections. (evidence is silent)
- **Lenient: ○ unresolved** · P(met) 0.01, P(contradicted) 0.18, strength 1.01. Republicans surrender the House in the November 3, 2026 midterm elections. (evidence is silent)

Evidence:
- T2 neutral · 2026-10-22 · [Reuters explainer (syndicated via Devdiscourse)](https://www.devdiscourse.com/article/international/3996004-explainer-what-you-need-to-know-about-the-2026-us-midterm-elections): "ahead of the November 3, 2026, midterm elections ... Currently, Republicans hold a 218-214 majority in the House ... win a net gain of four seats to win control [the House outcome is not known until after November 3, 20…"

<!-- PASS-THROUGH FOOTER -->
---
**called-it v1.0.0** · run `doll` · target year 2026 · season 2025-10-01 to 2026-01-31 · evidence 2026-01-01 to 2026-10-24
Grader: jev-1.14.0 (168 answers) · policy: met needs P(met) ≥ 0.7 and evidence strength ≥ 1.0; not met needs P(contradicted) ≥ 0.7; bars are nested, so a stricter bar met implies the looser ones met and a looser bar not met implies the stricter ones not met (1 cells implied)
Sources 6 (6 readable) · claims graded 14 · evidence items 57 (T1 31, T2 13, T3 0, T4 13, T5 0) · (claim, bar) pairs 42
Hit rate strict 21% · standard 29% · lenient 36% · generosity gap 14 points
---
<!-- END PASS-THROUGH FOOTER -->
