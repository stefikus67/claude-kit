---
name: fact-checking-claims
description: Use when a document, pitch, slide deck, report, one-pager or research output must be checked before it is shown to a jury, client, professor or anyone who knows the subject; when numbers, names, dates or quotes came from AI research; or when someone asks "is this true", "check the sources" or "what can go on the slides".
---

# Fact-checking claims

## Overview
Check claims one at a time against the source itself, and keep a ledger where every verdict carries the URL, a verbatim quote and the access date. A verdict without a quote is an opinion. The output is a **claim sheet** that says, per claim: use it, use the corrected wording, say "we estimate", check first, or do not use.

## Pick the depth first
- **Hackathon or anything a jury will see: HIGH.** Do not ask.
- **Anything else with no depth stated: ask the user** with one question: quick / standard / high / audit, and what it is for.

| Depth | Claims covered | Passes | Extra |
|---|---|---|---|
| quick | the 10-20 claims the conclusion rests on | 1 | — |
| standard | every number, name, date, quote, ranking in the deliverable | 1 | orchestrator re-opens 2-3 URLs per verifier |
| high | standard | 2 for CRITICAL claims, second pass on a **different model**, blind to the first verdicts | taint + numcheck on the final file |
| audit | every claim in every source file (atomic extraction) | 2 | provenance: where each claim first appeared |

## The procedure
1. **Extract** atomic claims into `claims.jsonl` (one checkable statement per row; implicit claims too: rankings, captions, "this proves"). Rules: `references/extraction-rules.md`. Load: `ledger.py add --ledger L claims.jsonl`.
2. **Verify** with `references/verifier-prompt.md`. Verifiers get claim text + location only, never the author's reasoning or a previous verdict. Cluster claims by source, one agent per cluster (a single agent works the clusters in order). Verdict lines **reuse the claim ids** and are loaded on top: `ledger.py add --ledger L --update verdicts-pass1.jsonl`.
3. **Second pass** (high/audit): same clusters, different model, blind. Disagreement → `DISPUTED (A vs B)`, keep both views; never silently pick the friendlier one. If no second model or agent can run, add `SINGLE_PASS` to the notes of every CRITICAL row and say so at the top of the report.
4. **Load and propagate**:
   ```
   python -X utf8 scripts/ledger.py init --ledger audit/ledger.csv
   python -X utf8 scripts/ledger.py add --ledger audit/ledger.csv verdicts.jsonl
   python -X utf8 scripts/ledger.py taint --ledger audit/ledger.csv
   python -X utf8 scripts/ledger.py sheet --ledger audit/ledger.csv --out audit/CLAIM-SHEET.md
   ```
5. **Gate the final deliverable**: `ledger.py numcheck --ledger audit/ledger.csv pitch.md` reports WRONG (a number that was corrected or failed), CHECK FIRST and UNBACKED numbers. Each one is fixed, labelled as an estimate, or removed. numcheck skips single digits and cannot read words, so also compare the final text against every USE CORRECTED row by eye ("live", "up to", "planned").
6. **Report** (to a file; if writing is blocked, in the reply): depth and single-pass status, counts per bucket, DO NOT USE with what to say instead, CHECK FIRST with who must confirm what, and the slide-safe list = USE rows plus USE CORRECTED rows in their corrected wording.

## Time
Plan about 1-2 minutes per claim per pass. If the time does not cover everything, order the work: (1) the headline claim and the key numbers the conclusion rests on, (2) named companies, people and dates, (3) other CRITICAL, (4) HIGH. State what was not reached.

## Verdict rules (these decide quality)
- **VERIFIED needs the number itself in the quote.** "143 weeks" in the source and "144 weeks" in the claim is CORRECTED, not VERIFIED. Compare digits, units, dates and scope (substation capacity ≠ live load; "up to" ≠ "will"; announced ≠ built ≠ energized).
- **Primary beats secondary.** A press article quoting a filing is checked against the filing when it can be opened. Five outlets quoting one figure are one source.
- **Search snippets are not sources.** Open the page. If the primary page blocks you (403, bot check), try an archived copy (web.archive.org) or a verbatim syndicated copy (PR Newswire, SEC full text, the regulator's PDF mirror) and name it in `evidence`. If nothing opens: NEEDS_HUMAN with the URL, never VERIFIED.
- **Absence is not refutation.** "No source found" is UNSUPPORTED; CONTRADICTED requires a source that states otherwise.
- **Internal facts** (what the company/client said, their own customers, capacity or prices, what a team file says) are checked against the transcript or file line. If you cannot access it, or the web is silent about the client's own internals, the verdict is NEEDS_HUMAN ("ask the client"), not UNSUPPORTED.
- **Conflicts inside the document**: when an estimate or claim contradicts a verified row in the same document, add `CONFLICT with <id>` to its notes. The sheet then puts it under CHECK FIRST.
- **`accessed` is the real clock time**, even in a simulation.
- **The checker adds nothing new to the deliverable.** New risks or facts found while checking go in a separate "found while checking" list, each with its own source and status. They never enter the slide-safe list unverified.

## Common mistakes
| Mistake | Fix |
|---|---|
| Sources listed at the end, not per claim | Every ledger row carries its own `source_url`, `quote`, `accessed` |
| "OK, with nuance" on a headline claim | Nuance means CORRECTED; write the corrected wording in `correct_value` |
| Verifying the author's mutated number because it is "close" | Digits must match the source; otherwise CORRECTED |
| Same model checks its own output | Second pass on a different model, blind |
| Fixing claims but not their dependents | Run `taint`: a total built on a wrong input is TAINTED |
| Checking once, then editing the deck freely | Run `numcheck` on the **final** file, after the last edit |
