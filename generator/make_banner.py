import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BRAND = os.path.join(os.path.dirname(HERE), "brand")
import numpy as np
from PIL import Image, ImageDraw
import make_video as mv
from make_video import ell, poly, line, text, mascot, cloud, DRAW, NUM_COLORS, INK, P, S, font

BW, BH = 2560, 1440
SAFE = (507, 509, 2053, 932)  # YouTube text/logo safe area (1546x423)

img = Image.new("RGB", (BW * S, BH * S))
top, bot = np.array([100, 195, 255]), np.array([215, 244, 255])
g = np.linspace(0, 1, BH * S)[:, None]
arr = (top * (1 - g) + bot * g).astype(np.uint8)
img.paste(Image.fromarray(np.repeat(arr[:, None, :], BW * S, axis=1)))
d = ImageDraw.Draw(img)

# sun top-right, clouds
DRAW["sun"](d, 2300, 230, 120, 0.4, 0)
for x, y, s in [(250, 180, 110), (900, 120, 80), (1650, 200, 95), (2050, 420, 60), (420, 470, 55)]:
    cloud(d, x, y, s)

# hills
ell(d, 400, 1500, 1100, 480, "#9be15d")
ell(d, 2200, 1530, 1150, 500, "#9be15d")
ell(d, 1280, 1700, 1900, 620, "#6fcf4a")
for (x, y) in [(120, 1200), (300, 1290), (2440, 1230), (2250, 1320), (900, 1350), (1700, 1340), (1300, 1390)]:
    ell(d, x, y, 12, 12, "white", ow=0)
    ell(d, x, y, 5, 5, "#ffd60a", ow=0)

# fringe characters (visible on desktop/TV, outside the safe area)
DRAW["balloon"](d, 180, 760, 95, 0.2, 0)
DRAW["balloon"](d, 330, 640, 80, 1.1, 2)
DRAW["flower"](d, 250, 1100, 80, 0.3, 0)
DRAW["duck"](d, 2280, 1060, 95, 0.3, 1)
DRAW["star"](d, 2350, 700, 75, 0.5, 2)
DRAW["fish"](d, 2140, 1250, 60, 0.1, 1)
DRAW["ladybug"](d, 430, 1230, 55, 0.2, 0)
DRAW["heart"](d, 2420, 520, 50, 0.2, 0)
for x, y, s in [(560, 330, 26), (1960, 300, 22), (2480, 900, 20), (90, 470, 22)]:
    poly(d, mv.star_pts(x, y, s, s * 0.45, 0), "#fff3a3", ow=3)

def explorer(d, mx, my, r, glass=True):
    mascot(d, mx, my, r, 0.2, wave=False, hop_h=0)
    hy = my - r * 0.93
    ell(d, mx, hy + 10, r * 0.95, r * 0.2, "#c8963e")           # brim
    d.chord([P(mx - r * 0.58), P(hy - r * 0.62), P(mx + r * 0.58), P(hy + r * 0.5)], 180, 360,
            fill="#e0b25c", outline=INK, width=int(P(5)))      # crown
    d.rectangle([P(mx - r * 0.57), P(hy - 16), P(mx + r * 0.57), P(hy - 2)], fill="#8a5a2b")
    ell(d, mx, hy - 0.35 * r, 10, 10, "#8a5a2b", ow=0)
    if glass:
        gx, gy = mx + r * 1.25, my - r * 0.25
        line(d, [(mx + r * 0.95, my + r * 0.25), (gx - 30, gy + 40)], fill=INK, w=24)
        line(d, [(mx + r * 0.95, my + r * 0.25), (gx - 30, gy + 40)], fill="#8a5a2b", w=14)
        ell(d, gx, gy, 52, 52, "#d7f3ff", ow=9)
        ell(d, gx - 16, gy - 16, 12, 8, "white", ow=0)
        ell(d, mx + r * 0.95, my + r * 0.25, r * 0.15, r * 0.15, "#ff8c42")


explorer(d, 700, 790, 130)

# title — letters in rotating brand colors
title = "Tiny Explorer"
px = 150
f = font(px)
total = sum(f.getlength(c) for c in title) / S
x = 1405 - total / 2
for k, c in enumerate(title):
    w = f.getlength(c) / S
    if c != " ":
        text(d, x + w / 2, 665 + math.sin(k * 0.9) * 8, c, px, NUM_COLORS[k % 10], stroke=12)
    x += w
# subtitle pill
sub = "Songs  •  Counting  •  Learning for Kids"
sw = font(46).getlength(sub) / S
d.rounded_rectangle([P(1405 - sw / 2 - 40), P(780), P(1405 + sw / 2 + 40), P(860)], radius=int(P(40)),
                    fill="#ffffff", outline=INK, width=int(P(5)))
text(d, 1405, 822, sub, 46, "#ff6b35", stroke=0)

out = img.reduce(S)
out.save(os.path.join(BRAND, "tiny_explorer_banner.png"))
# preview with safe-area guide (not for upload)
pv = out.copy().resize((1280, 720))
pd = ImageDraw.Draw(pv)
pd.rectangle([c // 2 for c in SAFE], outline="red", width=2)
pv.save(os.path.join(BRAND, "banner_preview.png"))

# ---- channel picture 800x800 (YouTube crops to a circle) ----
PS = 800
pimg = Image.new("RGB", (PS * S, PS * S), "#ffffff")
pd = ImageDraw.Draw(pimg)
yy = np.linspace(0, 1, PS * S)[:, None]
parr = (np.array([255, 214, 92]) * (1 - yy) + np.array([255, 160, 70]) * yy).astype(np.uint8)
pimg.paste(Image.fromarray(np.repeat(parr[:, None, :], PS * S, axis=1)))
pd = ImageDraw.Draw(pimg)
for k in range(16):
    a = k * math.tau / 16
    pts = [(400, 400), (400 + math.cos(a - 0.1) * 700, 400 + math.sin(a - 0.1) * 700),
           (400 + math.cos(a + 0.1) * 700, 400 + math.sin(a + 0.1) * 700)]
    poly(pd, pts, "#ffe08a" if k % 2 else "#ffc94d", ow=0)
ell(pd, 400, 760, 520, 190, "#6fcf4a", ow=6)
for x, y, s_ in [(170, 230, 26), (640, 200, 22), (650, 470, 18)]:
    poly(pd, mv.star_pts(x, y, s_, s_ * 0.45, 0), "#ffffff", ow=4)
explorer(pd, 360, 470, 175)
pimg.reduce(S).save(os.path.join(BRAND, "tiny_explorer_profile.png"))
pv = pimg.reduce(S).resize((400, 400))
m = Image.new("L", (400, 400), 0); ImageDraw.Draw(m).ellipse([0, 0, 399, 399], fill=255)
c = Image.new("RGB", (400, 400), "white"); c.paste(pv, (0, 0), m); c.save(os.path.join(BRAND, "profile_preview.png"))
