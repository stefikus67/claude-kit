"""Install the kit's Claude Code parts for this user: skills, the CLAUDE.md block, and settings.

  python setup/configure_claude.py [--claude-dir DIR]     (default DIR: ~/.claude)

- skills/<name> -> DIR/skills/<name> (copied; a different existing skill of the same name is backed up first)
- claude/CLAUDE.md -> merged into DIR/CLAUDE.md between claude-kit markers (the rest of the file is kept)
- DIR/settings.json: "enableWorkflows": true (needed by the council skill); everything else is kept, backup written
Safe to re-run: it replaces only what the kit owns.
"""
import argparse, filecmp, json, os, shutil, time

KIT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
START, END = "<!-- claude-kit:start -->", "<!-- claude-kit:end -->"


def same_tree(a, b):
    c = filecmp.dircmp(a, b)
    return not (c.left_only or c.right_only or c.diff_files) and all(same_tree(os.path.join(a, d), os.path.join(b, d)) for d in c.common_dirs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claude-dir", default=os.path.join(os.path.expanduser("~"), ".claude"))
    d = ap.parse_args().claude_dir
    stamp = time.strftime("%Y%m%d-%H%M%S")
    os.makedirs(os.path.join(d, "skills"), exist_ok=True)

    for name in sorted(os.listdir(os.path.join(KIT, "skills"))):
        src, dst = os.path.join(KIT, "skills", name), os.path.join(d, "skills", name)
        marker = os.path.join(dst, ".claude-kit")
        if os.path.lexists(dst):
            if os.path.isdir(dst) and not os.path.islink(dst) and (os.path.exists(marker) or same_tree(src, dst)):
                shutil.rmtree(dst)
            else:
                bak = os.path.join(d, "skills-backup-" + stamp, name)
                os.makedirs(os.path.dirname(bak), exist_ok=True)
                shutil.move(dst, bak)
                print(f"backed up your existing skill {name} -> {bak}")
        shutil.copytree(src, dst)
        open(marker, "w").write("installed by claude-kit; re-run setup to update\n")
        print(f"skill {name}")

    block = open(os.path.join(KIT, "claude", "CLAUDE.md"), encoding="utf-8").read().strip()
    md = os.path.join(d, "CLAUDE.md")
    old = open(md, encoding="utf-8").read() if os.path.exists(md) else ""
    if START in old and END in old:
        new = old[:old.index(START)] + block + old[old.index(END) + len(END):]
    else:
        new = (old.rstrip() + "\n\n" if old.strip() else "") + block + "\n"
    if new != old:
        if old:
            shutil.copy2(md, md + ".bak-" + stamp)
        open(md, "w", encoding="utf-8", newline="\n").write(new)
    print(f"CLAUDE.md block in {md}")

    sp = os.path.join(d, "settings.json")
    s = {}
    if os.path.exists(sp):
        raw = open(sp, encoding="utf-8").read()
        s = json.loads(raw) if raw.strip() else {}
    if s.get("enableWorkflows") is not True:
        if os.path.exists(sp):
            shutil.copy2(sp, sp + ".bak-" + stamp)
        s["enableWorkflows"] = True
        open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(s, indent=2) + "\n")
    print(f"settings: enableWorkflows on ({sp})")


if __name__ == "__main__":
    main()
