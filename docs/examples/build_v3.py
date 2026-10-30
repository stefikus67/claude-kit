"""v3 (= v2 with a tracked blur instead of the soft-mask blur): Stepan's own edit with only text-free trims.
- calling montage (37.35-43.65) sped up; audio cut by 8 beats (129.2 BPM) so the music stays continuous
- one beat of silent DM screen removed (73.17-73.66)
- captions added on the handshake passage; soft blur on the revenue sheet + inbox
"""
import subprocess

SRC = "out/opener-1080x1920.mp4"
OUT = "out/opener-v3.mp4"
END = 105.0
MONT = (37.35, 43.65)          # video sped up here
ACUT = (38.17, 41.91)          # audio removed: 8 beats, on beat
DMCUT = (73.17, 73.66)         # one beat, audio + video
XF = 0.03                      # audio crossfade at the joins
CAPS = [(67.16, 67.92), (67.94, 68.84), (68.86, 69.48), (69.50, 70.42), (70.42, 70.86)]
SHEET = "scratch/sheet_blurred.mkv"   # tracked blur, frames 76.50-80.133 (track_blur.py)
SHEET_T0 = 76.50

mont_out = (MONT[1] - MONT[0]) - (ACUT[1] - ACUT[0])
speed = (MONT[1] - MONT[0]) / mont_out

inputs = ["-i", SRC] + sum((["-i", f"scratch/caps/c{i}.png"] for i in range(len(CAPS))), []) + ["-i", SHEET]
f = []
f.append(f"[{len(CAPS) + 1}:v]setpts=PTS-STARTPTS+{SHEET_T0}/TB[sh]")
f.append("[0:v][sh]overlay=0:0:eof_action=pass[vb]")
cur = "[vb]"
for i, (a, b) in enumerate(CAPS):
    f.append(f"{cur}[{i + 1}:v]overlay=0:0:enable='between(t,{a},{b})'[vc{i}]")
    cur = f"[vc{i}]"

vseg = [(0, MONT[0], 1.0), (MONT[0], MONT[1], speed), (MONT[1], DMCUT[0], 1.0), (DMCUT[1], END, 1.0)]
f.append(f"{cur}split={len(vseg)}" + "".join(f"[vs{i}]" for i in range(len(vseg))))
for i, (a, b, s) in enumerate(vseg):
    f.append(f"[vs{i}]trim={a}:{b},setpts=(PTS-STARTPTS)/{s:.4f},fps=60[v{i}]")
f.append("".join(f"[v{i}]" for i in range(len(vseg))) + f"concat=n={len(vseg)}:v=1:a=0[v]")

h = XF / 2
aseg = [(0, ACUT[0] + h), (ACUT[1] - h, DMCUT[0] + h), (DMCUT[1] - h, END)]
f.append(f"[0:a]asplit={len(aseg)}" + "".join(f"[as{i}]" for i in range(len(aseg))))
for i, (a, b) in enumerate(aseg):
    f.append(f"[as{i}]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}]")
f.append(f"[a0][a1]acrossfade=d={XF}:c1=tri:c2=tri[a01]")
f.append(f"[a01][a2]acrossfade=d={XF}:c1=tri:c2=tri[a]")

cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(f),
       "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT]
subprocess.run(cmd, check=True)
print(f"montage speed {speed:.2f}x, total {END - (ACUT[1] - ACUT[0]) - (DMCUT[1] - DMCUT[0]):.2f} s")
