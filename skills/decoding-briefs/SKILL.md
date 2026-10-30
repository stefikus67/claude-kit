---
name: decoding-briefs
description: Use when receiving a challenge brief, case, assignment, tender, client request, research question or competition rules and before planning any research or solution; when unsure what is really being asked, what the evaluators reward, or what the deliverables, deadlines and limits are.
---

# Decoding briefs

## Overview
Starting wrong wastes everything that follows. Before any research, work out what is literally required, what the evaluators actually reward, what the asker already knows and does, and what every other team will say. The brief's own statements about the company or market are **claims to check**, not facts.

## Inputs to collect first
Every instruction source, not only the brief: the challenge text, organiser rules and emails (format, time limits, submission channel, deadlines), the judging criteria (there are often two sets: organiser and company), slides from the kickoff, anything said at the briefing. Make a list of what is missing and ask for it or fetch it. If a `personal.md` exists in the `winning-hackathons` skill folder, read it for where these usually live.

## Method
1. **Two or more independent reads.** Run at least two separate agents on the full inputs, on different models, at the highest reasoning effort available. One reads as the solver. One reads as the evaluator: "I am on this jury. What would impress me, what would bore me, what would make me distrust these students?" They do not see each other's output. If subagents cannot run, do the evaluator read first and write it down, then the solver read, and mark the decode "not independent".
2. **Reconcile.** Merge into `DECODED-BRIEF.md`. Where the reads disagree, keep both and mark the item as a question.
3. **Pre-mortem.** "It is after the final. We lost. Why?" List the 5 most likely reasons and add each as a trap or a question.
4. **Lock the checklist.** Turn the deliverables table into a checklist with internal deadlines.

## DECODED-BRIEF.md: required sections, in this order
1. **The real question**, in one sentence, plus the decision the asker must make afterwards that our answer feeds.
2. **Deliverables and hard limits.** Table: item, format, size/time limit, official deadline, internal deadline (at least 60 min earlier), submission channel, naming rule, source line. Mark each item **mandatory** or **requested-extra**. When the requests exceed what fits, the main output carries the mandatory items and the core answer; extras go to supporting material.
3. **Scoring.** Every criteria set with weights if given. For each criterion: what earns full marks in concrete terms. If weights are not given, rank by the order and wording used.
4. **The evaluators.** Who sits on the jury or reads the output: roles (engineer, sales, finance, management, professor, organiser), what each persona rewards, what each will attack. What they know better than we do: their own numbers, prices, capacity and history. Never guess those; ask or label them.
5. **Already done or known by the asker.** Everything the brief says they already do, tried or know. These cannot be the innovation.
6. **What every team will say.** The 5-8 obvious answers (trade shows, LinkedIn, an office, "sustainability", an app, "AI-powered"). Usable only as supporting tactics with a specific improvement.
7. **Claims in the brief to check.** Each statement about the market, competitors or the asker's own advantage, with how to check it.
8. **Unknowns ranked by impact.** For each: would the answer change what we recommend? Route each one to *ask the asker* / *ask a mentor* / *research* / *assume and label*.
9. **Winning shape.** One paragraph on what a winning entry looks like. It is usually: one sharp insight the asker had not framed, made concrete on one real customer or case (names, numbers, a first step they can take on Monday), and defended with sources. Give two alternative shapes.
10. **Traps.** Format traps (e.g. the kit assumes 7 minutes, the rules say 5), credibility traps (a wrong internal fact in front of insiders), scope traps.

## Length
Tables over prose. `DECODED-BRIEF.md` stays under about 1,200 words. The question sheet used in the room fits on one page; the "why" and "what changes" detail goes in an appendix.

## Questions for the asker (briefing, mentoring, organiser slots)
Rank by how much each answer changes the recommendation, not by curiosity. With several slots, route each question to the right one: the company's own facts (capacity, prices, customers, what they tried) go to the company slot; method, evaluation and "what did past juries punish" go to mentors; format and logistics go to the organiser. Put the most decision-changing company question first in the earliest company slot. Per question: wording in the asker's language and in English, why we ask, the answer public evidence suggests, what changes if they say otherwise, and a follow-up if they deflect. Fit the time slot (about 1 question per 90 seconds). Add a capture table to fill in during the meeting.

## Common mistakes
| Mistake | Fix |
|---|---|
| Using only the brief, not the organiser rules | Collect every instruction source first; format limits live in the rules |
| Taking the asker's hints (target market, buyers, "our advantage") as settled | List them under section 7 and test them |
| One read by one model | Two blind reads, one as the jury |
| "Innovation" = something the asker already does | Section 5 is a kill list for ideas |
| Planning research before the deliverables are locked | The checklist exists before wave 1 starts |
