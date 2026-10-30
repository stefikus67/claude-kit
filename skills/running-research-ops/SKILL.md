---
name: running-research-ops
description: Use when a question needs more than a few searches, when planning research for a hackathon, case, client or decision, when several AI agents or several people will research in parallel, or when research keeps going in circles, repeats itself, or produces confident text without sources.
---

# Running research operations

## Overview
Research exists to change a decision. Every task traces back to a question in the decision tree, and every finding carries an opened source and a verbatim quote. Agents retrieve and tabulate; the orchestrator judges. A research round that changes nothing ends that branch.

## Accuracy level
- Hackathon or competition: **high** (default, do not ask).
- Anything else with no level stated: ask once: "How much does accuracy matter here: quick / standard / high / audit? What is it for?" The level sets verification depth (see fact-checking-claims) and how many agents are worth spending.

## 1. Build the question tree before any search
`QUESTIONS.md`:
- **D0 decision**: what the output must let someone decide or do.
- **Criteria**: how the decision will be judged (from DECODED-BRIEF if one exists; see decoding-briefs).
- **Key questions Q1..Qn**: what must be known to decide.
- **Sub-questions Q1.1..**: each specific enough to be answered with sources.

Triage each sub-question:

| field | values |
|---|---|
| changes the answer? | yes / maybe / no (context only) |
| current uncertainty | high / medium / low |
| route | research / ask the asker / ask a mentor or expert / assume and label |
| tier | T1 = yes+high (now), T2 = credibility for the audience, T3 = nice to know (cut first) |

Each question also gets a **disconfirming query**: the search that would prove our current belief wrong.

## 2. Slice and dispatch
- One agent per slice of 3-6 related sub-questions, never one agent for "research the market".
- The prompt is `references/agent-prompt.md` filled in, plus the slice's question IDs. Retrieval agents do not score options, write strategy or recommend.
- Model and effort: `references/model-routing.md`. Judgment work (decoding, synthesis, red team) runs on the strongest model at the highest effort. A verifier never runs on the model that produced the claim.
- **Team mode** (several people, each with their own agent): repo layout, findings bus, claim protocol and account split are in `references/team-protocol.md`. Before writing any instruction file into a shared repo or sending these instructions to teammates, **ask the user whether to share them**.

## 3. Findings flow
Every agent appends findings as JSONL (schema in `references/team-protocol.md`), one line per finding, each with `question_id`, `source_url`, `quote` and `grade`. Merge with:
`python -X utf8 <fact-checking-claims>/scripts/ledger.py digest findings/ --out findings/DIGEST.md`
Agents read `DIGEST.md` before starting and skip questions that are already answered at grade A. Synthesis cites finding IDs. It never paraphrases another agent's prose.

## 4. Checkpoints and stop rules (the anti-slop loop)
At each checkpoint (every wave, or every 2-3 hours in a sprint), answer in `STATUS.md`:
1. Which findings changed the answer since the last checkpoint? (IDs)
2. Which hypotheses died?
3. Which T1 questions are still open, and what is the cheapest way to close each?

Stop rules:
- A branch with no answer-changing finding in two checkpoints is closed. Its open questions go to `UNKNOWN` with a "how a human could find out" line.
- The same question searched 3 times without a new primary source: mark UNKNOWN, add it to the human fetch list, move on.
- No new wave without a named T1 question it will answer.
- Text from training memory or a search snippet may suggest a query (grade LEAD). It never fills a cell.
- **Depth beats breadth.** After wave 1, pick the beachhead (one customer, one case, one segment) and send wave 2 deep on it: names, numbers, timing, who decides. Keep the broad list as a backup slide only.

## 5. Before anything leaves the research
Run the fact-checking-claims skill at the agreed level on the deliverable. Numbers are copied from the ledger by ID, never retyped from memory: retyping is how 143 becomes 144.

## Common mistakes
| Mistake | Fix |
|---|---|
| Splitting by topic ("market", "competitors") | Split by question IDs that feed the decision |
| Agents writing strategy | Retrieval only; judgment stays with the orchestrator |
| Re-summarising summaries across rounds | Synthesis cites finding IDs and quotes |
| Another wave because time is left | Only for a named open T1 question |
| Ending with 24 shallow targets | Pick the beachhead after wave 1 and go deep |
| Same model checks its own work | Cross-model or cross-account verification |
