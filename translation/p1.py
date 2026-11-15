"""Phase-1 translation chunks.

  python p1.py split            -> p1_NN.en.jsonl (about WORDS words each)
  python p1.py check [NN ...]   -> validate p1_NN.zh.jsonl against p1_NN.en.jsonl
  python p1.py merge <out.tsv>  -> en<TAB>zh lines for the runtime dictionary
"""
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "extract", "phase1.jsonl")
FONT = os.path.join(HERE, "..", "fonts", "fp12", "fusion-pixel-12px-proportional-zh_hans.ttf")
WORDS = 3500
SLOT = re.compile(r"\{\d\}")


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def split():
    entries = load(SRC)
    chunks, cur, words = [], [], 0
    for e in entries:
        w = len(e["en"].split())
        if cur and words + w > WORDS:
            chunks.append(cur)
            cur, words = [], 0
        cur.append(e)
        words += w
    chunks.append(cur)
    for i, c in enumerate(chunks, 1):
        with open(os.path.join(HERE, f"p1_{i:02d}.en.jsonl"), "w", encoding="utf-8") as f:
            for e in c:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        print(f"p1_{i:02d}: {len(c)} entries, {sum(len(e['en'].split()) for e in c)} words, cats {dict(collections.Counter(e['cat'] for e in c))}")


_cmap = None


def font_has(ch):
    global _cmap
    if _cmap is None:
        from fontTools.ttLib import TTFont
        _cmap = set(TTFont(FONT).getBestCmap())
    return ord(ch) < 128 or ord(ch) in _cmap


def check(nums):
    ok = True
    for n in nums:
        en_path = os.path.join(HERE, f"p1_{n}.en.jsonl")
        zh_path = os.path.join(HERE, f"p1_{n}.zh.jsonl")
        errors = []
        if not os.path.exists(zh_path):
            print(f"p1_{n}: missing {os.path.basename(zh_path)}")
            ok = False
            continue
        src = {e["id"]: e for e in load(en_path)}
        try:
            raw = open(zh_path, encoding="utf-8").read()
            if raw.startswith("\ufeff"):
                errors.append("file has a BOM")
            out = [json.loads(l) for l in raw.lstrip("\ufeff").splitlines() if l.strip()]
        except json.JSONDecodeError as ex:
            print(f"p1_{n}: invalid JSON: {ex}")
            ok = False
            continue
        seen = set()
        for o in out:
            i, zh = o.get("id"), o.get("zh")
            if i not in src:
                errors.append(f"{i}: unknown id")
                continue
            if i in seen:
                errors.append(f"{i}: duplicate id")
            seen.add(i)
            if not isinstance(zh, str) or not zh:
                errors.append(f"{i}: empty zh")
                continue
            if zh == "=":
                continue
            en = src[i]["en"]
            if sorted(SLOT.findall(en)) != sorted(SLOT.findall(zh)):
                errors.append(f"{i}: placeholders {SLOT.findall(en)} vs {SLOT.findall(zh)}")
            if en.count("\n") != zh.count("\n"):
                errors.append(f"{i}: {en.count(chr(10))} newlines in en, {zh.count(chr(10))} in zh")
            if "|" in zh:
                errors.append(f"{i}: contains |")
            bad = sorted({c for c in zh if not font_has(c)})
            if bad:
                errors.append(f"{i}: characters not in font: {''.join(bad)}")
            if re.search(r"[A-Za-z]{4,}", SLOT.sub("", zh)) and zh == en:
                errors.append(f"{i}: zh identical to en (use = if it should stay English)")
        missing = [i for i in src if i not in seen]
        if missing:
            errors.append(f"missing ids: {missing[:10]}{'...' if len(missing) > 10 else ''} ({len(missing)})")
        if errors:
            ok = False
            print(f"p1_{n}: {len(errors)} problems")
            for e in errors[:40]:
                print("   ", e)
        else:
            print(f"p1_{n}: OK ({len(out)} entries)")
    return ok


def esc(s):
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")


def merge(out_path):
    rows = {}
    for zh_path in sorted(glob.glob(os.path.join(HERE, "p1_*.zh.jsonl"))):
        src = {e["id"]: e for e in load(zh_path.replace(".zh.", ".en."))}
        for o in load(zh_path):
            if o["zh"] == "=":
                continue
            en, zh = src[o["id"]]["en"].strip(), o["zh"].strip()
            if en and en != zh:
                rows[en] = zh
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Bastard Bonds phase 1 (UI, items, skills, creatures)\n")
        for en, zh in rows.items():
            f.write(esc(en) + "\t" + esc(zh) + "\n")
    print(f"{len(rows)} entries -> {out_path}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "split":
        split()
    elif cmd == "check":
        nums = sys.argv[2:] or sorted(os.path.basename(p)[3:5] for p in glob.glob(os.path.join(HERE, "p1_*.en.jsonl")))
        sys.exit(0 if check(nums) else 1)
    elif cmd == "merge":
        merge(sys.argv[2])
