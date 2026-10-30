# Brief, per-agent briefs and the re-prompt loop

## The brief, long form

```
GOAL
  [What exists at the end, in one sentence.] [Why it matters, if the reason changes choices.]

DONE TEST
  D1 [check] - evidence: [file / command output / rendered page / quote + URL]
  D2 ...
  (3-7 items. Each one pass/fail. Someone who did not do the work can run it.)

CONSTRAINTS
  Scope:    [paths, accounts, tools allowed]
  Budget:   [time, agents, tokens, money: EUR 0 unless the user says otherwise]
  Never:    [actions that are out]
  Ask first: [send, post, pay, delete, install, push, account or settings changes]

CONTEXT
  Decided:  [decisions already made, with the file that records them]
  Tried:    [what failed and why]
  Inputs:   [paths, links]
  Audience: [who reads or uses the result]

STEPS
  1. [step] -> checkpoint: [what is checked]
  2. [step] (parallel with 3)
  3. [step] (parallel with 2)
  4. Verify against DONE TEST, report.
```

### Good and bad done tests
| Weak | Strong |
|---|---|
| The reel looks professional | 1080x1920, 9:16, captions inside the safe zone, no caption line over 32 characters, č/š/ž render |
| Research is thorough | Every claim in the table has a URL that opens and a verbatim quote; 0 cells from memory |
| The script works | `python -X utf8 run.py --dry-run` exits 0 and prints 12 rows |
| The email is ready | Under 120 words, contains only the three points the user named, Slovene check passed |
| Code is tested | `pytest -q` passes; the new test fails on the old code |

### Worked example
Rough request: "make a reel about the café's new menu"

```
GOAL         A 20-30 s Slovene reel announcing the autumn menu, ready to post as a trial reel.
DONE TEST    D1 Hook in the first 2 s names the menu (transcript line 1).
             D2 3-5 dishes shown, each named in captions with its price from PRICING.md.
             D3 1080x1920, captions in the safe zone, Slovene check passed.
             D4 the user approves the cut from the review page.
CONSTRAINTS  Own footage first, Pexels only for gaps. No posting: The user posts from the phone.
CONTEXT      Prices: the price list. Brand: brand.json.
STEPS        1 shot list (director skill) -> 2 the user films -> 3 STT + cut -> 4 render -> 5 check D1-D4.
```

## Per-agent brief
Each sub-agent knows only what its prompt says. Write it for a capable colleague with no context.

```
<task>
[Slice goal, one sentence.] This is part of: [the overall goal, one line].
</task>

<done_test>
[Only this slice's items, copied from the main DONE TEST and narrowed.]
</done_test>

<inputs>
[Paths and links to read. Say which to read first.]
</inputs>

<scope>
Work only in: [paths]. Do not touch: [paths].
Retrieve and report; do not recommend or decide.   (for research agents)
Ask-first actions are out of scope: stop and report instead.
</scope>

<output>
[Exact shape: JSON schema, table columns, or file path to write.]
Ground every claim in a tool result, file or quoted source. Mark anything unverified as UNVERIFIED.
</output>

<stop>
Stop when the done test passes, or after [N] attempts at the same blocker; then report the blocker.
</stop>
```

Notes:
- In a Workflow script, pass a JSON schema to `agent()` instead of describing the output in prose.
- Split by independent pieces of the done test, not by topic.
- Research agents retrieve; the main session judges (see running-research-ops).
- Model choice: cheap models collect, the strongest model judges and writes. A checker never runs on the same agent that produced the work.

## The loop, step by step

### Check
For each returned result, write a check row per done-test item:

| Item | Pass/fail | Evidence | Note |
|---|---|---|---|
| D1 | pass | `out/transcript.txt` line 1 | |
| D2 | fail | 2 of 4 prices missing | prices not in PRICING.md for soup, cake |

Use a fresh agent or a command to check anything that goes to a jury, client or the public. For facts, run fact-checking-claims.

### Delta brief (re-prompt)
```
Round [2/3]. Your last result failed [D2].
Evidence: [what was found, with location].
Change: [the specific fix].
Keep: [what passed and must not change].
Same scope, output and stop rule as before.
```
Send it to the same agent (SendMessage) when its context helps, or to a fresh agent when the first one went in circles.

### Stop
- Default 2 rounds. A third round only if round 2 closed at least half of the failed items.
- The same item failing twice for the same reason means the brief is wrong, not the agent. Fix the brief or ask the user.
- Back to the user with:

```
[Name], [task]: [X of Y] checks pass after [N] rounds.
Still failing: [item] - [why, one line].
Options: (a) [...] (b) [...]. I'd pick [a/b] because [one reason].
```

### Using /goal
For a loop that stays in one session, the user can type:
`/goal D1-D4 from BRIEF.md all print PASS in the transcript, or stop after 10 turns`
The evaluator reads only the conversation, so every check must print its own PASS/FAIL line. It does not run commands or open files itself.

## When not to loop
- A single edit, lookup or reversible step: just do it.
- Work whose result the user judges by taste (a cover, a hook line): give 2-3 variants once, let him pick.
- When the blocker is missing information only the user has: ask after round 1.
