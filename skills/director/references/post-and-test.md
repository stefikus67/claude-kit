# Post pack and test loop

## Post pack (Claude writes it; Stepan posts from the phone)
- [ ] **Cover frame:** the hook frame or a clear face plus 3-6 words. Check it in the 4:5 grid crop.
- [ ] **Caption:** the first line restates the hook. Use keywords people would search, said out loud and also in the caption (Instagram: "in your content, your caption, your bio, and your hashtags", A). Whether Slovene keywords are searchable is unknown.
- [ ] **Hashtags:** up to 5, specific (B: they help show what the post is about, not reach).
- [ ] **Collab:** a partner account if there is one (A/B).
- [ ] **Location tag:** yes; it costs nothing and has no proven reach effect.
- [ ] **Audio:** for trending audio, add it in the Instagram app at posting and keep the voice louder. Note: in-app music is added by Stepan.
- [ ] **No other app's watermark** in the file (A).
- [ ] **Slovene text proofread** (prompt-forge section 5).
- [ ] **Trial or normal:** a test is a Trial. A proven format goes to followers.
- [ ] **Story share:** after posting (B, "helps a bit").

## Test design (Trial reels)
- Trial reels are shown to non-followers first. Metrics (views, likes, comments, shares) arrive after about 24 h, and Instagram can auto-share a trial with followers if it does well in the first 72 h (opt-in) (A).
- Trials get less reach than normal reels, so **compare trials only with trials** (B).
- They need a professional account (B, vendor), which is Stepan's task 7.
- **One variable per pair:** hook A vs hook B, SL vs EN, 20 s vs 45 s cut, caption style, or a cover.
- Post both versions within an hour of each other, on the same weekday.
- **Read at 24 h and 72 h:** views, shares, likes, comments. Check whether skip rate, watch time and the retention curve show for trials too: Instagram's Apr 2026 Insights update did not cover trials (S1-66). If they're missing, judge by views, shares and watch time.
- A single pair is noise. Call a winner only when the same direction repeats in 3 pairs (our rule, no source).
- Seasonal or short-lived items (on sale for fewer than 6 weeks): run one pair, read it, decide, and log it as "low confidence".

## Metrics log
Keep one row per reel in `~/claude-kit/reels/reels-log.csv`:
```
date,reel,type,lang,trial,variable,variant,length_s,views_24h,reach_24h,skip_rate,avg_watch_s,shares,likes,comments,saves,follows,notes
```
- **Sends per reach** = shares / reach. This is the idea test (B, Mosseri).
- **Likes per reach** = follower satisfaction (our reading).
- **Average watch time / length** = hold, and the drop-off second shows which beat lost people.
- Every Sunday: Claude reads the log, names what changed, and picks the next 2 tests.
