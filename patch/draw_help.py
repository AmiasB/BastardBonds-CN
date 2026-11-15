# Rebuild the five F1 help pictures. Text is Fusion Pixel 10px,
# so the lines have room between them.
# Sprites, icons, and the yellow equipment diagram stay.
from PIL import Image, ImageDraw, ImageFont

FONT = r"E:\T File\BB_WORK\fonts\fp10\fusion-pixel-10px-proportional-zh_hans.ttf"
SRC = r"E:\T File\BB_WORK\patch\_help"
OUT = r"E:\T File\BB_WORK\patch\_help\out"

WHITE = (255, 255, 255, 255)
YELLOW = (255, 255, 0, 255)
RED = (255, 48, 32, 255)
CYAN = (64, 216, 255, 255)
ORANGE = (255, 168, 32, 255)
BLACK = (0, 0, 0, 179)

font = ImageFont.truetype(FONT, 10)


def width(s):
    return font.getlength(s)


def text(d, x, y, s, fill):
    d.text((int(x), int(y)), s, font=font, fill=fill)


def center(d, cx, y, s, fill):
    text(d, cx - width(s) / 2, y, s, fill)


def kill(px, box, pred):
    x0, y0, x1, y1 = box
    w, h = px.size if False else (None, None)
    for y in range(y0, y1):
        for x in range(x0, x1):
            if pred(px[x, y]):
                px[x, y] = BLACK


def is_whiteish(p):
    r, g, b = p[:3]
    return r > 150 and abs(r - g) < 22 and abs(g - b) < 22


def is_yellowish(p):
    r, g, b = p[:3]
    return r > 180 and g > 160 and b < 90 and r - b > 80


def is_reddish(p):
    r, g, b = p[:3]
    return r > 150 and g < 110 and b < 110 and r - g > 60


def is_cyan(p):
    r, g, b = p[:3]
    return b > 140 and g > 90 and r < 120 and b - r > 50


def is_orange(p):
    r, g, b = p[:3]
    return r > 190 and 90 < g < 200 and b < 90 and r - g > 30 and not is_yellowish(p)


def sprite_mask(src):
    # Character and tile pixels, not the white/yellow/red/cyan lettering.
    px = src.load()
    w, h = src.size
    core = [[False] * w for _ in range(h)]

    def core_at(x, y):
        if y > 270 or x > 330:
            return False
        r, g, b = px[x, y][:3]
        if r + g + b < 70:
            return False
        if is_yellowish(px[x, y]) or is_reddish(px[x, y]) or is_cyan(px[x, y]) or is_orange(px[x, y]):
            return False
        if r > 140 and abs(r - g) < 18 and abs(g - b) < 18:
            return False
        return True

    for y in range(h):
        for x in range(w):
            core[y][x] = core_at(x, y)
    mask = [row[:] for row in core]
    for y in range(h):
        for x in range(w):
            if core[y][x]:
                continue
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and core[yy][xx]:
                        r, g, b = px[x, y][:3]
                        if r + g + b < 140 and not is_yellowish(px[x, y]):
                            mask[y][x] = True
                        break
    return mask


def fill_keep(px, box, keep):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not keep(px[x, y]):
                px[x, y] = BLACK


def fill(px, box):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            px[x, y] = BLACK


def map_page():
    src = Image.open(SRC + r"\Help_MapExplorer.png").convert("RGBA")
    im = src.copy()
    px = im.load()
    opx = src.load()
    mask = sprite_mask(src)
    # Left labels. Icons sit at x < 20.
    fill(px, (20, 0, 216, 108))
    fill(px, (0, 108, 216, 254))
    # Action column, including the English names tucked against the tiles.
    fill(px, (250, 0, 534, 272))
    fill(px, (534, 100, 638, 272))
    fill(px, (542, 78, 634, 95))
    for y in range(272):
        for x in range(240, 330):
            if mask[y][x]:
                px[x, y] = opx[x, y]
    # English action names left gray, yellow, and red specks just left of
    # the Chinese labels. A speck that does not touch the sprite is removed.
    solid = [[False] * 640 for _ in range(272)]
    for y in range(272):
        for x in range(240, 330):
            r, g, b = px[x, y][:3]
            solid[y][x] = r + g + b > 30
    seen = [[False] * 640 for _ in range(272)]
    stack = []
    for y in range(272):
        for x in range(240, 292):
            if solid[y][x] and not seen[y][x]:
                seen[y][x] = True
                stack.append((x, y))
    while stack:
        x, y = stack.pop()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                xx, yy = x + dx, y + dy
                if 240 <= xx < 330 and 0 <= yy < 272 and solid[yy][xx] and not seen[yy][xx]:
                    seen[yy][xx] = True
                    stack.append((xx, yy))
    for y in range(272):
        for x in range(296, 330):
            if solid[y][x] and not seen[y][x]:
                px[x, y] = BLACK
    # Diagram words. Leave the yellow rules in place.
    fill_keep(px, (56, 250, 230, 273), is_yellowish)
    fill_keep(px, (0, 294, 78, 360), is_yellowish)

    d = ImageDraw.Draw(im)
    rows = [
        (22, 4, "离开关卡时获得经验"),
        (26, 20, "跟随模式"),
        (26, 38, "呼叫同伴"),
        (26, 56, "技能书"),
        (26, 74, "搜索掉落物品"),
        (26, 92, "返回大地图"),
    ]
    for x, y, s in rows:
        text(d, x, y, s, WHITE)
    keys = [
        (108, "WASD", "平移镜头"),
        (122, "空格", "查看选中的人"),
        (136, "Shift", "鲁莽行动"),
        (150, "Tab", "切换选中的人"),
        (164, "Ctrl", "切换地图透明"),
    ]
    for y, key, desc in keys:
        text(d, 4, y, key, YELLOW)
        text(d, 8 + width(key), y, desc, WHITE)
    text(d, 4, 184, "物品与装备", YELLOW)
    for i, s in enumerate((
        "装备只能在自己的回合更换。",
        "同伴的背包可以随时打开。",
        "战斗中使用物品不结束回合，",
        "也不产生风险。",
    )):
        text(d, 4, 200 + i * 12, s, WHITE)

    text(d, 62, 252, "金币、容量、钥匙", WHITE)
    text(d, 68, 277, "团伙仓库", WHITE)
    text(d, 18, 294, "生命", WHITE)
    text(d, 44, 300, "阵营", WHITE)
    text(d, 28, 318, "武器", WHITE)
    text(d, 28, 334, "护甲", WHITE)
    text(d, 28, 348, "饰品", WHITE)
    center(d, 589, 58, "小地图", WHITE)

    y = 4
    step = 12
    name_x = 322
    desc_x = 354

    def header(s):
        nonlocal y
        text(d, desc_x, y, s, WHITE)
        y += step

    def row(name, color, desc, desc_color):
        nonlocal y
        if name:
            text(d, name_x, y, name, color)
        text(d, desc_x, y, desc, desc_color)
        y += step

    header("对自身")
    row("防御", YELLOW, "伤害降低56%，直至下回合", WHITE)
    row("", WHITE, "投入防御技能可以强化", WHITE)
    row("待命", RED, "让下一名战斗者先行动", WHITE)
    row("", WHITE, "只产生很少的风险", WHITE)
    header("对同伴")
    row("充能", ORANGE, "按比例治疗，并给予强化", WHITE)
    row("", WHITE, "需要施法技能 Imarcus", CYAN)
    y = 100
    step = 13
    header("对敌人")
    row("攻击", RED, "试图伤害武器距离内的敌人", WHITE)
    row("", WHITE, "可能落空、暴击，也受运气影响", WHITE)
    row("", WHITE, "鲁莽攻击可以攻击非战斗者", RED)
    row("施法", RED, "试图用法术伤害远处的敌人", WHITE)
    row("", WHITE, "可能落空、暴击，受护佑与运气影响", WHITE)
    row("", WHITE, "产生大量风险", RED)
    row("", WHITE, "需要施法技能 Arcus", CYAN)
    row("", WHITE, "鲁莽施法可以攻击非战斗者", RED)
    row("交涉", YELLOW, "让敌人脱离战斗，可以不附条件", WHITE)
    row("", WHITE, "条件可能失败，且需要共同语言", WHITE)
    row("", WHITE, "投入辅助技能可以强化", WHITE)
    row("", WHITE, "目标必须正在犹豫", CYAN)
    im.save(OUT + r"\Help_MapExplorer.png")


def overworld():
    im = Image.new("RGBA", (640, 360), BLACK)
    d = ImageDraw.Draw(im)
    text(d, 16, 14, "WASD", YELLOW)
    text(d, 16 + width("WASD") + 8, 14, "平移镜头", WHITE)
    text(d, 16, 32, "PGUP/PGDN", YELLOW)
    text(d, 16 + width("PGUP/PGDN") + 8, 32, "滚轮", YELLOW)
    text(d, 16 + width("PGUP/PGDN") + 8 + width("滚轮") + 8, 32, "缩放镜头", WHITE)

    notes = [
        ["点击相连的区域，就能走过去。"],
        ["探完地形并消灭生物，地点才算肃清。", "之后可能开放新路线和据点。"],
        ["有的地点要有条件才能肃清，有的肃清不了。", "走不通就绕开。"],
        ["有人受伤或动弹不得，就先撤到出口。", "经验少一些，但能避免减员，背包也不至于塞满。"],
        ["肃清过的地点放太久，会重新变危险。", "可以回去练级、找赎金或新人、养伤，或等商人摆摊。"],
        ["每次进入都会记下进度。出了事，也能从入口重来。"],
    ]
    y = 64
    for lines in notes:
        for line in lines:
            text(d, 16, y, line, WHITE)
            y += 14
        y += 16
    im.save(OUT + r"\Help_Overworld.png")


def inventory():
    im = Image.new("RGBA", (640, 360), BLACK)
    d = ImageDraw.Draw(im)
    paragraphs = [
        "点击或右键点击任意同伴的名字，可以直接打开他的物品和装备。",
        "每个同伴都会自己保管物品，你也可以在这里放心存放少量东西。如果想大量囤积、留着锻造，或者把不要的东西换成钱，就该雇一名军需官。",
        "军需官不一定能为挂出的每件东西找到买主，有些种类也更难卖。估价师能让物品卖得更快、价钱更高。",
        "就算军需官不在了，仓库里的东西也还在。但你得再雇一名军需官来整理，才能重新取用。",
    ]
    y = 36
    for para in paragraphs:
        lines = wrap(para, 580)
        for line in lines:
            center(d, 320, y, line, WHITE)
            y += 16
        y += 22
    im.save(OUT + r"\Help_InventoryManage.png")


def stronghold():
    src = Image.open(SRC + r"\Help_Stronghold.png").convert("RGBA")
    im = Image.new("RGBA", (640, 360), BLACK)
    # Keep the five button icons.
    im.paste(src.crop((0, 16, 24, 110)), (0, 16))
    d = ImageDraw.Draw(im)
    legend = [
        (18, "F", "物品存储与出售"),
        (36, "C", "据点管理"),
        (54, "B", "技能书"),
        (74, "R", "搜索掉落物品"),
        (92, "", "返回大地图"),
    ]
    for y, key, desc in legend:
        x = 28
        if key:
            text(d, x, y, key, YELLOW)
            x += width(key) + 6
        text(d, x, y, desc, WHITE)
    text(d, 16, 118, "按 C 打开据点管理，才能招募下面这些人。帐篷在入口附近。", WHITE)
    text(d, 16, 134, "要有空铺位和盈余人力。想招更多人，就搬去更大的据点，并让人专精辅助。", WHITE)
    services = [
        (156, 16, "军需官  最多1", "存放并出售多余物品。大据点离不了。"),
        (156, 330, "锁匠  最多1", "制作并出售钥匙，除了最独特的锁。"),
        (186, 16, "商人  最多6", "定期来去卖货。商人越多，货越好。"),
        (186, 330, "脚夫  最多3", "随你冒险，增加背包。人越多，包越大。"),
        (216, 16, "治疗师  最多3", "治疗伤员。多名一起，效果更强。"),
        (216, 330, "铁匠  最多1", "两件相同武器合成更强的，也能镶宝石。"),
        (246, 16, "估价师  最多1", "帮军需官卖掉难出手的货，价格也更利于你。"),
    ]
    for y, x, name, desc in services:
        text(d, x, y, name, YELLOW)
        text(d, x, y + 12, desc, WHITE)
    text(d, 16, 278, "多陪他们、偶尔交谈，他们也许会信任你。想赶走谁，就看着他的眼睛，叫他离开。", WHITE)
    text(d, 16, 294, "丢在地上的东西，离开后再回来就不会还在。想留的都放进储物。", WHITE)
    text(d, 16, 310, "岛上某处有一件能帮你结交朋友的物品。", WHITE)
    im.save(OUT + r"\Help_Stronghold.png")


def base_page():
    src = Image.open(SRC + r"\Help_BaseManage.png").convert("RGBA")
    im = Image.new("RGBA", (640, 360), BLACK)
    sp = src.load()
    dp = im.load()
    w, h = src.size
    # Portraits are one opaque blob, including black cloth.
    # English captions are light gray and are not part of that blob.
    from collections import deque
    seen = bytearray(w * h)
    q = deque()

    def is_caption(r, g, b):
        return min(r, g, b) > 165 and max(r, g, b) - min(r, g, b) < 32

    for y in range(125, h):
        for x in range(w):
            r, g, b, a = sp[x, y]
            if a > 220 and max(r, g, b) - min(r, g, b) > 28 and r + g + b > 70 and not is_caption(r, g, b):
                seen[y * w + x] = 1
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                xx, yy = x + dx, y + dy
                if xx < 0 or yy < 125 or xx >= w or yy >= h:
                    continue
                i = yy * w + xx
                if seen[i]:
                    continue
                r, g, b, a = sp[xx, yy]
                if a > 220 and not is_caption(r, g, b):
                    seen[i] = 1
                    q.append((xx, yy))
    for y in range(125, h):
        row = y * w
        for x in range(w):
            if seen[row + x]:
                dp[x, y] = sp[x, y]
    d = ImageDraw.Draw(im)
    top = [
        "这里可以为据点招募非战斗者。",
        "招人需要空的铺位，以及一定的盈余人力。现在没有人选的话，等人力增加后再回来看。",
        "团伙里的每个人都会贡献据点的人力，但贡献多少随阵营而不同。",
        "找到合适的服务者需要时间。过一阵再回来，看看有没有人到。",
    ]
    y = 10
    for para in top:
        for line in wrap(para, 600):
            center(d, 320, y, line, WHITE)
            y += 15
        y += 6

    def person(cx, name_y, desc_x, desc_y, name, lines, desc_w):
        label = name
        center(d, cx, name_y, label, WHITE)
        yy = desc_y
        for line in lines:
            text(d, desc_x, yy, line, WHITE)
            yy += 14

    person(114, 190, 162, 150, "军需官 最多1", ("负责存放并出售余货。", "大据点离不了。"), 160)
    person(354, 182, 392, 140, "锁匠 最多1", ("制作并出售钥匙，", "除最独特的锁外都能开。"), 200)
    person(33, 270, 66, 222, "商人 最多6", ("出售物品，定期来去。", "商人越多，货越好。"), 140)
    person(243, 272, 286, 220, "脚夫 最多3", ("随你冒险，多给背包空间。", "脚夫越多，空间越大。"), 155)
    person(476, 272, 508, 222, "治疗师 最多3", ("帮助伤者恢复。", "多名效果更强。"), 110)
    person(104, 342, 144, 300, "铁匠 最多1", ("两件相同武器合成更强的。", "也能镶上宝石。"), 170)
    person(355, 344, 398, 302, "估价师 最多1", ("帮军需官卖掉难出手的货。", "据点价格也更利于你。"), 210)
    im.save(OUT + r"\Help_BaseManage.png")


def wrap(s, max_w):
    lines = []
    cur = ""
    for ch in s:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        trial = cur + ch
        if cur and width(trial) > max_w:
            lines.append(cur)
            cur = ch
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    map_page()
    overworld()
    inventory()
    stronghold()
    base_page()
    print("drew", OUT)
