"""Report script lines a player can see that the dictionary still leaves in English.

Usage: python check_coverage.py
Writes extract/missing_messages.txt and prints the count.
"""
import glob
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "build", "BB_CN")
DATA = os.path.join(ROOT, "extract", "data.tsv")
OUT = os.path.join(ROOT, "extract", "missing_messages.txt")
MSG = re.compile(r"(?:message|choice)\((.*?)\)\s*;", re.S)


def unesc(s):
    return s.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")


def load_exact():
    exact = set()
    for path in glob.glob(os.path.join(BUILD, "*.tsv")):
        for line in open(path, encoding="utf-8"):
            if not line.strip() or line.startswith("#") or "\t" not in line:
                continue
            exact.add(unesc(line.split("\t", 1)[0]))
    return exact


def main():
    exact = load_exact()
    bodies = {}
    for raw in open(DATA, encoding="utf-8"):
        if "\t" not in raw:
            continue
        file, path, val = raw.rstrip("\n").split("\t", 2)
        if not file.endswith(".bbm") or not path.endswith(".script"):
            continue
        for m in MSG.finditer(unesc(val)):
            args = m.group(1).split("|")
            if len(args) < 2:
                continue
            body = args[1].strip()
            if len(body) < 2 or not re.search(r"[A-Za-z]{3}", body):
                continue
            # The extractor stops at ")\s*;". A message that is not closed that way
            # swallows the following script. That text is never shown as one block.
            if re.search(r"message\(|ifCheck|ifcheck|setBehaviour|zoomEvent|choice\(|\bwait\(", body):
                continue
            bodies.setdefault(body, file)
    missing = [(en, src) for en, src in bodies.items() if en not in exact and ('"' + en + '"') not in exact]
    with open(OUT, "w", encoding="utf-8") as f:
        for en, src in sorted(missing, key=lambda x: (x[1], x[0])):
            f.write(src + "\t" + en.replace("\n", "\\n") + "\n")
    print(len(bodies), "script lines,", len(missing), "still English, across", len(Counter(s for _, s in missing)), "maps")
    print("list:", OUT)


if __name__ == "__main__":
    main()
