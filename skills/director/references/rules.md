# Rules with evidence (short form of VIRALITY-PLAYBOOK v2)

Full text, caveats and the claims that failed: `~/claude-kit/docs/VIRALITY-PLAYBOOK.md`.
Finding IDs point to `research/virality/findings/S*.jsonl`.
- **A:** a platform or paper says it.
- **B:** a practitioner, press, or a vendor (marked).
- **LEAD:** untested.
- **ads:** from ad research; may not transfer to organic.

## Ranking (what the platforms say)
| Rule | Grade | IDs |
|---|---|---|
| Instagram lists watch time, retention, shares, likes and comments for non-follower ranking; no weights | A | S1-01 |
| Mosseri's top three: watch time, likes, sends. Sends slightly more for non-followers, likes for followers | B | S1-07, S1-08, S1-10 |
| Sends per reach correlate with reach more than anything else (in his experience) | B | S1-09 |
| A reel is first shown to a small non-follower audience Instagram predicts will enjoy it | A | S1-02 |
| Most Reels engagement increasingly happens on day one | B | S1-14 |
| Reposts, third-party watermarks, aggregator accounts and low resolution are recommended less | A | S1-21, S1-22, S1-29, S1-31 |
| TikTok: unoriginal or reused content without anything new is ineligible for the For You feed | A | S2-11, S2-15, S2-17 |
| TikTok: finishing a longer video is a strong signal; trim lulls | A | S2-03, S2-07 |
| TikTok: follower count is not a direct factor (2020 page) | A | S2-01 |
| Reels up to 3 min can be recommended; Instagram's guide (reported) calls 15-60 s the sweet spot for most formats | A / B | S1-16, S1-19 |
| Hashtags do not significantly increase reach; up to 5; the FAQ still says relevant trending ones can help | B / A | S1-38..S1-41 |
| Trending audio can impact distribution | A | S1-48, S2-55 |
| Hidden or off-screen keyword text on TikTok can get a video flagged as spam | A | S2-19 |
| Collab posts can be recommended; slight bias to the inviting account | A / B | S1-50, S1-51 |
| Posting a reel to Stories helps a bit; hacks "sometimes work, usually don't" | B | S1-70, S1-69 |

## Craft (what practitioners and studies say)
| Rule | Grade | IDs |
|---|---|---|
| Intro works like a thumbnail; visual hook that works without sound; about 3 s, centred, no more than about 3 objects | B | S4-08, S4-11, S4-12 |
| Show, don't announce, what the video contains | B (long-form) | S4-02 |
| Chain beats with "but/therefore"; keep opening new problems; lists of 3/5/7 | B | S4-14, S4-25, S4-26 |
| End right after the payoff; trimming a dead last second helped one creator's retention (83 to 88%) | B | S4-06, S4-17 |
| Rewatches can push retention above 100% | B (anecdote) | S4-18 |
| Captions: +12% view time in Meta's tests; a review of 100+ studies shows better comprehension (instructional video) | A (ads / not social) | S3-06, S3-23 |
| Over 75% of Reels views are sound on, so audio matters too | A (ads page) | S3-08 |
| On-screen text: 5-10 words/s (TikTok ads guidance) | A (ads) | S2-34 |
| DIY, not over-polished, fits (TikTok ads); TikTok-first lo-fi 9:16 creative got about 3.3x clicks or shares | A (ads) | S2-35, S3-14 |
| Avoid static talking heads; quick demos with captions often outperform them | A (ads, no data) | S2-32 |
| Shared news content: high arousal (awe, anger), positive, useful, interesting, surprising; sad content shared less | A (news email, 2008) | S3-33..S3-36 |
| Curiosity gap: a middling amount of information revealed wins on headline clicks; flagged clickbait does not reliably win | A (headlines) | S3-44, S3-45 |
| Voiceover tells one story while the images add a second layer (dual narrative) | B | S4-21 |
| Hook formula lists | LEAD | S4-36..S4-47 |

## Local business
| Rule | Grade | IDs |
|---|---|---|
| Behind the scenes, process and staff build trust; process reveals perform well; 80/20 value vs promo; local creator partnerships | A (TikTok guidance) | S5-25, S5-26 |
| Measured visit lifts exist only for chains in paid campaigns, so measure the café's result with a code or a till question | A + our method | S5-22, S5-23 |
| Location tags: no evidence they raise reach; Instagram Map is US-first; TikTok Nearby is not confirmed in SI | A | S1-52, S5-27, S5-32 |
| Slovene is not in Meta AI reel translation (2026); 2022 caption lists exclude it | A | S5-11, S5-12, S5-14, S5-15 |
| Slovenia ad reach: IG about 0.72M, TikTok about 0.54M (18+), YouTube about 1.57M (Oct 2025) | A | S5-01..S5-03 |

## Our design choices (no evidence, marked "ours" wherever used)
- **Loop ending:** the last line runs into the first.
- **CTA:** a specific action (comment a keyword, show the reel at the till) instead of "follow for more".
- **Punch-in:** a 110-120% crop on each new sentence of a talking head.
- **Speaking rate:** Slovene speech at about 2-2.5 words/s for script length. Measured in the spike: FLEURS read speech ran at about 2 words/s.
- **Café visits:** measured with a code or a till question.
- **Calling a winner:** only after 3 Trial pairs point the same way. Exception: seasonal items, one pair, logged as "low confidence".

## Did not survive (don't repeat these)
- "85% watch without sound"
- "hashtags boost reach"
- "post at 6 pm"
- "the ideal length is N s"
- "faster cuts raise retention"
- "proven hook formulas"
- "1.7 s attention span"

See playbook section 3.
