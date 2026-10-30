---
name: winning-hackathons
description: Use when taking part in a hackathon, case competition, business challenge, pitch competition or any timed team challenge judged by a jury; from the moment the challenge is announced or chosen until after the results, including team setup, the company meeting, the pitch and the one-pager.
---

# Winning hackathons

## Overview
The orchestrator for a timed, jury-judged challenge. Accuracy is the default. Wrong internal facts in front of the company's own people, or a format mistake, lose more than any idea wins. Depth on one concrete case beats breadth. Each phase uses a sub-skill and ends at a gate.

**Read first:** `references/lessons.md` and `references/personal.md` if it exists (the user's own setup). Apply the lessons as rules. The "case notes" in that file are facts from past events: re-verify any of them before using it as a fact in a new event.

## Start (first 15 minutes)
Ask the user, in one message: team members and what each is best at; which AI accounts and plans each has; pitch language; anything already decided. Do not wait for the answers: continue on stated assumptions, list them at the top of your output, and revise when the answers arrive.
**If the briefing or kickoff is happening right now**, first do a 10-minute fast decode (deliverables and hard limits, scoring criteria, the 5 questions to ask in the room), then the full decode after. Collect every instruction source (see decoding-briefs). Create the working folder and, in team mode, the shared repo layout from running-research-ops `references/team-protocol.md`. **Before putting any instructions or skill content where teammates can read it, ask the user: "Share the team protocol with the others?"**

## Phases and gates
| # | Phase | Skill | Gate to pass before moving on |
|---|---|---|---|
| 1 | Decode the brief | decoding-briefs | `DECODED-BRIEF.md` exists with all 10 sections; deliverables checklist with internal deadlines |
| 2 | Questions for the company and mentors | decoding-briefs (questions part) | Ranked list fits the slot; capture table ready; recording consent asked |
| 3 | Question tree and wave 1 | running-research-ops | Every task has question IDs; slices spread across accounts |
| 4 | Checkpoint: pick the beachhead | running-research-ops | One customer, case or segment chosen from findings; written in `DECISIONS.md` |
| 5 | Wave 2, deep on the beachhead | running-research-ops | Who decides, when, the numbers, the first step, each with sources |
| 6 | Ideas and red team | forging-new-ideas | One spine idea locked (lock time below); survivors passed kill test (c), market-standard |
| 7 | Build pitch and one-pager | `references/pitch-and-qa.md` | Every number copied from the ledger by ID |
| 8 | Fact-check at HIGH | fact-checking-claims | Claim sheet done; `numcheck` clean on the **final** files |
| 9 | Q&A drill and rehearsal | `references/pitch-and-qa.md` | 2 timed runs under the limit; 25 hard questions answered |
| 10 | Submit early | — | Submitted before the internal deadline; confirmation saved |
| 11 | After results | — | Post-mortem appended to `references/lessons.md` |

Timeline for a 24-hour event: `references/timeline-24h.md`. For longer events, stretch phases 3-6 and add real validation (short calls with potential customers, made by the humans).

## Non-negotiables
- The organiser's rules beat the company's form and our assumptions on format, time and submission.
- Anything the company said verbally is one person's word: label it, never make it a headline number, and ask permission to quote it.
- Never guess the company's internals (capacity, prices, margins, customers). Ask, or say "to be confirmed with you".
- Kill test (c) runs on the spine idea before the lock: if competitors already sell it, it is not the innovation.
- Agents never send messages, emails or posts. Humans do, after the user approves.
- Keep an AI log from the start (`00-brief/AI-LOG.md`: time | tool and model | what for | who) in case the rules require disclosure.
- Scope: the pitch carries the spine idea plus the mandatory deliverables. Everything else the brief asks for goes on the one-pager, backup slides or an appendix, in that order.

## Common mistakes
| Mistake | Fix |
|---|---|
| Kit assumes a format the rules don't allow | Phase 1 gate: limits copied from the rules with the source line |
| 24 shallow targets, no depth | Phase 4: beachhead, then wave 2 deep |
| "Innovation" competitors already offer | Kill test (c) before the lock |
| One-pager written at the deadline | Internal deadline at least 60 minutes earlier |
| Numbers retyped from memory into slides | Copy from the ledger; `numcheck` the final files |
| Teammates' agents duplicate each other | BOARD claims plus reading the digest first |
