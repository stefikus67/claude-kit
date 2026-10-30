"""Claim ledger + team findings bus. Python 3 stdlib only.

Commands (run with: python -X utf8 ledger.py <command> ...):
  init   [--ledger L]                      create an empty ledger CSV
  add    [--ledger L] [--update|--check] F.jsonl ...   validate + append claim rows
  taint  [--ledger L] [--dry]              mark claims that depend on failed claims
  sheet  [--ledger L] [--out F.md] [--scope-col C]    claim sheet: USE / USE CORRECTED / ASSUMPTION / CHECK FIRST / DO NOT USE / UNCHECKED
  stats  [--ledger L]                      counts by verdict, type, severity
  numcheck [--ledger L] DELIVERABLE.md     numbers in a deliverable that are not backed by a usable ledger row
  digest FINDINGS_DIR [--out DIGEST.md]    merge findings/<person>.jsonl into one digest; flags duplicates and conflicts

Verdict vocabulary (first word counts): VERIFIED, PARTIAL, CORRECTED, LABELED_ASSUMPTION, UNSUPPORTED,
CONTRADICTED, CIRCULAR, NEEDS_HUMAN, DISPUTED (A vs B), TAINTED, or empty (not checked).
"""
import csv, json, os, re, sys, collections

COLS = ["id", "file", "line", "exact_text", "claim_type", "depends_on", "cited_source", "verdict",
        "source_url", "quote", "accessed", "evidence", "correct_value", "severity", "checker", "scope", "notes"]
TYPES = {"EXTERNAL_FACT", "CALCULATION", "INTERNAL_FACT", "ASSUMPTION", "STRATEGY_OPINION", "QUOTE"}
VERDICTS = {"VERIFIED", "PARTIAL", "CORRECTED", "LABELED_ASSUMPTION", "UNSUPPORTED", "CONTRADICTED",
            "CIRCULAR", "NEEDS_HUMAN", "DISPUTED", "TAINTED", ""}
BAD = {"UNSUPPORTED", "CONTRADICTED", "CIRCULAR"}
OK = {"VERIFIED", "PARTIAL", "CORRECTED"}
FIND_COLS = ["id", "who", "time", "question_id", "claim", "value", "unit", "as_of", "source_url", "quote",
             "source_type", "grade", "impact", "status", "notes"]


def arg(name, default=None):
    a = sys.argv
    if name in a:
        i = a.index(name); v = a[i + 1]; del a[i:i + 2]; return v
    return default


def flag(name):
    if name in sys.argv:
        sys.argv.remove(name); return True
    return False


def load(path):
    if not os.path.exists(path):
        sys.exit(f"no ledger at {path} (run: init --ledger {path})")
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def save(path, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n", extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def base(v):
    return (v or "").strip().split(" ")[0].rstrip(";:,")


def bucket(v, notes=""):
    if "CONFLICT" in (notes or ""): return "CHECK FIRST"
    v = (v or "").strip(); b = base(v)
    if b == "VERIFIED": return "USE"
    if b in ("PARTIAL", "CORRECTED"): return "USE CORRECTED"
    if b == "LABELED_ASSUMPTION": return "ASSUMPTION"
    if b == "DISPUTED":
        parts = [p for p in re.findall(r"[A-Z_]+", v.split("(", 1)[-1]) if p not in ("VS", "DISPUTED")]
        if parts and all(p in OK for p in parts):
            return "USE" if all(p == "VERIFIED" for p in parts) else "USE CORRECTED"
        return "CHECK FIRST"
    if b == "NEEDS_HUMAN": return "CHECK FIRST"
    if b in BAD or b == "TAINTED" or "TAINTED" in v: return "DO NOT USE"
    return "UNCHECKED"


def cmd_init(ledger):
    if os.path.exists(ledger): sys.exit(f"{ledger} exists; not overwriting")
    os.makedirs(os.path.dirname(os.path.abspath(ledger)), exist_ok=True)
    save(ledger, []); print(f"created {ledger}")


def cmd_add(ledger, files, update=False, check=False):
    rows = load(ledger) if os.path.exists(ledger) else []
    ids = {r["id"]: i for i, r in enumerate(rows)}
    added = replaced = 0
    for path in files:
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"): continue
                try:
                    o = json.loads(line)
                except json.JSONDecodeError as e:
                    sys.exit(f"{path}:{n}: bad JSON ({e})")
                bad = set(o) - set(COLS)
                if bad: sys.exit(f"{path}:{n}: unknown columns {sorted(bad)}")
                if not o.get("id"): sys.exit(f"{path}:{n}: missing id")
                if o.get("claim_type") and o["claim_type"] not in TYPES:
                    sys.exit(f"{path}:{n}: bad claim_type {o['claim_type']} (allowed: {sorted(TYPES)})")
                if base(o.get("verdict", "")) not in VERDICTS:
                    sys.exit(f"{path}:{n}: bad verdict {o.get('verdict')}")
                if base(o.get("verdict", "")) in OK and not (o.get("source_url") or o.get("evidence")):
                    sys.exit(f"{path}:{n}: {o['id']} has verdict {o['verdict']} but no source_url/evidence")
                if o["id"] in ids:
                    if not update: sys.exit(f"{path}:{n}: duplicate id {o['id']} (use --update)")
                    old = rows[ids[o["id"]]]
                    for c in COLS:
                        if c in o: old[c] = str(o[c])
                    replaced += 1
                else:
                    rows.append({c: str(o.get(c, "")) for c in COLS}); ids[o["id"]] = len(rows) - 1; added += 1
    if check:
        print(f"check OK: {added} new, {replaced} updated"); return
    save(ledger, rows); print(f"ledger {ledger}: {len(rows)} rows (+{added}, {replaced} updated)")


def cmd_taint(ledger):
    dry = flag("--dry"); rows = load(ledger); idx = {r["id"]: r for r in rows}; memo = {}; review = {}

    def roots(cid, seen):
        if cid in memo: return memo[cid]
        if cid in seen: return set()
        seen = seen | {cid}; r = idx.get(cid); out = set()
        if r is None: return out
        for d in [x.strip() for x in r["depends_on"].split(",") if x.strip()]:
            dr = idx.get(d)
            if dr is None: continue
            if base(dr["verdict"]) in BAD: out.add(d)
            elif base(dr["verdict"]) == "CORRECTED": review.setdefault(cid, set()).add(d)
            out |= roots(d, seen)
        memo[cid] = out; return out

    n = 0
    for r in rows:
        t = roots(r["id"], set())
        if t and base(r["verdict"]) not in BAD:
            n += 1; tag = "TAINTED by " + ",".join(sorted(t))
            if "TAINT:" not in r["notes"]: r["notes"] = (r["notes"] + " | " if r["notes"] else "") + "TAINT: " + tag
            if base(r["verdict"]) in ("", "VERIFIED", "PARTIAL", "LABELED_ASSUMPTION", "NEEDS_HUMAN") and "TAINTED" not in r["verdict"]:
                r["verdict"] = tag if not r["verdict"] else r["verdict"] + "; " + tag
            print(f"  {r['id']}: {tag}")
    for cid, deps in review.items():
        r = idx[cid]
        if "REVIEW:" not in r["notes"]:
            r["notes"] = (r["notes"] + " | " if r["notes"] else "") + "REVIEW: depends on corrected " + ",".join(sorted(deps))
        print(f"  {cid}: review, depends on corrected {','.join(sorted(deps))} (check the corrected wording still supports it)")
    if not dry: save(ledger, rows)
    print(f"tainted {n} claims, {len(review)} to review" + (" (dry run)" if dry else ""))


def cmd_sheet(ledger):
    out = arg("--out"); scope_col = arg("--scope-col", "scope")
    rows = load(ledger); order = ["USE", "USE CORRECTED", "ASSUMPTION", "CHECK FIRST", "DO NOT USE", "UNCHECKED"]
    scopes = sorted({r.get(scope_col, "") or "all" for r in rows})
    c = collections.Counter(((r.get(scope_col) or "all"), bucket(r["verdict"], r.get("notes", ""))) for r in rows)
    L = ["# Claim sheet", "", "USE = verified. USE CORRECTED = use only the corrected wording. ASSUMPTION = say \"we estimate\". "
         "CHECK FIRST = checks disagree or a human must look. DO NOT USE = unsupported, contradicted or tainted. UNCHECKED = not checked.", "",
         "| status | " + " | ".join(scopes) + " |", "|---|" + "---|" * len(scopes)]
    for s in order: L.append(f"| {s} | " + " | ".join(str(c[(sc, s)]) for sc in scopes) + " |")
    for sc in scopes:
        L.append(f"\n## {sc}\n")
        for s in order:
            sel = [r for r in rows if (r.get(scope_col) or "all") == sc and bucket(r["verdict"], r.get("notes", "")) == s]
            if not sel: continue
            L += [f"\n### {s} ({len(sel)})\n", "| id | claim | use this wording | source |", "|---|---|---|---|"]
            for r in sel:
                src = r["source_url"] or (re.search(r"https?://\S+", r["evidence"] or "") or [""])[0] if not r["source_url"] else r["source_url"]
                cell = lambda t, k: (t or "").replace("|", "/").replace("\n", " ")[:k]
                L.append(f"| {r['id']} | {cell(r['exact_text'], 170)} | {cell(r['correct_value'], 240)} | {cell(src, 110)} |")
    text = "\n".join(L) + "\n"
    if out:
        open(out, "w", encoding="utf-8").write(text); print(f"wrote {out}")
    else:
        print(text)


def cmd_stats(ledger):
    rows = load(ledger)
    for col, f in (("bucket", lambda r: bucket(r["verdict"], r.get("notes", ""))), ("verdict", lambda r: base(r["verdict"]) or "(none)"),
                   ("claim_type", lambda r: r["claim_type"] or "(none)"), ("severity", lambda r: r["severity"] or "(none)")):
        print(f"\n{col}:"); [print(f"  {k:22} {v}") for k, v in collections.Counter(map(f, rows)).most_common()]
    print(f"\ntotal rows: {len(rows)}")


NUM = re.compile(r"(?<![\w.])[-+]?\d[\d.,  ]*\d(?:\s?%)?|(?<![\w.])\d(?:\s?%)?")


def norm(n):
    n = n.replace(" ", "").replace(" ", "").replace("%", "")
    if re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", n): n = n.replace(".", "").replace(",", ".")   # 1.234,5 (sl)
    else: n = n.replace(",", "")                                                               # 1,234.5 (en)
    return n.rstrip(".")


def cmd_numcheck(ledger, deliverable):
    rows = load(ledger); good, wrong, pending = set(), {}, {}
    nums = lambda s: {norm(m) for m in NUM.findall(s or "")}
    for r in rows:
        b = bucket(r["verdict"], r.get("notes", ""))
        orig, corr = nums(r["exact_text"]), nums(r["correct_value"])
        if b == "USE": good |= orig | corr
        elif b == "ASSUMPTION": good |= orig
        elif b == "USE CORRECTED":
            good |= corr
            if corr:
                for x in orig - corr: wrong.setdefault(x, []).append(r["id"])
            else: good |= orig   # PARTIAL without a corrected wording: numbers stand
        elif b == "DO NOT USE":
            for x in orig: wrong.setdefault(x, []).append(r["id"])
        else:
            for x in orig: pending.setdefault(x, []).append(r["id"])
    text = open(deliverable, encoding="utf-8").read(); out = []
    skip = re.compile(r"\b\d{1,2}:\d{2}\b|\b\d{1,2}\.\s?\d{1,2}\.\s?\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b|https?://\S+|`[^`]*`")
    for i, line in enumerate(text.splitlines(), 1):
        for m in NUM.findall(skip.sub(" ", line)):
            x = norm(m)
            if len(x) < 2 or re.fullmatch(r"(19|20)\d\d", x) or x in good: continue
            if x in wrong: out.append(f"  L{i}: {m.strip()}  -> WRONG: appears only in corrected/failed claims {wrong[x]}; use the corrected wording")
            elif x in pending: out.append(f"  L{i}: {m.strip()}  -> CHECK FIRST: claim {pending[x]} is not settled")
            else: out.append(f"  L{i}: {m.strip()}  -> UNBACKED: no ledger row | {line.strip()[:110]}")
    print(f"numcheck {deliverable}: numbers backed by USE / corrected wording / labelled assumptions pass silently.")
    print("\n".join(out) if out else "  nothing to fix")
    print(f"{sum('WRONG' in o for o in out)} wrong, {sum('CHECK FIRST' in o for o in out)} check-first, {sum('UNBACKED' in o for o in out)} unbacked")


def cmd_digest(fdir):
    out = arg("--out", os.path.join(fdir, "DIGEST.md")); items = []
    for fn in sorted(os.listdir(fdir)):
        if not fn.endswith(".jsonl"): continue
        for n, line in enumerate(open(os.path.join(fdir, fn), encoding="utf-8"), 1):
            line = line.strip()
            if not line or line.startswith("#"): continue
            try: o = json.loads(line)
            except json.JSONDecodeError: print(f"skip {fn}:{n} bad JSON"); continue
            o.setdefault("who", fn[:-6]); items.append(o)
    byq = collections.defaultdict(list)
    for o in items: byq[o.get("question_id") or "UNASSIGNED"].append(o)
    L = [f"# Findings digest ({len(items)} findings, auto-built; do not edit)", "",
         "Flags: CHANGES-ANSWER = impact marked changes-answer; CONFLICT = same question, different values; NO-SOURCE = missing url or quote.", ""]
    hot = [o for o in items if (o.get("impact") or "").startswith("changes")]
    if hot:
        L.append("## CHANGES-ANSWER (read first)\n")
        for o in hot: L.append(f"- **{o.get('id')}** [{o.get('question_id')}] {o.get('claim')} ({o.get('who')}, {o.get('time','')}) {o.get('source_url','')}")
        L.append("")
    for q in sorted(byq):
        g = byq[q]; vals = {str(o.get("value", "")).strip() for o in g if str(o.get("value", "")).strip()}
        L.append(f"## {q}" + ("  CONFLICT: " + " vs ".join(sorted(vals)) if len(vals) > 1 else ""))
        for o in g:
            ns = "" if (o.get("source_url") and o.get("quote")) else " NO-SOURCE"
            L.append(f"- {o.get('id')} [{o.get('grade','?')}/{o.get('status','new')}] {o.get('claim')}"
                     f"{' = ' + str(o.get('value')) + ' ' + str(o.get('unit','')) if o.get('value') else ''}"
                     f" ({o.get('who')}){ns} {o.get('source_url','')}")
        L.append("")
    open(out, "w", encoding="utf-8").write("\n".join(L)); print(f"wrote {out}: {len(items)} findings, {len(byq)} questions, {len(hot)} changes-answer")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"): print(__doc__); sys.exit(0)
    cmd = sys.argv.pop(1); ledger = arg("--ledger", "ledger.csv")
    if cmd == "init": cmd_init(ledger)
    elif cmd == "add":
        u, c = flag("--update"), flag("--check"); cmd_add(ledger, sys.argv[1:], u, c)
    elif cmd == "taint": cmd_taint(ledger)
    elif cmd == "sheet": cmd_sheet(ledger)
    elif cmd == "stats": cmd_stats(ledger)
    elif cmd == "numcheck": cmd_numcheck(ledger, sys.argv[1])
    elif cmd == "digest": cmd_digest(sys.argv[1])
    else: sys.exit(f"unknown command {cmd}; run --help")
