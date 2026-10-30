---
name: forging-new-ideas
description: Use when a hackathon, case, strategy or product question needs an original solution rather than a summary of research; when the ideas on the table feel generic, obvious, or like what every team would say; or when choosing which idea to build the pitch or recommendation around.
---

# Forging new ideas

## Overview
A new idea is a specific mechanism that the asker does not run today, that competitors do not already sell to the same kind of buyer, and that the evidence makes credible. Generate wide from facts, kill hard with explicit tests, attack the survivors with the evaluators' eyes, and commit to one spine.

## Inputs
- `DECODED-BRIEF.md` (decoding-briefs): "already done by the asker", "what every team will say", the evaluators and their weights.
- Findings with IDs and grades (running-research-ops).

## 0. Before research exists
At the very start there are no finding IDs. Write 3-6 **seed hypotheses** (H-01..) from the brief's constraints. Each becomes research questions plus a disconfirming query. They are not ideas and are never pitched as such.

If the user hands you a shortlist, start at step 2 with it, and say that generation was skipped.

## 1. Generate 15-25 candidates, from facts, across lenses
Every candidate starts from a finding ID or a stated constraint. Use every lens at least once:

| Lens | Prompt |
|---|---|
| Offer / business model | What could they sell other than the product: time, certainty, risk transfer, capacity, service, data? |
| Channel | Who already has the buyer's trust and could carry this offer? |
| Proof / trust | How does a buyer with no reason to trust them get one in weeks, not years? |
| Product / standardisation | What could be pre-engineered, bundled or unbundled? |
| Financing / risk | Who carries which risk today, and who would pay to drop it? |
| Timing | What window opens or closes, and when? |
| Flip the weakness | Turn the asker's biggest weakness into the offer |
| Analogy | Which other industry solved the same shape of problem? Name the case, port the mechanism |
| Inversion | What would guarantee failure? Do the opposite, specifically |
| Remove a constraint | Without the budget/time/geography limit, what would we do? Then find the cheap version |

Candidates with the same mechanism are merged into one (note the merged IDs).

## 2. Kill tests (one failure kills; record the test and the evidence)
- **(a) Already done by the asker**: in the brief, on their site, or said by them.
- **(b) Obvious**: it is on the "what every team will say" list, or it is a generic category (marketing channel, trade show, office, certification, "AI monitoring/platform"), or a team could reach it from the brief alone within an hour.
- **(c) Already market-standard.** Run these three searches and record them:
  1. the mechanism + the **same product category**, any country, any buyer (e.g. "transformer capacity reservation", "transformer slot reservation agreement");
  2. the mechanism + the **same buyer segment**, any product (e.g. "data center developers reserve manufacturing slots");
  3. each named competitor + the mechanism.

  Run at least two query variants per search. Search 3 uses the competitors named in the brief or research; if none are named, the 3-5 largest makers found so far.
  **If any maker of the same product already offers this mechanism to the same type of buyer anywhere, it is market-standard.** Buyer type means the segment that signs: utilities, developers/hyperscalers, industrial users, EPCs, distributors. If a source does not say who the buyers are, treat them as the same type. It fails as the headline innovation, whatever twist is added. A precedent from another product or another buyer type is an *adjacent* precedent: it passes (c) and satisfies (f).
- **(d) Cannot start** within the brief's horizon and budget.
- **(e) No mechanism**: no payer, no reason to act now, or no believable first step.
- **(f) No precedent at all**: nothing adjacent shows it can work. (The same thing in the same market fails (c) instead.)

**Twists.** If a killed idea has a genuinely new twist (e.g. "resellable" or "design fixed later"), each twist becomes its **own candidate** and goes through every test again, the twist itself through (c). Standard parts that the twist needs stay on its card, labelled "standard enabler". If it survives, the pitch says honestly: "X is standard in this market; what nobody offers is Y."
**Passing (c) on absence** means: all three searches run with their variants, nothing found, unopened hits recorded as LEAD. The pitch then says "we found no one offering Y", never "nobody offers Y".

Facts found during kill tests are recorded as findings with a grade (A/B/C/LEAD as defined in running-research-ops). Any opened page (A, B or C) showing that something exists is enough to kill an idea; a LEAD is not. Supporting an idea in the pitch needs grade A or B.

## 3. Idea cards (survivors only)
Killed candidates get one line in the kill table: id, idea, lens, rests on, failed test, evidence (URL).
Survivors get a full card: name · mechanism in two sentences · who pays and why now · why this asker can do it and others cannot · first step for Monday (owner role; cost as an order-of-magnitude estimate, labelled) · closest *adjacent* precedent (link) · finding IDs · the riskiest assumption · the (c) searches run and what they found.

## 4. Red team
Run it as a separate subagent on a **different model** from the author (e.g. author on Opus → red team on Fable, or the reverse), at the highest effort. It gets the cards but not the author's reasoning. Personas: 3-5 from the decoded brief (e.g. the company's engineer, salesperson, finance lead; the professor; the organiser). Each persona asks the three questions that would sink the idea and marks each as answered, partly answered or unanswered by the evidence. If no second model is available, use a fresh subagent on the same model with no access to the author's reasoning, and mark the result "same-model red team, provisional". Write the steelman of each survivor.

## 5. Score and commit
- Score 1-5 per criterion. Total = Σ(score × weight) / 5, out of 100 with the brief's weights. Each unanswered sinking question costs 1 point on the 1-5 score of usefulness or feasibility. Without a red team, label the scores "provisional (no red team)". The steelman does not change the score. Tie-break: innovation, then usefulness.
- Apply the brief's hard gates, plus the survivor's own riskiest assumption if the whole mechanism depends on it. A gate that cannot be checked yet gives a **conditional lock**: name the condition, who checks it and by when, and the fallback spine.
- Lock **one spine** at the lock time in the plan (hackathon default: before the midnight check or 9 hours in). Write one line in `DECISIONS.md`: time | spine | why | finding IDs | condition | fallback. Other survivors become supporting tactics or "further development", not a second headline.

## Output order
1. Inputs used (findings with grades) → 2. candidate table → 3. kill table with evidence → 4. survivor cards → 5. red team → 6. scores → 7. the lock line.

## Common mistakes
| Mistake | Fix |
|---|---|
| Calling a same-product precedent "adjacent" | Same product + same buyer type anywhere = market-standard (c) |
| Adding a twist and keeping the standard mechanism as the headline | The twist is its own candidate; the pitch names the standard part as standard |
| Red team by the same model that wrote the ideas | Different model, fresh context; otherwise mark it provisional |
| Brainstorming from a blank page | Every candidate starts from a finding ID or a constraint |
| Three ideas presented as one pitch | One spine; the rest support it |
| Buzzwords instead of mechanics | The card forces a payer, a first step and a precedent |
