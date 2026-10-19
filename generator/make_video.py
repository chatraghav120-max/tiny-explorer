"""Let's Count 1 to 10! — original kids counting cartoon (1080p, 30fps) with synthesized soundtrack."""
import math, random, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Pool
from scipy.io import wavfile
from scipy.signal import butter, lfilter

W, H, S, FPS = 1920, 1080, 2, 30
BEAT = 0.5
INTRO_B, SCENE_B, RECAP_B, OUTRO_B = 8, 8, 12, 12
T_INTRO = INTRO_B * BEAT
T_SCENE = SCENE_B * BEAT
T_SCENES_END = T_INTRO + 10 * T_SCENE
T_RECAP_END = T_SCENES_END + RECAP_B * BEAT
T_TOTAL = T_RECAP_END + OUTRO_B * BEAT
OUT = os.path.dirname(os.path.abspath(__file__))

INK = "#2d2340"
NUM_COLORS = ["#ff595e", "#ff924c", "#ffca3a", "#8ac926", "#2ec4b6",
              "#1982c4", "#4267ac", "#8b5cf6", "#f15bb5", "#00bbf9"]
WORDS = ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN"]
THINGS = ["sun", "duck", "fish", "balloon", "star", "apple", "flower", "bubble", "ladybug", "heart"]
THING_NAMES = ["sun", "ducks", "fish", "balloons", "stars", "apples", "flowers", "bubbles", "ladybugs", "hearts"]
FONT_PATH = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
_fonts = {}


def font(px):
    if px not in _fonts:
        _fonts[px] = ImageFont.truetype(FONT_PATH, int(px * S))
    return _fonts[px]


def P(v):
    return v * S


def clamp01(x):
    return max(0.0, min(1.0, x))


def ease_out_back(x):
    x = clamp01(x)
    c1 = 1.9
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ell(d, cx, cy, rx, ry, fill, ow=4):
    box = [P(cx - rx), P(cy - ry), P(cx + rx), P(cy + ry)]
    if ow:
        d.ellipse(box, fill=fill, outline=INK, width=int(P(ow)))
    else:
        d.ellipse(box, fill=fill)


def poly(d, pts, fill, ow=4):
    d.polygon([(P(x), P(y)) for x, y in pts], fill=fill, outline=INK if ow else None,
              width=int(P(ow)) if ow else 0)


def line(d, pts, fill=INK, w=4):
    d.line([(P(x), P(y)) for x, y in pts], fill=fill, width=int(P(w)), joint="curve")


def text(d, x, y, s, px, fill, stroke=8, stroke_fill=INK, anchor="mm"):
    d.text((P(x), P(y)), s, font=font(px), fill=fill, stroke_width=int(P(stroke)),
           stroke_fill=stroke_fill, anchor=anchor)


def face(d, x, y, s, t=0.0, blink_off=0.0):
    blink = ((t + blink_off) % 3.7) < 0.12
    for sx in (-1, 1):
        ex, ey = x + sx * 0.3 * s, y - 0.1 * s
        if blink:
            line(d, [(ex - 0.1 * s, ey), (ex + 0.1 * s, ey)], w=max(3, s * 0.05))
        else:
            ell(d, ex, ey, 0.12 * s, 0.14 * s, INK, ow=0)
            ell(d, ex + 0.04 * s, ey - 0.05 * s, 0.045 * s, 0.045 * s, "white", ow=0)
    ell(d, x - 0.5 * s, y + 0.12 * s, 0.11 * s, 0.07 * s, "#ff8fab", ow=0)
    ell(d, x + 0.5 * s, y + 0.12 * s, 0.11 * s, 0.07 * s, "#ff8fab", ow=0)
    d.arc([P(x - 0.22 * s), P(y - 0.05 * s), P(x + 0.22 * s), P(y + 0.3 * s)], 15, 165,
          fill=INK, width=int(P(max(3, s * 0.05))))


# ---------------- objects ----------------
def draw_sun(d, x, y, s, t, i):
    rot = t * 0.9
    for k in range(12):
        a = rot + k * math.tau / 12
        pts = [(x + math.cos(a - 0.14) * s * 0.92, y + math.sin(a - 0.14) * s * 0.92),
               (x + math.cos(a) * s * 1.42, y + math.sin(a) * s * 1.42),
               (x + math.cos(a + 0.14) * s * 0.92, y + math.sin(a + 0.14) * s * 0.92)]
        poly(d, pts, "#ffb703")
    ell(d, x, y, s * 0.95, s * 0.95, "#ffd60a")
    face(d, x, y + 0.05 * s, s, t, i)


def draw_duck(d, x, y, s, t, i):
    y += math.sin(t * 4 + i) * s * 0.06
    ell(d, x, y + 0.75 * s, s * 1.0, s * 0.18, "#7cc6fe", ow=0)
    ell(d, x, y + 0.25 * s, s * 0.85, s * 0.55, "#ffd23f")
    ell(d, x - 0.15 * s, y + 0.25 * s, s * 0.4, s * 0.25, "#f4b400")
    poly(d, [(x + 0.62 * s, y - 0.42 * s), (x + 1.08 * s, y - 0.3 * s), (x + 0.62 * s, y - 0.16 * s)], "#ff8c1a")
    ell(d, x + 0.35 * s, y - 0.35 * s, s * 0.42, s * 0.42, "#ffd23f")
    ell(d, x + 0.48 * s, y - 0.45 * s, s * 0.08, s * 0.09, INK, ow=0)
    ell(d, x + 0.5 * s, y - 0.48 * s, s * 0.03, s * 0.03, "white", ow=0)
    ell(d, x + 0.3 * s, y - 0.25 * s, s * 0.08, s * 0.05, "#ff8fab", ow=0)


FISH_COLORS = ["#ff7b54", "#4cc9f0", "#b5e48c"]


def draw_fish(d, x, y, s, t, i):
    x += math.sin(t * 2.5 + i * 2) * s * 0.12
    y += math.cos(t * 3 + i) * s * 0.06
    c = FISH_COLORS[i % 3]
    wag = math.sin(t * 10 + i) * 0.15 * s
    poly(d, [(x - 0.7 * s, y), (x - 1.25 * s, y - 0.5 * s + wag), (x - 1.25 * s, y + 0.5 * s + wag)], c)
    poly(d, [(x - 0.1 * s, y - 0.5 * s), (x + 0.2 * s, y - 0.85 * s), (x + 0.35 * s, y - 0.45 * s)], c)
    ell(d, x, y, s * 0.9, s * 0.6, c)
    ell(d, x + 0.45 * s, y - 0.15 * s, s * 0.18, s * 0.18, "white")
    ell(d, x + 0.5 * s, y - 0.15 * s, s * 0.09, s * 0.09, INK, ow=0)
    d.arc([P(x + 0.35 * s), P(y + 0.0 * s), P(x + 0.75 * s), P(y + 0.3 * s)], 20, 160, fill=INK, width=int(P(4)))
    for k in range(3):
        b = ((t * 0.6 + i * 0.37 + k * 0.33) % 1.0)
        ell(d, x + 0.95 * s + k * 6, y - b * s * 1.3, 6 + 4 * b, 6 + 4 * b, "#e0f7ff", ow=2)


BALLOON_COLORS = ["#ff595e", "#ffca3a", "#1982c4", "#8ac926"]


def draw_balloon(d, x, y, s, t, i):
    sway = math.sin(t * 2 + i) * 10
    pts = [(x + sway * (1 - k / 8) + math.sin(k + t * 3) * 5, y + 0.8 * s + k * s * 0.11) for k in range(9)]
    line(d, pts, w=3)
    bx = x + sway
    poly(d, [(bx - 0.12 * s, y + 0.85 * s), (bx, y + 0.68 * s), (bx + 0.12 * s, y + 0.85 * s)], BALLOON_COLORS[i % 4])
    ell(d, bx, y - 0.1 * s, s * 0.72, s * 0.85, BALLOON_COLORS[i % 4])
    ell(d, bx - 0.3 * s, y - 0.4 * s, s * 0.12, s * 0.22, "white", ow=0)


def star_pts(x, y, ro, ri, rot):
    pts = []
    for k in range(10):
        a = rot - math.pi / 2 + k * math.pi / 5
        r = ro if k % 2 == 0 else ri
        pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
    return pts


def draw_star(d, x, y, s, t, i):
    rot = math.sin(t * 3 + i) * 0.15
    poly(d, star_pts(x, y, s * 1.05, s * 0.5, rot), "#ffd60a")
    face(d, x, y + 0.1 * s, s * 0.75, t, i)


def draw_apple(d, x, y, s, t, i):
    y += math.sin(t * 3 + i) * 4
    line(d, [(x, y - 0.7 * s), (x + 0.08 * s, y - 1.05 * s)], fill="#7a4b2a", w=7)
    ell(d, x + 0.28 * s, y - 0.95 * s, s * 0.28, s * 0.13, "#57cc04")
    ell(d, x - 0.32 * s, y, s * 0.6, s * 0.78, "#e63946")
    ell(d, x + 0.32 * s, y, s * 0.6, s * 0.78, "#e63946")
    ell(d, x, y + 0.02 * s, s * 0.55, s * 0.7, "#e63946", ow=0)
    ell(d, x - 0.5 * s, y - 0.35 * s, s * 0.1, s * 0.18, "#ffb3b8", ow=0)
    face(d, x, y + 0.1 * s, s * 0.8, t, i)


PETALS = ["#f15bb5", "#9b5de5", "#ff924c", "#00bbf9"]


def draw_flower(d, x, y, s, t, i):
    sway = math.sin(t * 2 + i) * 0.1 * s
    cx, cy = x + sway, y - 0.25 * s
    line(d, [(x, y + 0.95 * s), (x + sway * 0.5, y + 0.3 * s), (cx, cy)], fill="#38b000", w=8)
    ell(d, x + 0.25 * s, y + 0.6 * s, s * 0.25, s * 0.11, "#38b000")
    for k in range(5):
        a = k * math.tau / 5 + t * 0.5
        ell(d, cx + math.cos(a) * s * 0.5, cy + math.sin(a) * s * 0.5, s * 0.36, s * 0.36, PETALS[i % 4])
    ell(d, cx, cy, s * 0.38, s * 0.38, "#ffd60a")
    face(d, cx, cy, s * 0.45, t, i)


def draw_bubble(d, x, y, s, t, i):
    y += math.sin(t * 2.2 + i * 1.3) * 14
    x += math.cos(t * 1.7 + i) * 8
    d.ellipse([P(x - s * 0.8), P(y - s * 0.8), P(x + s * 0.8), P(y + s * 0.8)], fill="#cdeffd",
              outline="#3aa6dd", width=int(P(5)))
    ell(d, x - 0.32 * s, y - 0.32 * s, s * 0.2, s * 0.13, "white", ow=0)
    ell(d, x + 0.4 * s, y + 0.35 * s, s * 0.07, s * 0.07, "white", ow=0)


def draw_ladybug(d, x, y, s, t, i):
    x += math.sin(t * 1.5 + i) * 6
    line(d, [(x - 0.15 * s, y - 0.95 * s), (x - 0.35 * s, y - 1.25 * s)], w=4)
    line(d, [(x + 0.15 * s, y - 0.95 * s), (x + 0.35 * s, y - 1.25 * s)], w=4)
    ell(d, x - 0.35 * s, y - 1.27 * s, 7, 7, INK, ow=0)
    ell(d, x + 0.35 * s, y - 1.27 * s, 7, 7, INK, ow=0)
    ell(d, x, y - 0.7 * s, s * 0.4, s * 0.35, INK)
    ell(d, x, y, s * 0.78, s * 0.75, "#ef233c")
    line(d, [(x, y - 0.74 * s), (x, y + 0.74 * s)], w=5)
    for dx, dy in [(-0.4, -0.25), (0.4, -0.25), (-0.45, 0.25), (0.45, 0.25), (-0.18, 0.5), (0.18, 0.5)]:
        ell(d, x + dx * s, y + dy * s, s * 0.12, s * 0.12, INK, ow=0)
    ell(d, x - 0.15 * s, y - 0.75 * s, s * 0.08, s * 0.09, "white", ow=0)
    ell(d, x + 0.15 * s, y - 0.75 * s, s * 0.08, s * 0.09, "white", ow=0)


def draw_heart(d, x, y, s, t, i):
    k = 1 + 0.06 * math.sin(t * 8 + i)
    pts = []
    for j in range(60):
        a = j * math.tau / 60
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((x + hx * s * 0.058 * k, y + hy * s * 0.058 * k))
    poly(d, pts, ["#ff4d6d", "#ff8fab"][i % 2])
    ell(d, x - 0.4 * s, y - 0.35 * s, s * 0.12, s * 0.08, "white", ow=0)
    face(d, x, y + 0.05 * s, s * 0.6, t, i)


DRAW = dict(sun=draw_sun, duck=draw_duck, fish=draw_fish, balloon=draw_balloon, star=draw_star,
            apple=draw_apple, flower=draw_flower, bubble=draw_bubble, ladybug=draw_ladybug, heart=draw_heart)


# ---------------- mascot "Bobo" ----------------
def mascot(d, cx, cy, r, t, wave=False, hop_h=26):
    p = (t % BEAT) / BEAT
    hop = abs(math.sin(math.pi * p))
    y = cy - hop * hop_h
    sx, sy = 1 + 0.07 * (1 - hop), 1 - 0.07 * (1 - hop)
    ell(d, cx, cy + r * 0.98, r * (0.9 - 0.25 * hop), r * 0.14, "#4fa83a", ow=0)
    ell(d, cx - 0.4 * r, y + 0.9 * r, r * 0.3, r * 0.16, "#e86a1c")
    ell(d, cx + 0.4 * r, y + 0.9 * r, r * 0.3, r * 0.16, "#e86a1c")
    # arms
    if wave:
        a = -2.2 + 0.5 * math.sin(t * 9)
        hx, hy = cx + r * 0.85 + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.6
        line(d, [(cx + r * 0.8, y), (hx, hy)], fill=INK, w=r * 0.2)
        line(d, [(cx + r * 0.8, y), (hx, hy)], fill="#ff8c42", w=r * 0.12)
        ell(d, hx, hy, r * 0.15, r * 0.15, "#ff8c42")
    else:
        ell(d, cx + r * 0.92, y + 0.15 * r, r * 0.17, r * 0.24, "#ff8c42")
    ell(d, cx - r * 0.92, y + 0.15 * r, r * 0.17, r * 0.24, "#ff8c42")
    # tuft
    ell(d, cx + 0.12 * r, y - r * sy - 0.12 * r, r * 0.2, r * 0.1, "#57cc04")
    line(d, [(cx, y - r * sy + 2), (cx + 0.05 * r, y - r * sy - 0.12 * r)], fill="#2d6a1f", w=5)
    ell(d, cx, y, r * sx, r * sy, "#ff8c42")
    ell(d, cx, y + 0.35 * r, r * 0.55 * sx, r * 0.42 * sy, "#ffd3a8", ow=0)
    # eyes
    blink = (t % 3.1) < 0.12
    for s_ in (-1, 1):
        ex, ey = cx + s_ * 0.33 * r, y - 0.22 * r
        if blink:
            line(d, [(ex - 0.15 * r, ey), (ex + 0.15 * r, ey)], w=6)
        else:
            ell(d, ex, ey, 0.21 * r, 0.26 * r, "white")
            ell(d, ex + 0.04 * r, ey + 0.04 * r, 0.11 * r, 0.13 * r, INK, ow=0)
            ell(d, ex + 0.08 * r, ey - 0.02 * r, 0.04 * r, 0.04 * r, "white", ow=0)
    ell(d, cx - 0.6 * r, y + 0.08 * r, 0.12 * r, 0.07 * r, "#ff6f91", ow=0)
    ell(d, cx + 0.6 * r, y + 0.08 * r, 0.12 * r, 0.07 * r, "#ff6f91", ow=0)
    d.chord([P(cx - 0.25 * r), P(y - 0.05 * r), P(cx + 0.25 * r), P(y + 0.38 * r)], 0, 180,
            fill="#b5223b", outline=INK, width=int(P(5)))
    ell(d, cx, y + 0.29 * r, 0.1 * r, 0.05 * r, "#ff8fab", ow=0)


# ---------------- background ----------------
def make_bg():
    img = Image.new("RGB", (W * S, H * S))
    top, bot = np.array([110, 200, 255]), np.array([220, 245, 255])
    g = np.linspace(0, 1, H * S)[:, None]
    arr = (top * (1 - g) + bot * g).astype(np.uint8)
    img.paste(Image.fromarray(np.repeat(arr[:, None, :], W * S, axis=1).reshape(H * S, W * S, 3)))
    d = ImageDraw.Draw(img)
    ell(d, 350, 1180, 900, 380, "#9be15d")
    ell(d, 1650, 1220, 1000, 420, "#9be15d")
    ell(d, 960, 1330, 1400, 420, "#6fcf4a")
    for (x, y) in [(150, 960), (260, 1010), (1840, 990), (1700, 1040), (620, 1040), (1250, 1030)]:
        ell(d, x, y, 10, 10, "#ffffff", ow=0)
        ell(d, x, y, 4, 4, "#ffd60a", ow=0)
    return img


def cloud(d, x, y, s):
    parts = [(-0.6, 0.1, 0.5), (0, -0.15, 0.65), (0.6, 0.1, 0.5), (0.25, 0.2, 0.5), (-0.25, 0.2, 0.5)]
    for dx, dy, r in parts:
        ell(d, x + dx * s, y + dy * s, r * s + 4, r * s * 0.85 + 4, "#b9dcf2", ow=0)
    for dx, dy, r in parts:
        ell(d, x + dx * s, y + dy * s, r * s, r * s * 0.85, "white", ow=0)


def clouds(d, t):
    for i, (x0, y, s, v) in enumerate([(200, 120, 90, 18), (900, 80, 70, 12), (1500, 150, 100, 22), (1200, 300, 55, 9)]):
        x = (x0 + t * v) % (W + 400) - 200
        cloud(d, x, y, s)


# ---------------- layout / timing ----------------
def layout(n):
    if n <= 5:
        s = {1: 150, 2: 140, 3: 130, 4: 115, 5: 100}[n]
        xs = [910] if n == 1 else [300 + k * (1220 / (n - 1)) for k in range(n)]
        if n > 1 and n < 4:
            xs = [910 + (k - (n - 1) / 2) * 400 for k in range(n)]
        return [(x, 650, s) for x in xs]
    top = math.ceil(n / 2)
    bot = n - top
    s = 92 if n < 9 else 86
    out = []
    for row, cnt, y in ((0, top, 530), (1, bot, 845)):
        span = 1260 if cnt == 5 else 1000
        for k in range(cnt):
            x = 910 + (k - (cnt - 1) / 2) * (span / max(cnt - 1, 1))
            out.append((x, y, s))
    return out


def pop_times(n):
    if n == 1:
        return [1.0 * BEAT]
    return [(1 + 0.5 * round(k * 11 / (n - 1))) * BEAT for k in range(n)]


SCALE = [72, 74, 76, 79, 81, 84, 86, 88, 91, 93]


# ---------------- frame rendering ----------------
BG = None


def render(fi):
    global BG
    if BG is None:
        BG = make_bg()
    t = fi / FPS
    img = BG.copy()
    d = ImageDraw.Draw(img)
    clouds(d, t)

    if t < T_INTRO:
        title = "Let's Count!"
        f = font(150)
        total = sum(f.getlength(c) for c in title) / S
        x = 960 - total / 2
        for k, c in enumerate(title):
            w = f.getlength(c) / S
            a = ease_out_back((t - 0.2 - k * 0.07) / 0.4)
            if a > 0.01:
                yy = 280 + (1 - a) * 200 + math.sin(t * 6 + k * 0.6) * 10
                text(d, x + w / 2, yy, c, 150, NUM_COLORS[k % 10], stroke=10)
            x += w
        a = ease_out_back((t - 1.5) / 0.5)
        if a > 0.01:
            sub = "1 to 10"
            text(d, 960, 480 + (1 - a) * 80, sub, int(130 * max(a, 0.3)), "white", stroke=10)
        mascot(d, 960, 820, 150, t, wave=True)
    elif t < T_SCENES_END:
        idx = int((t - T_INTRO) // T_SCENE)
        lt = t - T_INTRO - idx * T_SCENE
        n = idx + 1
        nw = font(230).getlength(str(n)) / S
        ww = font(110).getlength(WORDS[idx]) / S
        x0 = 960 - (nw + 40 + ww) / 2
        a = ease_out_back(lt / 0.45)
        text(d, x0 + nw / 2, 205 - (1 - a) * 300, str(n), 230, NUM_COLORS[idx], stroke=12)
        a2 = ease_out_back((lt - 0.2) / 0.45)
        if a2 > 0.01:
            text(d, x0 + nw + 40 + (1 - a2) * -60, 215, WORDS[idx], 110, "white", stroke=10, anchor="lm")
        pts = layout(n)
        times = pop_times(n)
        for k, ((x, y, s), tp) in enumerate(zip(pts, times)):
            sc = ease_out_back((lt - tp) / 0.3)
            if sc > 0.02:
                DRAW[THINGS[idx]](d, x, y, s * sc, t, k)
        for k, ((x, y, s), tp) in enumerate(zip(pts, times)):
            sc = ease_out_back((lt - tp) / 0.3)
            if sc > 0.02:
                ly = y - s * 1.55 - 30
                ell(d, x, ly, 32 * sc, 32 * sc, NUM_COLORS[idx], ow=4)
                text(d, x, ly + 2, str(k + 1), max(8, int(40 * sc)), "white", stroke=4)
        if lt > 6.5 * BEAT:
            a3 = ease_out_back((lt - 6.5 * BEAT) / 0.3)
            label = f"{WORDS[idx].capitalize()} {THING_NAMES[idx]}!"
            text(d, 960, 1010, label, int(70 * max(a3, 0.2)), "#fff7d6", stroke=8)
        mascot(d, 1775, 880, 95, t)
    elif t < T_RECAP_END:
        lt = t - T_SCENES_END
        b = lt / BEAT
        a = ease_out_back(lt / 0.4)
        text(d, 960, 170, "Count with me!", int(110 * max(a, 0.2)), "#ffca3a", stroke=10)
        active = int(b) - 2
        for k in range(10):
            row, col = divmod(k, 5)
            x = 480 + col * 240
            y = 470 + row * 280
            lit = k <= active
            sc = 1.0
            if k == active:
                sc = 1 + 0.3 * (1 - clamp01((b - int(b)) / 0.6))
            c = NUM_COLORS[k] if lit else "#dfe7ef"
            ell(d, x, y, 95 * sc, 95 * sc, c, ow=6)
            text(d, x, y + 4, str(k + 1), int(110 * sc), "white" if lit else "#b4c2cf",
                 stroke=8 if lit else 0, stroke_fill=INK)
        mascot(d, 1775, 880, 95, t)
    else:
        lt = t - T_RECAP_END
        rnd = random.Random(7)
        for k in range(140):
            x0 = rnd.uniform(0, W)
            sp = rnd.uniform(180, 380)
            delay = rnd.uniform(0, 1.2)
            c = NUM_COLORS[rnd.randrange(10)]
            yy = -40 + (lt - delay) * sp
            if yy < -40 or yy > H + 40:
                continue
            xx = x0 + math.sin(lt * 3 + k) * 30
            ang = lt * 5 + k
            pts = [(xx + math.cos(ang + q * math.pi / 2 + 0.4 * (q % 2)) * 14,
                    yy + math.sin(ang + q * math.pi / 2 + 0.4 * (q % 2)) * 8) for q in range(4)]
            poly(d, pts, c, ow=0)
        word = "Yay!"
        f = font(230)
        total = sum(f.getlength(c) for c in word) / S
        x = 960 - total / 2
        for k, c in enumerate(word):
            w = f.getlength(c) / S
            a = ease_out_back((lt - k * 0.1) / 0.4)
            if a > 0.01:
                text(d, x + w / 2, 260 + math.sin(lt * 7 + k) * 14 + (1 - a) * 200, c, 230, NUM_COLORS[k * 2], stroke=12)
            x += w
        a = ease_out_back((lt - 0.8) / 0.5)
        if a > 0.01:
            text(d, 960, 470, "You counted to 10!", int(105 * max(a, 0.2)), "white", stroke=10)
        mascot(d, 960, 820, 150, t, wave=True, hop_h=60)

    # fade in/out
    out = img.reduce(S)
    fade = min(clamp01(t / 0.4), clamp01((T_TOTAL - t) / 0.6))
    if fade < 1:
        out = Image.blend(Image.new("RGB", out.size, "white"), out, fade)
    return out.tobytes()


# ---------------- audio ----------------
SR = 44100


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tone(f, dur, decay, amp, harm=(1.0, 0.4, 0.15)):
    tt = np.arange(int(dur * SR)) / SR
    sig = harm[0] * np.sin(2 * np.pi * f * tt)
    sig += harm[1] * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * decay * 2)
    sig += harm[2] * np.sin(2 * np.pi * 3 * f * tt) * np.exp(-tt * decay * 3)
    env = np.exp(-tt * decay) * np.minimum(1, tt / 0.004)
    return sig * env * amp


def make_audio(path):
    buf = np.zeros(int((T_TOTAL + 2) * SR))

    def add(sig, t):
        i = int(t * SR)
        j = min(len(buf), i + len(sig))
        buf[i:j] += sig[: j - i]

    rng = np.random.default_rng(1)
    b_hp, a_hp = butter(2, 6000 / (SR / 2), "high")
    b_bp, a_bp = butter(2, [900 / (SR / 2), 3000 / (SR / 2)], "band")
    roots = [48, 43, 45, 41]
    chords = [[60, 64, 67], [59, 62, 67], [57, 60, 64], [57, 60, 65]]
    melody = [(0, 72, 1), (1, 76, .5), (1.5, 79, .5), (2, 76, 1), (3, 72, 1),
              (4, 74, 1), (5, 79, .5), (5.5, 77, .5), (6, 74, 1), (7, 71, 1),
              (8, 72, 1), (9, 76, .5), (9.5, 81, .5), (10, 79, 1), (11, 76, 1),
              (12, 77, 1), (13, 76, .5), (13.5, 74, .5), (14, 72, 2)]
    nbeats = int(T_TOTAL / BEAT)
    end_b = nbeats - 4
    for b in range(nbeats):
        t = b * BEAT
        bar = (b // 4) % 4
        if b < end_b:
            if b % 2 == 0:
                tt = np.arange(int(0.15 * SR)) / SR
                ph = 2 * np.pi * np.cumsum(45 + 80 * np.exp(-tt * 30)) / SR
                add(np.sin(ph) * np.exp(-tt * 16) * 0.55, t)
            else:
                nz = lfilter(b_bp, a_bp, rng.standard_normal(int(0.15 * SR)))
                add(nz * np.exp(-np.arange(len(nz)) / SR * 22) * 0.22, t)
            for h in (0, 0.5):
                nz = lfilter(b_hp, a_hp, rng.standard_normal(int(0.06 * SR)))
                add(nz * np.exp(-np.arange(len(nz)) / SR * 70) * (0.07 if h else 0.04), t + h * BEAT)
            r = roots[bar]
            if b % 4 in (0, 2):
                add(tone(mtof(r), 0.45, 5, 0.32, (1, 0.3, 0.05)), t)
            if b % 4 == 3:
                add(tone(mtof(r + 12), 0.25, 7, 0.22, (1, 0.3, 0.05)), t + 0.5 * BEAT)
            for m in chords[bar]:
                add(tone(mtof(m), 0.3, 9, 0.06), t + 0.5 * BEAT)
    for loop in range(0, end_b, 16):
        for bb, m, du in melody:
            if loop + bb < end_b:
                add(tone(mtof(m), du * BEAT + 0.2, 4.5, 0.13, (1, 0.5, 0.2)), (loop + bb) * BEAT)

    def bell(f, amp=0.25):
        tt = np.arange(int(1.4 * SR)) / SR
        return (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2.76 * f * tt) * np.exp(-tt * 4)) * np.exp(-tt * 3) * amp

    def pop(f, amp=0.3):
        tt = np.arange(int(0.25 * SR)) / SR
        ph = 2 * np.pi * np.cumsum(f * (1 + 0.5 * np.exp(-tt * 40))) / SR
        return np.sin(ph) * np.exp(-tt * 14) * amp * np.minimum(1, tt / 0.002)

    for i in range(10):
        st = T_INTRO + i * T_SCENE
        add(bell(mtof(84 + (0 if i % 2 == 0 else 7)), 0.2), st)
        for k, tp in enumerate(pop_times(i + 1)):
            add(pop(mtof(SCALE[k])), st + tp)
    for k in range(10):
        add(bell(mtof(SCALE[k]), 0.22), T_SCENES_END + (2 + k) * BEAT)
    for k, m in enumerate([72, 76, 79, 84, 88, 91, 96]):
        add(tone(mtof(m), 0.6, 5, 0.15), T_RECAP_END + k * 0.07)
    for m in [48, 60, 64, 67, 72]:
        add(tone(mtof(m), 2.5, 1.2, 0.12), T_RECAP_END + end_b * BEAT - T_RECAP_END + 0.0)

    buf = buf[: int(T_TOTAL * SR)]
    buf /= np.max(np.abs(buf)) + 1e-9
    buf = np.tanh(buf * 1.3) / np.tanh(1.3) * 0.89
    fade = int(0.6 * SR)
    buf[-fade:] *= np.linspace(1, 0, fade)
    wavfile.write(path, SR, (buf * 32767).astype(np.int16))


def thumbnail(path):
    img = make_bg()
    d = ImageDraw.Draw(img)
    clouds(d, 3)
    for k, (x, y, s) in enumerate([(230, 760, 95), (450, 830, 85), (1450, 820, 90), (1680, 720, 80)]):
        DRAW[["star", "apple", "duck", "heart"][k]](d, x, y, s, 0.3, k)
    for k, c in enumerate("1 2 3"):
        pass
    text(d, 960, 210, "COUNT", 230, "#ffca3a", stroke=16)
    text(d, 960, 430, "1 to 10!", 200, "white", stroke=16)
    mascot(d, 960, 830, 160, 0.2, wave=True, hop_h=0)
    img.reduce(S).resize((1280, 720), Image.LANCZOS).save(path)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "stills":
        for tt in [2.5, 6.6, 15.5, 22.8, 34.5, 43.6, 47.0, 51.5]:
            Image.frombytes("RGB", (W, H), render(int(tt * FPS))).save(f"{OUT}/still_{tt}.png")
        thumbnail(f"{OUT}/thumbnail.png")
        sys.exit()
    make_audio(f"{OUT}/audio.wav")
    thumbnail(f"{OUT}/thumbnail.png")
    N = int(T_TOTAL * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", f"{OUT}/audio.wav",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                           f"{OUT}/Lets_Count_1_to_10.mp4"], stdin=subprocess.PIPE)
    with Pool(2) as pool:
        for k, fr in enumerate(pool.imap(render, range(N), chunksize=6)):
            ff.stdin.write(fr)
            if k % 150 == 0:
                print(f"frame {k}/{N}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done", T_TOTAL)
