"""Render reel captions from a words.json with HyperFrames.

usage: render_captions.py WORDS.json OUT.(mp4|webm|mov) --style klasika|pill|highlight|pop
         [--bg photo.jpg|clip.mp4] [--audio audio.wav] [--start S --end S] [--accent #FFD400] [--top 1180]
- With --bg: a finished preview (background with a slow zoom, audio, captions).
- Without --bg and with .webm/.mov output: a transparent caption layer to overlay with ffmpeg.
Words are shifted so --start becomes 0. Runs `npx hyperframes render` from ~/claude-kit/tools/reel (local install, telemetry off).
"""
import argparse, json, os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
REEL = os.path.dirname(HERE)
STYLES = ("klasika", "pill", "highlight", "pop")
ACCENTS = {"klasika": "#FFFFFF", "pill": "#1C1E1D", "highlight": "#E5143A", "pop": "#FFD400"}


def build(words, style, duration, bg=None, audio=None, accent=None, top=1180):
    html = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    bg_html = ""
    if bg:
        tag = "video" if bg.lower().endswith((".mp4", ".mov", ".webm")) else "img"
        extra = f' class="clip" data-start="0" data-duration="{duration}" muted playsinline' if tag == "video" else ""
        bg_html += f'<{tag} id="bg" src="{os.path.basename(bg)}"{extra}></{tag}>' if tag == "video" else f'<img id="bg" src="{os.path.basename(bg)}" />'
        bg_html += '<div id="shade"></div>'
    if audio:
        bg_html += f'<audio class="clip" src="{os.path.basename(audio)}" data-start="0" data-duration="{duration}" data-has-audio="true"></audio>'
    for k, v in {"__STYLE__": style, "__DURATION__": f"{duration:.2f}", "__ACCENT__": accent or ACCENTS[style],
                 "__WORDS__": json.dumps(words, ensure_ascii=False), "__BG__": bg_html, "__TOP__": str(top)}.items():
        html = html.replace(k, v)
    return html


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("words"); ap.add_argument("out")
    ap.add_argument("--style", choices=STYLES, default="klasika")
    ap.add_argument("--bg"); ap.add_argument("--audio")
    ap.add_argument("--start", type=float, default=0.0); ap.add_argument("--end", type=float)
    ap.add_argument("--accent"); ap.add_argument("--top", type=int, default=1180)
    ap.add_argument("--quality", default="standard")
    ap.add_argument("--at", help="with OUT.png: snapshot these times (s, comma list) into one strip instead of rendering")
    a = ap.parse_args()
    data = json.load(open(a.words, encoding="utf-8"))
    end = a.end or data.get("duration") or max(w["e"] for w in data["words"])
    words = [dict(w=w["w"], s=round(w["s"] - a.start, 3), e=round(w["e"] - a.start, 3)) for w in data["words"] if w["s"] >= a.start and w["e"] <= end]
    dur = round(end - a.start, 2)
    proj = tempfile.mkdtemp(prefix="reelcap-", dir=os.path.join(REEL, "tmp") if os.path.isdir(os.path.join(REEL, "tmp")) else None)
    try:
        audio = None
        if a.audio:  # trim the audio to the window so the composition starts at 0
            audio = os.path.join(proj, "audio.m4a")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(a.start), "-t", str(dur), "-i", a.audio, "-c:a", "aac", "-b:a", "192k", audio], check=True)
        bg = None
        if a.bg:
            bg = os.path.join(proj, "bg" + os.path.splitext(a.bg)[1].lower())
            shutil.copy(a.bg, bg)
        open(os.path.join(proj, "index.html"), "w", encoding="utf-8").write(build(words, a.style, dur, bg, audio, a.accent, a.top))
        json.dump({"name": "reelcap"}, open(os.path.join(proj, "meta.json"), "w"))
        fmt = os.path.splitext(a.out)[1].lstrip(".").lower()
        env = dict(os.environ, HYPERFRAMES_SKIP_SKILLS="1")
        if fmt == "png":
            snap = os.path.join(proj, "snaps")
            r = subprocess.run(["npx", "hyperframes", "snapshot", proj, "-o", snap, "--at", a.at or "1,3,5", "--no-end"], cwd=REEL, env=env, shell=(os.name == "nt"), capture_output=True, text=True)
            pngs = sorted(p for p in os.listdir(snap) if p.endswith(".png")) if os.path.isdir(snap) else []
            if not pngs: sys.exit(f"snapshot failed: {r.stdout[-800:]} {r.stderr[-800:]}")
            ins = sum((["-i", os.path.join(snap, p)] for p in pngs), [])
            subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", "".join(f"[{i}:v]scale=360:640[v{i}];" for i in range(len(pngs))) + "".join(f"[v{i}]" for i in range(len(pngs))) + f"hstack={len(pngs)}" if len(pngs) > 1 else "scale=360:640", a.out], check=True)
            print(f"{a.style}: snapshots {', '.join(pngs)} -> {a.out}")
            return
        cmd = ["npx", "hyperframes", "render", proj, "-o", os.path.abspath(a.out), "--format", fmt, "--quiet"]
        if fmt == "mp4": cmd += ["--quality", a.quality]
        r = subprocess.run(cmd, cwd=REEL, env=env, shell=(os.name == "nt"))
        if r.returncode: sys.exit(f"render failed ({r.returncode}); project kept at {proj}")
        print(f"{a.style}: {len(words)} words, {dur} s -> {a.out}")
    finally:
        if os.path.exists(a.out): shutil.rmtree(proj, ignore_errors=True)


if __name__ == "__main__":
    main()
