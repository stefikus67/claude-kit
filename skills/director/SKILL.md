---
name: director
description: Use when planning, scripting, filming, editing, captioning or posting a short vertical video (Instagram reel, TikTok, YouTube Short) for Stepan, Café Biennale / Tivoli, Kaval Group or a client; when he asks for hooks, a script, a shot list, how to make something go viral, or to edit raw clips into a reel; when a reel needs Slovene captions or an English version; or when reading a reel's numbers and deciding the next test.
---

# Director

## Overview
Turns an idea into a postable 1080x1920 reel, and the reel's numbers into the next idea. Every rule here comes from the fact-checked virality playbook (`~/claude-kit/docs/VIRALITY-PLAYBOOK.md`, v2). The grade sits next to the rule: A means a platform or paper says it; B means a practitioner or press source; LEAD means an untested tip. Never present a LEAD as proven. Nothing here posts anything: Stepan posts from the phone app, where Trial reels and in-app audio live.

## On a claude-kit PC (Gaber's)
- Gaber is the editor; Stepan is the creator and client. Stepan's standing choices below apply to his reels and the café's reels.
- Where this skill says "show Stepan" or "ask Stepan": prepare it for Gaber, who passes it on (or Gaber decides, if Stepan delegated it).
- Stepan posts from his phone. Never post, and never promise offers or prices without Stepan's OK.
- Tools: `~/claude-kit/tools` (reel + sl-stt). Footage per reel: `~/claude-kit/reels/<yyyy-mm-dd>-<name>/intake/`.

## The five things that matter most
1. **Hold.** Watching is a named top signal on Instagram, TikTok and YouTube (A). Cut every pause, filler and retake. End right after the payoff.
2. **Send-worthiness.** Sends per reach correlated with reach more than anything else, in Mosseri's experience (B). Before scripting, ask "who exactly would he send this to, and why?" No answer means a weaker idea.
3. **First seconds.** Treat the intro like a thumbnail: visual, centred, no more than about three objects, works with sound off, about 3 s (B). Show the thing; don't announce it.
4. **Originality.** No reposts, no other apps' watermarks (CapCut, TikTok), and no reaction-only clips (A). Our own logo is fine.
5. **Test, don't guess.** Every experiment is a pair of Trial reels that differ in one variable (A for the feature; the method is ours).

## Stepan's standing choices (decision page, 2026-10-28)
- **Captions:** `klasika` by default. `highlight` and `pop` are his alternatives, so they're the natural second variant in a caption test.
- **Edit decisions:** Claude decides cuts and text fixes and renders. Stepan reacts to the reel ("most of the time"). Show him the cut list first only when a cut removes content, not just a retake or pause.
- **English:** later, not per video for now. Make an English version only when he asks.
- **First test:** same reel, two hooks, as a Trial pair.
- **Reference creator so far:** @gaspergubanc. The full list is still to be agreed with him.
- **Types are not fixed.** Mixed formats are normal (a talking head with vlog B-roll, a promo told as a story). The three types in `references/types.md` are building blocks to combine, not boxes.
- **Plans come first.** Every reel belongs to a short-term plan (this week or month) inside a long-term plan (pillars, series, goals). Read `~/claude-kit/docs/CONTENT-STRATEGY.md` once it exists, and say which pillar and series a reel serves before scripting it.

## Workflow
| Step | Do | Output |
|---|---|---|
| 1. Brief | Exactly five lines: (1) type (or mix) + goal, (2) audience, (3) language (SL first; EN as a separate post), (4) CTA, (5) deadline + target length. Then list **Assumptions** and **Open facts**. The platform defaults to Instagram. Ask at most 3 questions; otherwise assume and write the assumption down. Goal-specific contents are in the table below. | Brief + assumptions + open facts |
| 2. Idea check | Apply the send test plus share drivers: useful, surprising, interesting, awe or anger (A, news-sharing data; transfer to reels untested). Café: behind the scenes, process, staff, 80/20 value vs promo (A, TikTok guidance). | Go / rework |
| 3. Hooks | 3 variants, each with a visual, a spoken line and on-screen text. The spoken hook is under about 12 words and about 4 s; the first 3 s of image must carry the hook without it. Patterns: `references/hooks-sl.md` (LEAD). | 3 hooks |
| 4. Script | Beats chained by "but / therefore" (B). Deliver right after the hook. Keep opening new questions (B). Lists of 3/5/7 (B). End on the payoff, ideally looping into the first line. Target 15-60 s (B, Instagram's guide as reported). Slovene speech runs at about 2-2.5 words/s, so 60 s is about 120-150 words. | Script with timings |
| 5. Shot list | Per beat: shot, framing, B-roll, on-screen text, seconds. Per type: `references/types.md`. | Table |
| 6. Filming card | A task card for Stepan (prompt-forge format): phone vertical at 4K/30 if possible, light facing him, mic or a quiet room. On a fumble, say **"še enkrat"**, pause 1 s, and restart the sentence. Film 5-7 s B-roll clips. | Card |
| 7. Edit | `references/pipeline.md`: `reel.py ingest`, review `REVIEW.md` (decide every `propose` cut, fix names and numbers), choose the caption style, `reel.py render`. Check the contact sheet before calling it done. | `out/reel.mp4` |
| 8. Post pack | Caption with keywords, up to 5 targeted hashtags (B), Collab partner, location, audio note, cover frame, Trial or normal. `references/post-and-test.md`. | Post pack |
| 9. Read and learn | After about 24 h: skip rate (if shown for trials), average watch time and drop-off, sends per reach, likes per reach. Log it, and pick the next test. | 1 row in the log + next test |

## Goals change the plan
| Goal | The plan must contain | Measure |
|---|---|---|
| Reach | A send-worthy moment named in step 2; optionally a CTA asking to send it (ours, untested) | Sends per reach (B, S1-09) |
| Follows | A reason to follow (a series or part 2, only if Stepan will make it); profile checked (bio, pinned reel) (LEAD) | Follows per 24 h in the log |
| Visits | A code or a till question (ours); the same offer in both Trial variants; till sales of the item before and after | Redeemed codes, till tally, daily item sales |

## Hard rules
- **Never invent a fact** about Stepan, the café or a client: prices, offers, hours, product names, results, numbers. Write `[X?]` in the script and list every `[X?]` as step 1 of the filming card. A reel with an open `[X?]` is not postable.
- Burn in captions on every reel. We found no confirmed Slovene auto-captions on Instagram or TikTok (2022 lists; current support unknown), so captions come from `~/claude-kit/tools/sl-stt`, and names and numbers are fixed before render.
- Proofread Slovene on-screen text and captions (prompt-forge section 5) before Stepan posts.
- Never claim a reel "will go viral". Say what the evidence says and what the test will show.
- Never download someone else's reel to re-upload it. To feature a guest's reel, use Instagram's native repost (A).
- Never scrape Instagram or TikTok, and never bypass bot detection. Trend research = TikTok Creative Center, in-app trending audio, and Stepan's own feed.
- Café reels that make offers: check with Stepan, since money, prices and promises go to real customers.
- **People on camera:** staff have given their OK. Stepan asks each guest after filming whether they can be posted. A guest without a yes is cut or blurred before posting. No minors without a parent's yes.

## Finished edits (captions already burned in)
When the input is an already-edited video, not raw clips:
- Cut only where nothing is spoken and no text is on screen. List those spots with timestamps and ask Stepan first.
- To shorten a silent montage, speed up the picture and cut the audio on whole beats, so the music never jumps.
- Time any blur or overlay to the exact shot edges (scene detect), never to speech.
- Example: `~/claude-kit/docs/examples/build_v3.py`.

## References
| File | Read when |
|---|---|
| `references/rules.md` | The full rule list with grades and finding IDs (short form of the playbook) |
| `references/types.md` | Shot structures for talking head, vlog/B-roll and business promo |
| `references/hooks-sl.md` | Writing hooks (patterns plus Slovene examples, LEAD) |
| `references/pipeline.md` | Editing raw clips: commands, edl.json fields, review steps, caption styles |
| `references/post-and-test.md` | Caption/post checklist, Trial-reel test design, metrics log |
