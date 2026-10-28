# Top five findings, with the figure for each

As of 2026-10-24, four subjects graded (Every, Scott Galloway, Mike Ippolito, Bob Doll), 71 claims, 213 cells. Each item names the figure in `article/figures/` and the run data behind it.

## 1. The grade depends on who is grading, and the size of that dependence is measurable

Figure: `generosity-gap.png` (and `hit-rates.png`).

Lenient minus strict hit rate: Bob Doll 14 points, Mike Ippolito 35, Scott Galloway 47, Every 50, in the order of how much of each list is numbers versus stories. Nobody publishes this number because nobody grades at more than one bar. It is the piece's headline because it reframes every "X got Y% of their predictions right" claim as a statement about the grader as much as the predictor.

## 2. The same list supports a 100% and a 17%, and both are honest

Figure: `resolved-vs-all.png`.

Every's 22 claims: at the lenient bar, every claim that could be resolved was met (12 of 12, 100%); at the strict bar, one of six (17%). Count unresolved claims against the author and the lenient rate is 55%. Three defensible conventions, three numbers from 17 to 100 for one list. Galloway spans 0% to 70%, Ippolito 15% to 82%, Doll 21% to 62%. The practical point: a year-end scorecard that does not say which convention it used is not reporting a number.

## 3. Numbers protect the reader, not the author

Figure: `numbers-vs-words.png`.

Pooled across all four subjects, the 22 claims with a number, date or threshold in them (classifier specificity 2.5 or higher, scored before any evidence) have a smaller generosity gap (23 points versus 45) and lower hit rates at the standard and lenient bars (14% and 32% versus 39% and 53%). We expected numbers to shrink the gap; they do. We did not expect them to lower the hit rate; they do that too, because a number is a bar written in advance and it makes a miss undeniable. Ippolito's two all-bar hits had numbers (2X, a REV trough); his two all-bar misses were sentiment calls; Doll's hardest misses are his most precise lines (the yield band, the 14% consensus); Galloway's one wrong-before-the-year-began number ($28 billion for TikTok US, which closed at about $14 billion) is a miss no reading can rescue.

## 4. Self-grades disagree with independent grades on exactly one word: "wrong"

Figure: `self-grade.png`.

Bob Doll's own October 5 scorecard for his ten predictions: 5 heading in the right direction, 0 wrong, 5 too soon. called-it at the standard bar, three weeks later, on the same ten (split into 14 claims): 4 met, 5 not met, 5 unresolved. The "too soon" and "unresolved" columns nearly agree. The entire difference is that he has a category for "half correct" and does not have one for "wrong." Ippolito's 2025 self-grade (21 of 27) versus an outside review (48%) is the same pattern from a different field.

## 5. Some outcomes have no bar, and that is a finding about bars

Figure: the Cursor pair in `scorecard-every.png` (claims c31 and c41).

Dan Shipper predicted Cursor was the coding-agent leader most likely to stumble. His guest Reid Hoffman predicted none of the leaders would. SpaceX bought Cursor for $60 billion in June. Shipper's strict and standard bars (growth stalls, down round, distressed sale) are not met; Hoffman's strict bar (still independent) is not met either. Neither prediction, and neither bar we wrote, had room for an acquisition at a record price. Writing bars before the year taught us to write one more bar than the prediction seems to need: what counts if the company exits.

## Ten individual outcomes worth a line each

1. Prediction-market volume did far more than double: June through August 2026 alone exceeded all of 2025 (Ippolito, met at every bar).
2. Solana's REV bottomed at $14.3 million in June and was $30.1 million by September, as predicted (Ippolito, met at every bar).
3. ETH is down 21% in the year predicted to be its best since 2021 (Ippolito, not met at every bar).
4. Zcash is up 129% in the year predicted to be bad for it (Ippolito, not met at every bar).
5. S&P 500 earnings growth is running at 32.8% against a prediction it would fall short of 14% (Doll, not met at every bar).
6. The 10-year closed above 5% on 22 days, against a predicted band of "high 3s to mid 4s"; the author calls it "half correct" (Doll, not met at every bar).
7. Core PCE sits at 3.0%, exactly where it started, as predicted (Doll, met at every bar).
8. Half of 900 surveyed designers pushed AI-generated code to production, as Shipper predicted (Every, met at every bar).
9. Every grew from about 20 people to about 30 after "we're not going to hire a ton" (Every, not met at strict).
10. Base's content coins fell 99.8% from peak and Jesse Pollak said "I was wrong," as predicted, while Base still leads every L2 category (Ippolito, met at standard, not at strict).
11. SpaceX priced its IPO at $1.75 trillion in June and closed its first day up 19%, in the year Galloway called space "the next big thing" (Galloway, met at standard).
12. The TikTok US deal closed at about $14 billion, half the $28 billion figure in the prediction that called it the best investment of the year (Galloway, not met at every bar).
13. Scotland went out of the World Cup in the group stage; the author wrote "Hey, I can dream" beside the prediction (Galloway, not met at every bar, and the only cell in 213 that everyone involved expected).

## A finding about the method, kept out of the top five on purpose

Re-asking 40 grading requests live, 120 answers moved by 1.1 and 1.4 points on average, 97% within 5 points, two crossing the decision threshold; the one 17-point move was on a cell where three trackers disagree. The grader is repeatable where the evidence is clear and unstable where it is not, which is the behaviour you would want and the reason the probabilities are printed in every cell.
