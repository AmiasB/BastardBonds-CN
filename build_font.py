"""Rebuild the FONT_XBOX_PRE bitmap font (used by every TextMesh) with CJK glyphs.

Usage: python build_font.py <charset.txt> <out_sharedassets0.assets> [preview.png]

Original glyphs are copied over untouched. CJK glyphs come from Fusion Pixel 12px,
rendered without anti-aliasing, then given the same per-row cream gradient and
1px dark-brown outline as the game's Latin letters, with the baseline aligned to
the capitals (fill rows 2-11 above the baseline, row 12 just below it).
"""
import os
import sys

import UnityPy
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from UnityPy.enums import TextureFormat

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "backup", "sharedassets0.assets")
CJK_FONT = os.path.join(HERE, "fonts", "fp12", "fusion-pixel-12px-proportional-zh_hans.ttf")
FONT_ID = 360
TEX_ID = 9

CELL_H = 14
BASELINE = 12
CJK_PX = 12
CJK_ADVANCE = 13
PAD = 1

OUTLINE_RGB = (82, 47, 34)
# Fill colour by cell row, sampled from the capital letters of the original atlas.
ROW_RGB = {
    1: (215, 160, 64), 2: (215, 160, 64), 3: (255, 207, 93), 4: (255, 255, 162), 5: (255, 255, 200),
    6: (255, 255, 219), 7: (255, 255, 208), 8: (255, 255, 178), 9: (255, 250, 151),
    10: (255, 241, 147), 11: (255, 255, 173), 12: (255, 255, 173), 13: (255, 255, 173),
}


def render_cjk(ch, font):
    """Return a (CJK_PX + 2) x CELL_H RGBA glyph, or None if the font has no ink for it."""
    w = CJK_PX + 2
    mask = Image.new("L", (w, CELL_H), 0)
    draw = ImageDraw.Draw(mask)
    draw.fontmode = "1"
    adv = font.getlength(ch)
    x = 1 + max(0, (CJK_PX - adv) // 2)
    draw.text((x, BASELINE), ch, font=font, fill=255, anchor="ls")
    if mask.getbbox() is None:
        return None
    outline = mask.filter(ImageFilter.MaxFilter(3))
    glyph = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    glyph.paste(OUTLINE_RGB + (255,), mask=outline)
    px, mp = glyph.load(), mask.load()
    for yy in range(CELL_H):
        rgb = ROW_RGB.get(yy, ROW_RGB[13])
        for xx in range(w):
            if mp[xx, yy]:
                px[xx, yy] = rgb + (255,)
    return glyph


def main(charset_path, out_path, preview_path=None):
    with open(charset_path, encoding="utf-8") as f:
        wanted = sorted({c for c in f.read() if ord(c) > 126 and not c.isspace() and c != "\ufeff"})

    env = UnityPy.load(SRC)
    objs = {o.path_id: o for o in env.objects}
    font_obj = objs[FONT_ID]
    tree = font_obj.read_typetree()
    tex = objs[TEX_ID].read()
    old_img = tex.image.convert("RGBA")
    ow, oh = old_img.size

    existing = {r["index"] for r in tree["m_CharacterRects"]}
    wanted = [c for c in wanted if ord(c) not in existing]

    font = ImageFont.truetype(CJK_FONT, CJK_PX)
    missing, cjk = [], []
    for ch in wanted:
        g = render_cjk(ch, font)
        if g is None:
            missing.append(ch)
            continue
        rect = {
            "index": ord(ch),
            "uv": None,
            "vert": {"x": -1.0, "y": 0.0, "width": float(g.width), "height": -float(CELL_H)},
            "width": float(CJK_ADVANCE),
            "flipped": False,
        }
        cjk.append((rect, g))

    width, height = 2048, 1024
    while not fits(cjk, width, height - oh - PAD):
        height *= 2
    atlas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    atlas.paste(old_img, (0, 0))
    rects = []
    for r in tree["m_CharacterRects"]:
        uv = r["uv"]
        r = dict(r)
        left = uv["x"] * ow
        top = oh - (uv["y"] + uv["height"]) * oh
        r["uv"] = {"x": left / width, "y": 1 - (top + uv["height"] * oh) / height,
                   "width": uv["width"] * ow / width, "height": uv["height"] * oh / height}
        rects.append(r)

    x, y = 0, oh + PAD
    for rect, img in cjk:
        w, h = img.size
        if x + w > width:
            x, y = 0, y + CELL_H + PAD
        atlas.paste(img, (x, y))
        rect = dict(rect)
        rect["uv"] = {"x": x / width, "y": 1 - (y + h) / height, "width": w / width, "height": h / height}
        rects.append(rect)
        x += w + PAD

    tex.set_image(atlas, target_format=TextureFormat.ARGB32)
    tex.save()
    tree["m_CharacterRects"] = rects
    font_obj.save_typetree(tree)

    with open(out_path, "wb") as f:
        f.write(env.file.save())
    if preview_path:
        crop = atlas.crop((0, 0, 600, 120))
        bg = Image.new("RGBA", crop.size, (40, 90, 160, 255))
        bg.alpha_composite(crop)
        bg.resize((crop.width * 3, crop.height * 3), Image.NEAREST).save(preview_path)
    print(f"atlas {width}x{height}, glyphs {len(rects)}, new cjk {len(cjk)}, missing {''.join(missing)!r}")


def fits(glyphs, width, height):
    x = y = 0
    for _, img in glyphs:
        w = img.width
        if x + w > width:
            x, y = 0, y + CELL_H + PAD
        x += w + PAD
    return y + CELL_H <= height


if __name__ == "__main__":
    main(*sys.argv[1:])
