# Team protocol: several people, each with their own AI agent

Use when 2+ people research in parallel with their own Claude (or other) accounts. Before writing these rules into a shared repo or sending them to teammates, ask the user whether to share them.

## Roles
- **Orchestrator** (one person + their strongest-model session): owns `DECODED-BRIEF.md`, `QUESTIONS.md`, `DECISIONS.md`, synthesis and the final story. Only the orchestrator edits these.
- **Slice owners** (each person + their agent): own question slices, write findings, verify someone else's findings.
- **Human-only work** is assigned by name too: calls and meetings with the asker, mentor sessions, slides and design, rehearsal, submission. Agents never send messages to anyone.
- Assign by strengths and available usage. Ask each person: what are you best at, which account/plan do you have, how much usage is left.

## Account split
- Each person's agent runs its own slices. This spreads usage limits.
- Cross-verification: person B's agent verifies person A's CRITICAL findings (blind to A's grade). This is both independence and load-sharing.
- At each checkpoint, each person reports their remaining usage in `STATUS.md`. Rebalance slices if someone is near their limit.

## Repo layout (shared git repo = message bus)
```
00-brief/        inputs verbatim (brief, rules, emails, meeting notes) + DECODED-BRIEF.md
QUESTIONS.md     question tree with IDs, tier, route, owner   (orchestrator edits)
BOARD.md         tasks: id | question IDs | owner | account | status | started | output path
DECISIONS.md     time | decision | why | finding IDs           (orchestrator edits)
STATUS.md        checkpoint notes: what changed the answer, what died, open T1, usage left
findings/<person>.jsonl   append-only, one finding per line (schema below)
findings/DIGEST.md        auto-built: ledger.py digest findings/ (never edit by hand)
raw/<person>/    full agent outputs, verbatim
audit/           ledger.csv, claim sheet (fact-checking-claims skill)
deliverables/    pitch, one-pager, report (one owner per file)
```

## Protocol for every agent and person
1. `git pull --rebase`, then read `DIGEST.md`, `BOARD.md`, `DECISIONS.md`. If a decision exists, do not reopen it.
2. Claim the task on `BOARD.md` and push immediately (`claim: <task>`). If the push fails: pull, re-read; if someone else claimed it, pick another.
3. Before researching, check the digest: is the question already answered at grade A? Then verify it or move on; do not redo it.
4. Write findings only to your own `findings/<person>.jsonl` (append). Never edit others' files; add a finding that disputes theirs instead (`status: disputes <id>`).
5. Commit and push after each meaningful step; rebuild the digest after pulling.
6. A finding with `impact: changes-answer` also gets one line to the team chat from the human: "CHANGES ANSWER: <id> <one line>". Agents do not post.

## Finding schema (JSONL, one per line)
`id, who, time, question_id, claim, value, unit, as_of, source_url, quote, source_type, grade, impact, status, notes`. `grade` A/B/C, `impact` changes-answer / supports / context, `status` new / verified / disputed / disputes <id>.

## Merge rules
- An opened primary source beats no source. Two sourced values that conflict become a range with both sources, until someone resolves the definition.
- A cell with no grade A or B finding stays UNKNOWN.
- Two people reaching the same idea from the same shared material is not independent confirmation.
