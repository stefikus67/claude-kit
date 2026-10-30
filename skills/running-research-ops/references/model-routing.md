# Model and effort routing

Check what is available at run time (the Agent tool lists models; effort levels are low → max). As of Oct 2026 the strongest options were Fable 5.1 and Opus 5.5; Sonnet 5.5 for volume work; Haiku 5.5 for trivial mechanical work. Prefer the newest strongest model when this table is out of date.

| Work | Model | Effort | Why |
|---|---|---|---|
| Decoding the brief (2+ blind reads) | strongest two, one each | max | Starting wrong ruins everything after it |
| Question tree, triage, synthesis, decisions | strongest | max / xhigh | Judgment |
| Idea generation and red team | strongest; the red team runs on a different model than the idea author | max | Avoids one model agreeing with itself |
| Retrieval slices | strong (Opus/Fable) for hard or primary-source-heavy slices; Sonnet for list-building | high | Quotes and URLs must be exact |
| Claim extraction (splitting text into claims) | Sonnet | high | Mechanical but atomicity matters |
| Verification, first pass | strong | max | Verdicts |
| Verification, second pass | a different model from the first pass, blind | max | Independence |
| Formatting, file conversion, slide text from settled content | Sonnet / Haiku | medium | Mechanical |

Rules:
- A verifier never runs on the model that produced the claim it checks.
- When only one vendor's models are available, say so in the report: a Claude-only second check is not an independent audit.
- Usage limits: watch the remaining budget at every checkpoint. When short, cut T3 questions first, then T2. Never cut T1 or the verification pass.
- Team mode: spread load across accounts (see team-protocol.md). Heavy retrieval slices go to whoever has the most headroom; cross-verification goes to a different person's account, which also gives independence.
