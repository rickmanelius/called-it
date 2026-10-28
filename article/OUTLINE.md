# Article outline (draft structure, numbers to come from runs/*/data.json)

Working title options:
- "Did they actually call it? Grading three sets of 2026 predictions at three bars"
- "Every prediction grade is an argument about the bar. So we graded at three."
- "Before the 2027 prediction season: receipts for 2026"

Audience: Hacker News front page and the people who write annual prediction lists. Tone: fair, curious, no gotcha. The subjects are not targets; they are the first three people brave enough to write things down.

## 1. The ritual and its missing half (150 words)
Every November to January, people publish predictions. Almost nobody grades them, and the few who do grade generously. Mike Ippolito scored his own 2025 list at 21 of 27; a third party scored the same list at 48%. Both are plausible. That gap is the subject of this piece.

## 2. The idea: three bars, not one grade (250 words)
Every argument about whether a prediction came true is an argument about the bar. Instead of picking one, write three before looking at any evidence: strict (what a hostile critic would require), standard (what a fair reader accepts), lenient (the weakest reading a critic would still concede). Grade all three. Report the gap. The flying-car example: "cars fly" versus "cars fly between cities" is not a disagreement about facts.

The critic floor: lenient is lenient about the claim's scope, never about the evidence. Social chatter meets no bar. An author's victory lap is weak evidence; an author's admission is strong.

## 3. Why now: decision classifiers (200 words)
Jev (TypeSafe's System One model) answers typed questions with calibrated probabilities instead of prose. Ask it the same question twice and it moves by a few points, not a paragraph. For a grade that gets published, a number that reproduces is worth more than a clever rationale. Strong reasoning models do the reading and the searching; the classifier does the repeated yes/no. The whole run is committed, so anyone can replay it offline and get the same scorecard.

What we learned building it: the critic check (would a skeptic accept this bar as fair?) caught real problems in our own bars three times (a 2-point margin the author never promised, a bar Ethereum already met when the prediction was made, a lenient bar that dropped half the claim), and it is wording-sensitive enough that you must not iterate against it.

## 4. The three subjects (100 words)
Every (AI, a company that predicts the thing it builds), Mike Ippolito of Blockworks (crypto, 27 numbered calls, three years running), Bob Doll of Crossmark (finance, ten numbered calls for 30 years, grades himself quarterly). Chosen for a spread: vague to numeric, company to person, hype to macro.

## 5. Scorecards (600 words, one figure each plus the cross-subject chart)
Per subject: the three hit rates, the generosity gap, the two or three claims where the bars disagree most, and one claim where the evidence surprised us. For Doll: his own Oct 5 self-grade (5 right direction, 0 wrong, 5 too soon) beside ours. For Every: Shipper's "Cursor will stumble" beside Hoffman's "none of them will". For Ippolito: the numeric calls (VC $12-18B, 2X prediction-market volume, vault AUM $15-20B) versus the narrative ones.

Figure 1: hit rate at each bar, three subjects (one hue, direct labels).
Figure 2: the generosity gap per subject.
Figure 3: one claim ladder, probably Doll's, because the numbers are crisp.

## 6. What the gap says (250 words)
Hypotheses to test against the data, not conclusions yet:
- Numeric predictions have a small gap (the bar is in the claim). Narrative predictions have a large one.
- Self-grades land near the lenient bar.
- "Unresolved" is a bigger category than anyone admits in October; most year-end lists are graded before the year ends.

## 7. Caveats (150 words)
Run on October 24 with ten weeks left; everything with a December horizon is provisional. Jev and the reasoning model are both text-only; some claims hinge on things a screenshot would settle. Our bars are ours; the sheet is public and the run is replayable, so argue with the bars, not the numbers. Guest predictions on a subject's podcast are shown apart.

## 8. The ask (120 words)
The 2027 season opens in a week. Before you publish your list: run it through the skill in "pre-register" mode and write your three bars now, while you still mean them. If you published a 2026 list: run it on yourself and post the receipts. The repo takes runs by pull request; a gallery of graded lists is the plan.

Install lines for Claude Code and Codex. One sentence on costs (no keys needed; Jev is the upgrade).

## Figures and assets
- `article/infographic/process.png` (the method, 1600x900)
- per-subject `runs/<run>/report.html` screenshots
- cross-subject chart from `runs/*/data.json` (to build)

## Pre-publication review
Mike Taylor (@hammer_mt, Every) for the method and the Every scorecard. Pitch note to draft once the Every run is final.
