"""Write charset.txt: all of GB2312 plus every character used by the translation files."""
import glob
import os

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRA = "，。！？：；、“”‘’（）【】《》「」『』…—～·％＋－×÷＝＜＞￥＄＃＆＊＠０１２３４５６７８９"

chars = set(EXTRA)
for hi in range(0xA1, 0xF8):
    for lo in range(0xA1, 0xFF):
        try:
            chars.add(bytes([hi, lo]).decode("gb2312"))
        except UnicodeDecodeError:
            pass
for path in glob.glob(os.path.join(HERE, "translation", "*.tsv")) + glob.glob(os.path.join(HERE, "translation", "*.jsonl")) + glob.glob(os.path.join(HERE, "translation", "*.md")) + [os.path.join(HERE, "patch", "BB_CN.cs")]:
    with open(path, encoding="utf-8") as f:
        chars.update(f.read())
chars = sorted(c for c in chars if ord(c) > 126 and not c.isspace() and c != "\ufeff")
with open(os.path.join(HERE, "charset.txt"), "w", encoding="utf-8") as f:
    f.write("".join(chars))
print(len(chars), "characters")
