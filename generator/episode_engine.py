"""Tiny Explorer episode engine.

Write an episode as a list of beats (see episodes/ for examples), then:
    python3 generator/episode_engine.py episodes/<file>.py            # 16:9 episode + thumbnail
    python3 generator/episode_engine.py episodes/<file>.py --stills   # contact sheet only (fast review)
    python3 generator/episode_engine.py episodes/<file>.py --short 1  # vertical Short from SHORTS[0]

Beat types: hello, say, count, ask, lesson, grownup, recap, bye (and the branded intro is added automatically).
"""
import math, os, random, subprocess, sys, importlib.util
import numpy as np
from PIL import Image, ImageDraw
from multiprocessing import Pool
from scipy.io import wavfile
from scipy.signal import butter, lfilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_video as mv
from make_video import ell, poly, line, font, DRAW, NUM_COLORS, INK, P, S, star_pts, ease_out_back, clamp01, tone, mtof

FPS = 30
BEAT = 0.5
SR = 44100
CFG = {"W": 1920, "H": 1080}


def W(): return CFG["W"]
def H(): return CFG["H"]
def U(): return min(W(), H()) / 1080.0          # unit scale so vertical and horizontal share sizes
def VERT(): return H() > W()


def text(d, x, y, s, px, fill, stroke=8, stroke_fill=INK, anchor="mm"):
    d.text((P(x), P(y)), s, font=font(max(6, int(px))), fill=fill, stroke_width=int(P(stroke)),
           stroke_fill=stroke_fill, anchor=anchor)


def ease_in_out(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


# ----------------------------------------------------------------- scenes
_BG = {}


def _grad(top, bot):
    img = Image.new("RGB", (W() * S, H() * S))
    g = np.linspace(0, 1, H() * S)[:, None]
    a = (np.array(top) * (1 - g) + np.array(bot) * g).astype(np.uint8)
    img.paste(Image.fromarray(np.repeat(a[:, None, :], W() * S, axis=1)))
    return img


def _hills(d, c1="#9be15d", c2="#6fcf4a", lift=0):
    w, h = W(), H()
    gy = h * 0.80 - lift
    ell(d, w * 0.18, gy + h * 0.12, w * 0.55, h * 0.24, c1)
    ell(d, w * 0.86, gy + h * 0.14, w * 0.6, h * 0.26, c1)
    ell(d, w * 0.5, gy + h * 0.26, w * 0.85, h * 0.3, c2)
    rnd = random.Random(4)
    for _ in range(int(14 * w / 1920 + 6)):
        x, y = rnd.uniform(0.03, 0.97) * w, rnd.uniform(gy + h * 0.06, h * 0.98)
        ell(d, x, y, 9 * U(), 9 * U(), "#ffffff", ow=0)
        ell(d, x, y, 4 * U(), 4 * U(), "#ffd60a", ow=0)


def _tree(d, x, y, s):
    d.rectangle([P(x - 0.12 * s), P(y - 0.2 * s), P(x + 0.12 * s), P(y + 1.0 * s)], fill="#8a5a2b", outline=INK, width=int(P(4)))
    for dx, dy, r in [(-0.45, -0.55, 0.55), (0.45, -0.55, 0.55), (0, -0.95, 0.65), (0, -0.4, 0.6)]:
        ell(d, x + dx * s, y + dy * s, r * s + 4, r * s + 4, INK, ow=0)
    for dx, dy, r in [(-0.45, -0.55, 0.55), (0.45, -0.55, 0.55), (0, -0.95, 0.65), (0, -0.4, 0.6)]:
        ell(d, x + dx * s, y + dy * s, r * s, r * s, "#57cc04", ow=0)
    for dx, dy in [(-0.5, -0.6), (0.35, -0.9), (0.55, -0.35), (-0.1, -0.3), (0.1, -1.2)]:
        ell(d, x + dx * s, y + dy * s, 0.09 * s, 0.09 * s, "#e63946", ow=3)


def scene_bg(name):
    key = (name, W(), H())
    if key in _BG:
        return _BG[key]
    w, h = W(), H()
    if name == "night":
        img = _grad((40, 40, 110), (110, 90, 170)); d = ImageDraw.Draw(img)
        rnd = random.Random(2)
        for _ in range(60):
            x, y, r = rnd.uniform(0, w), rnd.uniform(0, h * 0.6), rnd.uniform(1.5, 4)
            ell(d, x, y, r * U(), r * U(), "#fff6c4", ow=0)
        ell(d, w * 0.82, h * 0.18, 70 * U(), 70 * U(), "#fff1a8", ow=4)
        ell(d, w * 0.85, h * 0.16, 62 * U(), 62 * U(), (60, 55, 125), ow=0)
        _hills(d, "#3f8f4a", "#2f7a3c")
    elif name == "beach":
        img = _grad((110, 205, 255), (215, 245, 255)); d = ImageDraw.Draw(img)
        d.rectangle([0, P(h * 0.55), P(w), P(h * 0.75)], fill="#3fb8e8")
        for i in range(8):
            yy = h * (0.58 + i * 0.022)
            line(d, [(w * (0.05 + 0.11 * k), yy) for k in range(10)], fill="#9ee0fa", w=3)
        ell(d, w * 0.5, h * 1.02, w * 0.9, h * 0.34, "#ffe29a")
        ell(d, w * 0.12, h * 0.16, 70 * U(), 70 * U(), "#ffd60a")
    elif name == "room":
        img = _grad((255, 236, 205), (255, 214, 170)); d = ImageDraw.Draw(img)
        d.rectangle([0, P(h * 0.72), P(w), P(h)], fill="#e8a86c", outline=INK, width=int(P(4)))
        for i in range(9):
            x = w * i / 8
            line(d, [(x, h * 0.72), (x - w * 0.06, h)], fill="#d18f55", w=3)
        wx, wy, ww, wh = w * 0.62, h * 0.12, w * 0.24, h * 0.32
        if VERT():
            wx, ww = w * 0.5, w * 0.4
        d.rounded_rectangle([P(wx), P(wy), P(wx + ww), P(wy + wh)], radius=int(P(18)), fill="#9fdcff", outline=INK, width=int(P(5)))
        line(d, [(wx + ww / 2, wy), (wx + ww / 2, wy + wh)], w=5)
        line(d, [(wx, wy + wh / 2), (wx + ww, wy + wh / 2)], w=5)
        ell(d, w * 0.5, h * 0.9, w * 0.32, h * 0.06, "#8b5cf6", ow=4)
    else:  # meadow, orchard
        img = _grad((110, 200, 255), (220, 245, 255)); d = ImageDraw.Draw(img)
        _hills(d)
        if name == "orchard":
            s = 160 * U()
            _tree(d, w * 0.07, h * 0.62, s)
            _tree(d, w * 0.93, h * 0.6, s * 1.05)
    _BG[key] = img
    return img


def outdoor(name):
    return name in ("meadow", "orchard", "beach")


def clouds(d, t):
    w, h = W(), H()
    for x0, y, s, v in [(0.1, 0.12, 80, 16), (0.47, 0.08, 62, 11), (0.78, 0.15, 90, 20), (0.6, 0.28, 50, 8)]:
        x = (x0 * w + t * v) % (w + 400) - 200
        mv.cloud(d, x, y * h, s * U())


# ----------------------------------------------------------------- characters
def hop_at(t, amp):
    p = (t % BEAT) / BEAT
    return abs(math.sin(math.pi * p)) * amp


def eyes(d, cx, cy, r, mood, t, look=0.0, blink_seed=0.0):
    blink = ((t + blink_seed) % 3.3) < 0.11
    for s_ in (-1, 1):
        ex, ey = cx + s_ * 0.33 * r, cy - 0.2 * r
        if mood == "excited":
            d.arc([P(ex - 0.15 * r), P(ey - 0.1 * r), P(ex + 0.15 * r), P(ey + 0.16 * r)], 200, 340, fill=INK, width=int(P(max(4, r * 0.06))))
            continue
        if blink:
            line(d, [(ex - 0.15 * r, ey), (ex + 0.15 * r, ey)], w=max(4, r * 0.05))
            continue
        big = 1.18 if mood == "surprised" else 1.0
        ell(d, ex, ey, 0.21 * r * big, 0.26 * r * big, "white")
        pr = 0.08 if mood == "surprised" else 0.115
        dy = 0.06 * r if mood == "sad" else 0.03 * r
        ell(d, ex + look * 0.07 * r, ey + dy, pr * r, pr * 1.15 * r, INK, ow=0)
        ell(d, ex + look * 0.07 * r + 0.035 * r, ey + dy - 0.04 * r, 0.04 * r, 0.04 * r, "white", ow=0)
        if mood == "sad":
            line(d, [(ex - s_ * 0.2 * r, ey - 0.36 * r), (ex + s_ * 0.05 * r, ey - 0.27 * r)], w=max(4, r * 0.05))


def mouth(d, cx, cy, r, mood, talk, t):
    open_ = (0.5 + 0.5 * math.sin(t * 22)) if talk else 0
    if mood == "sad" and not talk:
        d.arc([P(cx - 0.2 * r), P(cy + 0.12 * r), P(cx + 0.2 * r), P(cy + 0.4 * r)], 200, 340, fill=INK, width=int(P(max(4, r * 0.05))))
    elif mood == "surprised" and not talk:
        ell(d, cx, cy + 0.2 * r, 0.09 * r, 0.12 * r, "#b5223b", ow=4)
    else:
        hgt = 0.2 + 0.18 * open_ + (0.08 if mood == "excited" else 0)
        d.chord([P(cx - 0.25 * r), P(cy - 0.05 * r), P(cx + 0.25 * r), P(cy + hgt * 2 * r)], 0, 180,
                fill="#b5223b", outline=INK, width=int(P(5)))
        ell(d, cx, cy + hgt * 1.4 * r, 0.1 * r, 0.05 * r, "#ff8fab", ow=0)


def bobo(d, cx, cy, r, t, mood="happy", talk=False, wave=False, hop=True, look=0.0, glass=False, hold=None,
         hat=True, squash=0.0, lift=0.0):
    amp = (40 if mood == "excited" else 20) if hop else 0
    hh = hop_at(t, amp) + lift
    y = cy - hh
    sq = (1 - min(hh, amp) / max(amp, 1)) * 0.07 if hop else 0
    sq += squash
    sx, sy = 1 + sq, 1 - sq
    y += r * squash * 0.9
    ell(d, cx, cy + r * 0.98, r * (0.9 - 0.25 * min(hh, max(amp, 1)) / max(amp, 1)) * (1 - 0.5 * min(lift / (r * 1.5), 1)), r * 0.14, (40, 90, 40), ow=0)
    ell(d, cx - 0.4 * r, y + 0.9 * r, r * 0.3, r * 0.16, "#e86a1c")
    ell(d, cx + 0.4 * r, y + 0.9 * r, r * 0.3, r * 0.16, "#e86a1c")
    # arms
    ell(d, cx - r * 0.93, y + 0.15 * r, r * 0.17, r * 0.24, "#ff8c42")
    if wave:
        a = -2.2 + 0.55 * math.sin(t * 9)
        hx, hy = cx + r * 0.85 + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.6
        line(d, [(cx + r * 0.8, y), (hx, hy)], fill=INK, w=r * 0.2)
        line(d, [(cx + r * 0.8, y), (hx, hy)], fill="#ff8c42", w=r * 0.12)
        ell(d, hx, hy, r * 0.15, r * 0.15, "#ff8c42")
    elif hold is None and not glass:
        ell(d, cx + r * 0.93, y + 0.15 * r, r * 0.17, r * 0.24, "#ff8c42")
    # body
    ell(d, cx, y, r * sx, r * sy, "#ff8c42")
    ell(d, cx, y + 0.35 * r, r * 0.55 * sx, r * 0.42 * sy, "#ffd3a8", ow=0)
    eyes(d, cx, y, r, mood, t, look)
    ell(d, cx - 0.6 * r, y + 0.08 * r, 0.12 * r, 0.07 * r, "#ff6f91", ow=0)
    ell(d, cx + 0.6 * r, y + 0.08 * r, 0.12 * r, 0.07 * r, "#ff6f91", ow=0)
    mouth(d, cx, y, r, mood, talk, t)
    if hat:
        draw_hat(d, cx, y - r * sy * 0.93, r)
    if glass:
        gx, gy = cx + r * 1.25, y - r * 0.25
        line(d, [(cx + r * 0.95, y + r * 0.25), (gx - 0.23 * r, gy + 0.3 * r)], fill=INK, w=0.18 * r)
        line(d, [(cx + r * 0.95, y + r * 0.25), (gx - 0.23 * r, gy + 0.3 * r)], fill="#8a5a2b", w=0.1 * r)
        ell(d, gx, gy, 0.4 * r, 0.4 * r, "#d7f3ff", ow=8)
        ell(d, cx + r * 0.95, y + r * 0.25, r * 0.15, r * 0.15, "#ff8c42")
    if hold is not None:
        hx, hy2 = cx + r * 1.05, y + r * 0.1
        DRAW[hold](d, hx, hy2, r * 0.32, t, 0)
        ell(d, cx + r * 0.85, y + r * 0.25, r * 0.15, r * 0.15, "#ff8c42")


def draw_hat(d, cx, hy, r, ang=0.0):
    """Bobo's explorer hat; hy is the brim line, r is Bobo's radius. ang tilts it (radians)."""
    if abs(ang) > 0.01:
        layer = Image.new("RGBA", (int(P(r * 3)), int(P(r * 3))), (0, 0, 0, 0))
        draw_hat(ImageDraw.Draw(layer), r * 1.5, r * 1.6, r)
        layer = layer.rotate(math.degrees(-ang), resample=Image.BICUBIC)
        d._image.paste(layer, (int(P(cx - r * 1.5)), int(P(hy - r * 1.6))), layer)
        return
    ell(d, cx, hy + 10 * U(), r * 0.95, r * 0.2, "#c8963e")
    d.chord([P(cx - r * 0.58), P(hy - r * 0.62), P(cx + r * 0.58), P(hy + r * 0.5)], 180, 360, fill="#e0b25c", outline=INK, width=int(P(5)))
    d.rectangle([P(cx - r * 0.57), P(hy - 0.12 * r), P(cx + r * 0.57), P(hy - 0.015 * r)], fill="#8a5a2b")
    ell(d, cx, hy - 0.35 * r, 0.075 * r, 0.075 * r, "#8a5a2b", ow=0)


def pip(d, cx, cy, r, t, mood="happy", talk=False, hop=True, look=0.0, flap=False):
    amp = (36 if mood == "excited" else 16) if hop else 0
    hh = hop_at(t + 0.25, amp)
    y = cy - hh
    line(d, [(cx - 0.25 * r, cy + 0.85 * r), (cx - 0.3 * r, cy + 1.05 * r)], fill="#ff8c1a", w=6)
    line(d, [(cx + 0.25 * r, cy + 0.85 * r), (cx + 0.3 * r, cy + 1.05 * r)], fill="#ff8c1a", w=6)
    fa = math.sin(t * (16 if flap or mood == "excited" else 3)) * (0.5 if flap or mood == "excited" else 0.12)
    for s_ in (-1, 1):
        wx = cx + s_ * 0.92 * r
        pts = [(wx - s_ * 0.15 * r, y - 0.1 * r), (wx + s_ * 0.45 * r, y - 0.35 * r - fa * r * s_ * s_), (wx + s_ * 0.3 * r, y + 0.3 * r)]
        poly(d, pts, "#2a9fd6")
    # tuft
    poly(d, [(cx - 0.1 * r, y - 0.95 * r), (cx, y - 1.3 * r), (cx + 0.12 * r, y - 0.95 * r)], "#2a9fd6")
    ell(d, cx, y, r, r * 0.95, "#4cc9f0")
    ell(d, cx, y + 0.35 * r, r * 0.55, r * 0.45, "#c9f1ff", ow=0)
    eyes(d, cx, y - 0.05 * r, r * 0.95, mood, t, look, blink_seed=1.3)
    # beak
    op = (0.5 + 0.5 * math.sin(t * 24)) * 0.12 * r if talk else 0
    poly(d, [(cx - 0.17 * r, y + 0.08 * r), (cx + 0.17 * r, y + 0.08 * r), (cx, y + 0.3 * r)], "#ffb703")
    if op > 0:
        poly(d, [(cx - 0.12 * r, y + 0.16 * r + op), (cx + 0.12 * r, y + 0.16 * r + op), (cx, y + 0.34 * r + op)], "#ffb703")
    ell(d, cx - 0.55 * r, y + 0.12 * r, 0.11 * r, 0.065 * r, "#ff8fab", ow=0)
    ell(d, cx + 0.55 * r, y + 0.12 * r, 0.11 * r, 0.065 * r, "#ff8fab", ow=0)
    if mood == "sad":
        ell(d, cx + 0.42 * r, y + 0.02 * r + (t % 1.2) * 0.4 * r, 0.05 * r, 0.08 * r, "#7fd7ff", ow=2)


# ----------------------------------------------------------------- ui pieces
def wrap(s, px, maxw):
    f = font(int(px)); words = s.split(); lines = []; cur = ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if f.getlength(trial) / S <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines


def bubble(d, x, y, s, px, shown, tail, maxw=None):
    """Speech bubble centred at x, with its bottom edge at y; tail points to (tx, ty)."""
    maxw = maxw or (W() * (0.8 if VERT() else 0.5))
    lines = wrap(s, px, maxw)
    f = font(int(px))
    bw = max(f.getlength(l) / S for l in lines) + 70 * U()
    bh = len(lines) * px * 1.25 + 46 * U()
    x0 = min(max(x - bw / 2, 24 * U()), W() - bw - 24 * U())
    y0 = y - bh
    tx, ty = tail
    bx = min(max(tx, x0 + 40 * U()), x0 + bw - 40 * U())
    poly(d, [(bx - 26 * U(), y - 4), (bx + 26 * U(), y - 4), (tx, ty)], "white", ow=5)
    d.rounded_rectangle([P(x0), P(y0), P(x0 + bw), P(y)], radius=int(P(34 * U())), fill="white", outline=INK, width=int(P(5)))
    d.polygon([(P(bx - 22 * U()), P(y - 8)), (P(bx + 22 * U()), P(y - 8)), (P(bx), P(y + 6))], fill="white")
    left = shown
    for i, l in enumerate(lines):
        vis = l[:max(0, left)]
        left -= len(l) + 1
        if vis:
            d.text((P(x0 + 35 * U()), P(y0 + 23 * U() + i * px * 1.25)), vis, font=f, fill=INK)


def big_word(d, x, y, s, px, color, t0, t, stroke=12):
    a = ease_out_back((t - t0) / 0.4)
    if a > 0.02:
        text(d, x, y - (1 - a) * 60 * U(), s, px * max(a, 0.3), color, stroke=stroke * U())


def badge(d):
    if VERT():
        x0, y0 = W() / 2 - 200, 60
    else:
        x0, y0 = 36, 30
    d.rounded_rectangle([P(x0), P(y0), P(x0 + 360), P(y0 + 64)], radius=int(P(32)), fill="white", outline=INK, width=int(P(4)))
    f = font(38); xx = x0 + 26
    for k, c in enumerate("Tiny Explorer"):
        w = f.getlength(c) / S
        if c != " ": text(d, xx + w / 2, y0 + 33, c, 38, NUM_COLORS[k % 10], stroke=4)
        xx += w


_BADGE = {}


def badge_layer():
    key = (W(), H())
    if key not in _BADGE:
        im = Image.new("RGBA", (W() * S, H() * S), (0, 0, 0, 0))
        badge(ImageDraw.Draw(im))
        im = im.reduce(S)
        box = im.getbbox()
        crop = im.crop(box)
        _BADGE[key] = (crop, (box[0], box[1]), crop)
    return _BADGE[key]


def countdown(d, x, y, n_left, frac, r):
    ell(d, x, y, r, r, "white", ow=6)
    d.arc([P(x - r + 10), P(y - r + 10), P(x + r - 10), P(y + r - 10)], -90, -90 + 360 * (1 - frac), fill="#ff595e", width=int(P(12)))
    text(d, x, y + 4, str(n_left), r * 1.1, "#2d2340", stroke=0)


def confetti(d, lt, n=120, seed=7):
    rnd = random.Random(seed)
    for k in range(n):
        x0 = rnd.uniform(0, W()); sp = rnd.uniform(200, 420); delay = rnd.uniform(0, 1.0)
        c = NUM_COLORS[rnd.randrange(10)]
        yy = -40 + (lt - delay) * sp
        if yy < -40 or yy > H() + 40: continue
        xx = x0 + math.sin(lt * 3 + k) * 30
        ang = lt * 5 + k
        pts = [(xx + math.cos(ang + q * math.pi / 2 + 0.4 * (q % 2)) * 14 * U(), yy + math.sin(ang + q * math.pi / 2 + 0.4 * (q % 2)) * 8 * U()) for q in range(4)]
        poly(d, pts, c, ow=0)


def grid_positions(n, area):
    """Lay out n items in area (x0, y0, x1, y1); returns (x, y, size)."""
    x0, y0, x1, y1 = area
    w, h = x1 - x0, y1 - y0
    best = None
    for cols in range(1, n + 1):
        rows = math.ceil(n / cols)
        s = min(w / cols, h / rows) * 0.36
        score = s * (1 - 0.12 * (rows - 1))
        if best is None or score > best[0]: best = (score, cols, rows, s)
    _, cols, rows, s = best
    out = []
    for i in range(n):
        r_, c_ = divmod(i, cols)
        in_row = min(cols, n - r_ * cols)
        cx = x0 + w / 2 + (c_ - (in_row - 1) / 2) * (w / cols)
        cy = y0 + h / 2 + (r_ - (rows - 1) / 2) * (h / rows)
        out.append((cx, cy, s))
    return out


# ----------------------------------------------------------------- timeline
TYPE_RATE = 20.0          # characters per second in bubbles


def beat_len(b):
    k = b["type"]
    if k in ("say", "hello", "grownup", "lesson_say"):
        return b.get("dur", max(2.6, len(b["text"]) / TYPE_RATE + 1.6))
    if k == "count":
        return b.get("dur", 2.0 + b["n"] * 2 * BEAT + 2.5)
    if k == "ask":
        return b.get("dur", 3.0 + 3.0 + 2.2)
    if k == "lesson":
        return b.get("dur", 7.0)
    if k == "recap":
        return b.get("dur", 6.0)
    if k == "bye":
        return b.get("dur", 5.0)
    if k == "gag":
        return b.get("dur", GAG_DUR[b["gag"]])
    return b.get("dur", 3.0)


def timeline(beats, intro=True):
    out, t = [], (3.5 if intro else 0.0)
    for b in beats:
        L = beat_len(b)
        out.append((t, t + L, b)); t += L
    return out, t


# ----------------------------------------------------------------- beat renderers
def cast_pos(b):
    w, h = W(), H()
    if VERT():
        return (w * 0.3, h * 0.72), (w * 0.72, h * 0.7)
    return (w * 0.28, h * 0.74), (w * 0.72, h * 0.72)


def draw_cast(d, b, t, talker=None, lt=0.0):
    (bx, by), (px, py) = cast_pos(b)
    rb, rp = 175 * U(), 115 * U()
    bm = b.get("bobo", "happy"); pm = b.get("pip", "happy")
    show_pip = b.get("show_pip", True)
    bobo(d, bx, by, rb, t, mood=bm, talk=(talker == "bobo"), wave=b.get("wave", False), look=0.6 if show_pip else 0,
         glass=b.get("glass", False), hold=b.get("hold"))
    if show_pip:
        pip(d, px, py, rp, t, mood=pm, talk=(talker == "pip"), look=-0.6, flap=b.get("flap", False))
    return (bx, by, rb), (px, py, rp)


def r_say(d, b, lt, t):
    who = b.get("who", "bobo")
    if b["type"] == "hello":
        b = dict(b, wave=True, show_pip=b.get("show_pip", False))
    if b["type"] == "grownup":
        b = dict(b, show_pip=b.get("show_pip", True))
    (bx, by, rb), (px, py, rp) = draw_cast(d, b, t, talker=who if lt < len(b["text"]) / TYPE_RATE + 0.2 else None, lt=lt)
    shown = int(lt * TYPE_RATE)
    sx, sy, sr = (bx, by, rb) if who == "bobo" else (px, py, rp)
    by_top = sy - sr * (1.75 if who == "bobo" else 1.45)
    if b.get("show_pip", True) or who == "pip":
        by_top = min(by_top, by - rb * 1.75, py - rp * 1.45)
    px_ = 58 * U()
    bubble(d, sx if not VERT() else W() / 2, by_top, b["text"], px_, shown, (sx, sy - sr * 1.15))
    if b["type"] == "grownup":
        big_word(d, W() / 2, H() * (0.16 if VERT() else 0.14), "With your grown-up!", 76 * U(), "#ffca3a", 0.2, lt)


def r_count(d, b, lt, t):
    n, thing = b["n"], b["thing"]
    w, h = W(), H()
    title = b.get("title", "Let's explore!")
    big_word(d, w / 2, h * (0.14 if VERT() else 0.12), title, 92 * U(), "#ffca3a", 0.0, lt)
    area = (w * 0.08, h * 0.3, w * 0.92, h * 0.62) if VERT() else (w * 0.17, h * 0.32, w * 0.86, h * 0.8)
    pts = grid_positions(n, area)
    t0 = 1.5
    shown = 0
    for i, (x, y, s) in enumerate(pts):
        tp = t0 + i * 2 * BEAT
        sc = ease_out_back((lt - tp) / 0.3)
        if sc > 0.02:
            shown = i + 1
            DRAW[thing](d, x, y, s * sc, t, i)
            ly = y - s * 1.5 - 26 * U()
            ell(d, x, ly, 34 * U() * sc, 34 * U() * sc, NUM_COLORS[i % 10], ow=4)
            text(d, x, ly + 2, str(i + 1), 42 * U() * sc, "white", stroke=4)
    done_t = t0 + n * 2 * BEAT + 0.3
    if shown and lt <= done_t:
        words =["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"]
        nm = b.get("names", words)[shown - 1] if not b.get("label_fn") else b["label_fn"](shown)
        k = (lt - (t0 + (shown - 1) * 2 * BEAT)) / 0.35
        text(d, w / 2, h * (0.70 if VERT() else 0.9), nm + "!", (96 if VERT() else 84) * U() * (0.6 + 0.4 * ease_out_back(k)), NUM_COLORS[(shown - 1) % 10], stroke=10 * U())
    done_t = t0 + n * 2 * BEAT + 0.3
    if lt > done_t:
        a = ease_out_back((lt - done_t) / 0.4)
        lbl = b.get("total", f"{n} {thing}s!")
        text(d, w / 2, h * (0.78 if VERT() else 0.9) + (0 if VERT() else 0), lbl, 88 * U() * max(a, 0.3), "#fff7d6", stroke=10 * U())
    bobo(d, w * (0.2 if VERT() else 0.1), h * (0.88 if VERT() else 0.83), 105 * U(), t, mood="excited" if lt > done_t else "happy", glass=True)


def r_ask(d, b, lt, t):
    w, h = W(), H()
    q = b["q"]; ans = b["a"]
    ty = h * (0.16 if VERT() else 0.13)
    lines = wrap(q, 74 * U(), w * (0.86 if VERT() else 0.7))
    for i, l in enumerate(lines):
        big_word(d, w / 2, ty + i * 86 * U(), l, 74 * U(), "white", 0.0, lt, stroke=10)
    top = ty + len(lines) * 86 * U() + 30 * U()
    area = (w * 0.08, top + 40 * U(), w * 0.92, h * 0.66) if VERT() else (w * 0.17, top + 40 * U(), w * 0.86, h * 0.76)
    show = b.get("show")
    if show:
        thing, n = show
        for i, (x, y, s) in enumerate(grid_positions(n, area)):
            DRAW[thing](d, x, y, s * min(1, ease_out_back((lt - 0.4 - i * 0.08) / 0.3)), t, i)
    t_your = 2.2
    t_reveal = t_your + 3.0
    if t_your <= lt < t_reveal:
        frac = (lt - t_your) / 3.0
        cx, cy = (w * 0.5, h * 0.69) if VERT() else (w * 0.5 + 300 * U(), h * 0.88)
        countdown(d, cx, cy, 3 - int(frac * 3), frac, 62 * U())
        big_word(d, w / 2 - (0 if VERT() else 60 * U()), h * (0.78 if VERT() else 0.88), "Your turn!", 80 * U(), "#ffca3a", t_your, lt)
    if lt >= t_reveal:
        a = ease_out_back((lt - t_reveal) / 0.35)
        cy = h * (0.74 if VERT() else 0.88)
        d.rounded_rectangle([P(w / 2 - 330 * U() * a), P(cy - 70 * U()), P(w / 2 + 330 * U() * a), P(cy + 70 * U())], radius=int(P(70 * U())), fill="#8ac926", outline=INK, width=int(P(6)))
        text(d, w / 2, cy + 3, ans, 84 * U() * max(a, 0.3), "white", stroke=8 * U())
        big_word(d, w / 2, cy - (120 if VERT() else 110) * U(), "Yay, you did it!", 60 * U(), "#ffca3a", t_reveal + 0.3, lt)
    mood = "surprised" if lt < t_your else ("happy" if lt < t_reveal else "excited")
    bobo(d, w * (0.2 if VERT() else 0.1), h * (0.88 if VERT() else 0.83), 105 * U(), t, mood=mood, glass=lt < t_reveal)


def r_lesson(d, b, lt, t):
    """Bobo gives an item to Pip, Pip cheers, lesson card."""
    w, h = W(), H()
    (bx, by), (px, py) = cast_pos(b)
    item = b.get("item", "apple")
    give_t0, give_t1 = 0.8, 2.6
    pm = "sad" if lt < give_t1 else "excited"
    bobo(d, bx, by, 175 * U(), t, mood="happy" if lt < give_t1 else "excited", hold=item if lt < give_t0 else None)
    pip(d, px, py, 115 * U(), t, mood=pm, flap=lt > give_t1)
    if give_t0 <= lt <= give_t1 + 3:
        k = ease_in_out((lt - give_t0) / (give_t1 - give_t0))
        sx, sy = bx + 175 * U() * 1.05, by
        ex, ey = px - 115 * U() * 0.9, py
        x = sx + (ex - sx) * k
        y = sy + (ey - sy) * k - math.sin(k * math.pi) * 180 * U()
        DRAW[item](d, x, y, 58 * U(), t, 1)
    if lt > give_t1:
        for k in range(6):
            a = (lt - give_t1) * 2 + k
            hx = px + math.cos(a) * 160 * U(); hy = py - 160 * U() + math.sin(a * 1.3) * 60 * U() - (lt - give_t1) * 30 * U()
            DRAW["heart"](d, hx, hy, 26 * U(), t, k)
    if lt > give_t1 + 0.8:
        a = ease_out_back((lt - give_t1 - 0.8) / 0.45)
        cy = h * (0.17 if VERT() else 0.16)
        lines = wrap(b["lesson"], 76 * U(), w * 0.8)
        bh = len(lines) * 90 * U() + 50 * U()
        bw = max(font(int(76 * U())).getlength(l) / S for l in lines) + 90 * U()
        d.rounded_rectangle([P(w / 2 - bw / 2 * a), P(cy - bh / 2), P(w / 2 + bw / 2 * a), P(cy + bh / 2)], radius=int(P(40 * U())), fill="#ff8c42", outline=INK, width=int(P(6)))
        if a > 0.6:
            for i, l in enumerate(lines):
                text(d, w / 2, cy - (len(lines) - 1) * 45 * U() + i * 90 * U() + 4, l, 76 * U(), "white", stroke=8 * U())


def r_recap(d, b, lt, t):
    w, h = W(), H()
    big_word(d, w / 2, h * 0.13, b.get("title", "Sing it again!"), 88 * U(), "#ffca3a", 0, lt)
    items = b["items"]
    area = (w * 0.08, h * 0.25, w * 0.92, h * 0.65) if VERT() else (w * 0.17, h * 0.26, w * 0.86, h * 0.72)
    pts = grid_positions(len(items), area)
    active = int(lt / (2 * BEAT)) % len(items)
    for i, ((x, y, s), it) in enumerate(zip(pts, items)):
        k = 1.25 if i == active else 1.0
        DRAW[it](d, x, y, s * k, t, i)
    words = b.get("chorus", "One, two, three, explore with me!")
    shown = int(len(words) * clamp01(lt / (len(words) / 12.0)))
    wl = wrap(words, 62 * U(), w * 0.62)
    left = shown
    for i, l in enumerate(wl):
        vis = l[:max(0, left)]; left -= len(l) + 1
        if vis:
            d.text((P(w / 2 - font(int(62 * U())).getlength(l) / S / 2), P(h * (0.72 if VERT() else 0.8) + i * 74 * U())), vis,
                   font=font(int(62 * U())), fill="white", stroke_width=int(P(7 * U())), stroke_fill=INK)
    bobo(d, w * (0.2 if VERT() else 0.1), h * (0.88 if VERT() else 0.83), 105 * U(), t, mood="excited", glass=False)


def r_bye(d, b, lt, t):
    w, h = W(), H()
    confetti(d, lt)
    (bx, by), (px, py) = cast_pos(b)
    bobo(d, bx, by, 175 * U(), t, mood="excited", wave=True)
    pip(d, px, py, 115 * U(), t, mood="excited", flap=True)
    if VERT():
        big_word(d, w / 2, h * 0.16, "Bye-bye,", 110 * U(), "#ff8c42", 0.3, lt)
        big_word(d, w / 2, h * 0.16 + 125 * U(), "explorers!", 110 * U(), "#ff8c42", 0.45, lt)
    else:
        big_word(d, w / 2, h * 0.2, "Bye-bye, explorers!", 104 * U(), "#ff8c42", 0.3, lt)
    if b.get("next"):
        big_word(d, w / 2, h * (0.34 if VERT() else 0.34), b["next"], 52 * U(), "white", 1.2, lt, stroke=7)


RENDER = {"say": r_say, "hello": r_say, "grownup": r_say, "count": r_count, "ask": r_ask,
          "lesson": r_lesson, "recap": r_recap, "bye": r_bye}


# ----------------------------------------------------------------- frame
EP = {}


def load_episode(path):
    spec = importlib.util.spec_from_file_location("ep", path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def camera_crop(lt, L, b):
    """Gentle drift: slow zoom toward the speaker on dialogue beats."""
    if b["type"] in ("say", "hello", "grownup"):
        z = 1.0 + 0.06 * ease_in_out(lt / max(L, 0.1))
        (bx, by), (px, py) = cast_pos(b)
        fx = bx if b.get("who", "bobo") == "bobo" else px
        fx = (fx * 0.35 + W() / 2 * 0.65)
        fy = H() * 0.55
    else:
        z = 1.0 + 0.02 * (0.5 + 0.5 * math.sin(lt * 0.6))
        fx, fy = W() / 2, H() / 2
    cw, ch = W() / z, H() / z
    x0 = min(max(fx - cw / 2, 0), W() - cw); y0 = min(max(fy - ch / 2, 0), H() - ch)
    return (x0 * S, y0 * S, (x0 + cw) * S, (y0 + ch) * S)


def render_frame(i):
    t = i / FPS
    tl, total, intro = EP["tl"], EP["total"], EP["intro"]
    if intro and t < 3.5:
        import brand
        return brand.frame(t) if not VERT() else _vertical_intro(t)
    seg = next((s for s in tl if s[0] <= t < s[1]), tl[-1])
    t0, t1, b = seg
    lt = t - t0
    scene = b.get("scene", EP["scene"])
    img = scene_bg(scene).copy()
    d = ImageDraw.Draw(img)
    if outdoor(scene):
        clouds(d, t)
    RENDER[b["type"]](d, b, lt, t)
    out = img.resize((W(), H()), Image.BILINEAR, box=camera_crop(lt, t1 - t0, b), reducing_gap=2.0)
    out.paste(*badge_layer())
    # white dip on scene cuts
    prev = next((s for s in tl if s[1] == t0), None)
    cut = prev is not None and prev[2].get("scene", EP["scene"]) != scene
    fade = 1.0
    if cut and lt < 0.3: fade = min(fade, lt / 0.3)
    if t < (3.6 if intro else 0.3): fade = min(fade, clamp01((t - (3.5 if intro else 0)) / 0.3))
    fade = min(fade, clamp01((total - t) / 0.6))
    if fade < 1:
        out = Image.blend(Image.new("RGB", out.size, "white"), out, fade)
    return out.tobytes()


def _vertical_intro(t):
    img = scene_bg("meadow").copy(); d = ImageDraw.Draw(img)
    clouds(d, t + 10)
    a = ease_out_back((t - 0.1) / 0.6)
    bobo(d, W() / 2, H() * 1.25 - a * H() * 0.55, 190 * U(), t, glass=True, hop=False)
    title = "Tiny Explorer"; px = 120; f = font(px)
    tot = sum(f.getlength(c) for c in title) / S; x = W() / 2 - tot / 2
    for k, c in enumerate(title):
        w = f.getlength(c) / S
        aa = ease_out_back((t - 0.8 - k * 0.05) / 0.35)
        if c != " " and aa > 0.02:
            text(d, x + w / 2, H() * 0.28 + (1 - aa) * 120, c, px * max(aa, 0.3), NUM_COLORS[k % 10], stroke=11)
        x += w
    out = img.reduce(S)
    f2 = min(clamp01(t / 0.25), clamp01((3.5 - t) / 0.3))
    if f2 < 1: out = Image.blend(Image.new("RGB", out.size, "white"), out, f2)
    return out.tobytes()


# ----------------------------------------------------------------- audio
def make_audio(path, tl, total, intro, seed=3):
    rng = np.random.default_rng(seed)
    buf = np.zeros(int((total + 1) * SR))

    def add(sig, t, g=1.0):
        i = int(t * SR); j = min(len(buf), i + len(sig))
        if i < len(buf) and j > i: buf[i:j] += sig[: j - i] * g

    b_hp, a_hp = butter(2, 6000 / (SR / 2), "high")
    roots = [48, 43, 45, 41]
    chords = [[60, 64, 67], [59, 62, 67], [57, 60, 64], [57, 60, 65]]
    chorus = [(0, 72, 1), (1, 74, 1), (2, 76, 1), (3, 79, 1), (4, 81, .5), (4.5, 79, .5), (5, 76, 1), (6, 74, 1), (7, 72, 1),
              (8, 76, 1), (9, 76, .5), (9.5, 79, .5), (10, 81, 1), (11, 79, 1), (12, 76, .5), (12.5, 74, .5), (13, 72, 1), (14, 72, 2)]
    # music level per segment
    def level(t):
        if intro and t < 3.5: return 0.0
        seg = next((s for s in tl if s[0] <= t < s[1]), None)
        if seg is None: return 0.0
        k = seg[2]["type"]
        return 1.0 if k in ("count", "recap", "bye") else (0.55 if k == "lesson" else 0.4)
    start = 3.5 if intro else 0.0
    nb = int((total - start) / BEAT)
    for bi in range(nb):
        t = start + bi * BEAT
        g = level(t)
        if g <= 0: continue
        bar = (bi // 4) % 4
        if bi % 2 == 0:
            tt = np.arange(int(0.15 * SR)) / SR
            ph = 2 * np.pi * np.cumsum(45 + 80 * np.exp(-tt * 30)) / SR
            add(np.sin(ph) * np.exp(-tt * 16) * 0.45, t, g)
        nz = lfilter(b_hp, a_hp, rng.standard_normal(int(0.05 * SR)))
        add(nz * np.exp(-np.arange(len(nz)) / SR * 70) * 0.05, t + BEAT / 2, g)
        if bi % 4 in (0, 2):
            add(tone(mtof(roots[bar]), 0.45, 5, 0.3, (1, 0.3, 0.05)), t, g)
        for m in chords[bar]:
            add(tone(mtof(m), 0.32, 8, 0.055), t + BEAT / 2, g)
    # chorus melody in song beats
    for (t0, t1, b) in tl:
        if b["type"] in ("count", "recap", "bye"):
            k = 0; tt0 = t0
            while tt0 < t1 - 0.2:
                for bb, m, du in chorus:
                    tt = tt0 + bb * BEAT
                    if tt < t1 - 0.1:
                        add(tone(mtof(m), du * BEAT + 0.25, 4.5, 0.12, (1, 0.5, 0.2)), tt)
                tt0 += 16 * BEAT
    # sfx
    def pop(f, amp=0.3):
        tt = np.arange(int(0.25 * SR)) / SR
        ph = 2 * np.pi * np.cumsum(f * (1 + 0.5 * np.exp(-tt * 40))) / SR
        return np.sin(ph) * np.exp(-tt * 14) * amp * np.minimum(1, tt / 0.002)

    def bell(f, amp=0.22, dur=1.2):
        tt = np.arange(int(dur * SR)) / SR
        return (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2.76 * f * tt) * np.exp(-tt * 4)) * np.exp(-tt * 3) * amp

    def blip(f, amp=0.12):
        tt = np.arange(int(0.07 * SR)) / SR
        sig = np.sign(np.sin(2 * np.pi * f * tt)) * 0.3 + np.sin(2 * np.pi * f * tt)
        return sig * np.exp(-tt * 30) * amp * np.minimum(1, tt / 0.004)

    def cheer():
        out = np.zeros(int(0.9 * SR))
        for k, m in enumerate([72, 76, 79, 84, 88]):
            s = tone(mtof(m), 0.5, 6, 0.12); i = int(k * 0.06 * SR); out[i:i + len(s)] += s[: len(out) - i]
        return out

    def boing():
        tt = np.arange(int(0.35 * SR)) / SR
        ph = 2 * np.pi * np.cumsum(220 + 380 * tt / 0.35 + 30 * np.sin(tt * 60)) / SR
        return np.sin(ph) * np.exp(-tt * 6) * 0.2

    def sad():
        out = np.zeros(int(1.4 * SR))
        for k, m in enumerate([67, 65, 64, 60]):
            s = tone(mtof(m), 0.45, 5, 0.1, (1, 0.2, 0.05)); i = int(k * 0.28 * SR); out[i:i + len(s)] += s[: len(out) - i]
        return out

    scale = [72, 74, 76, 79, 81, 84, 86, 88, 91, 93]
    for (t0, t1, b) in tl:
        k = b["type"]
        if k in ("say", "hello", "grownup"):
            who = b.get("who", "bobo")
            base = [55, 57, 59, 60, 62] if who == "bobo" else [74, 76, 79, 81, 83]
            n_chars = len(b["text"]); dur = n_chars / TYPE_RATE
            r = random.Random(hash(b["text"]) & 0xffff); tt = t0
            while tt < t0 + dur:
                add(blip(mtof(r.choice(base)) * (1.0 if who == "bobo" else 1.0)), tt)
                tt += r.uniform(0.075, 0.11)
            if b.get("pip") == "sad" or b.get("bobo") == "sad":
                add(sad(), t0 + 0.2)
            if k == "hello":
                add(boing(), t0 + 0.1)
        elif k == "count":
            add(bell(mtof(84)), t0 + 0.05)
            for i in range(b["n"]):
                add(pop(mtof(scale[i % 10])), t0 + 1.5 + i * 2 * BEAT)
            add(cheer(), t0 + 1.5 + b["n"] * 2 * BEAT + 0.3)
        elif k == "ask":
            add(boing(), t0 + 0.1)
            for s_ in range(3):
                add(tone(1400, 0.08, 40, 0.18, (1, 0, 0)), t0 + 2.2 + s_)
            add(bell(mtof(88)), t0 + 5.2); add(cheer(), t0 + 5.3)
        elif k == "lesson":
            tt = np.arange(int(1.8 * SR)) / SR
            ph = 2 * np.pi * np.cumsum(500 + 500 * tt / 1.8) / SR
            add(np.sin(ph) * 0.06 * np.exp(-tt), t0 + 0.8)
            add(cheer(), t0 + 2.6); add(bell(mtof(84)), t0 + 3.4)
        elif k == "gag":
            gag_sfx(add, b, t0, tone, mtof, boing, pop, bell)
        elif k == "bye":
            for i, m in enumerate([72, 76, 79, 84, 88, 91, 96]):
                add(tone(mtof(m), 0.6, 5, 0.13), t0 + i * 0.07)
            for m in [48, 60, 64, 67, 72]:
                add(tone(mtof(m), 2.5, 1.2, 0.1), t1 - 2.6)
    if intro:
        import brand
        brand.jingle(path + ".jingle.wav")
        _, jg = wavfile.read(path + ".jingle.wav")
        add(jg.astype(np.float64) / 32767 * 0.9, 0.0)
        os.remove(path + ".jingle.wav")
    buf = buf[: int(total * SR)]
    buf /= np.max(np.abs(buf)) + 1e-9
    buf = np.tanh(buf * 1.25) / np.tanh(1.25) * 0.89
    fl = int(0.6 * SR); buf[-fl:] *= np.linspace(1, 0, fl)
    wavfile.write(path, SR, (buf * 32767).astype(np.int16))


# ----------------------------------------------------------------- thumbnail
def thumbnail(ep, path):
    CFG.update(W=1920, H=1080)
    img = scene_bg(getattr(ep, "SCENE", "meadow")).copy(); d = ImageDraw.Draw(img)
    clouds(d, 3)
    th = getattr(ep, "THUMB", {})
    big, small = th.get("big", ep.TITLE.split("|")[0].strip()), th.get("small", "")
    text(d, 1200, 230, big, th.get("px", 190), "#ffca3a", stroke=16)
    if small: text(d, 1200, 430, small, 130, "white", stroke=14)
    bobo(d, 470, 760, 230, 0.1, mood="excited", hop=False, glass=True)
    if th.get("pip", True):
        pip(d, 1560, 760, 150, 0.1, mood="excited", hop=False)
    for k, (thing, x, y, s) in enumerate(th.get("objects", [])):
        DRAW[thing](d, x, y, s, 0.3, k)
    badge(d)
    img.reduce(S).resize((1280, 720), Image.LANCZOS).save(path)


# ----------------------------------------------------------------- main
def build(ep_path, out_mp4, beats=None, vertical=False, intro=True, stills=None):
    ep = load_episode(ep_path)
    CFG.update(W=1080, H=1920) if vertical else CFG.update(W=1920, H=1080)
    tl, total = timeline(beats if beats is not None else ep.BEATS, intro=intro)
    EP.update(tl=tl, total=total, intro=intro, scene=getattr(ep, "SCENE", "meadow"))
    if stills:
        times = stills if isinstance(stills, list) else [ (s[0] + s[1]) / 2 + 0.6 for s in tl ]
        ims = [Image.frombytes("RGB", (W(), H()), render_frame(int(tt * FPS))) for tt in times]
        cols = 3 if not vertical else 4
        tw = 640 if not vertical else 270
        th = int(tw * H() / W())
        rows = math.ceil(len(ims) / cols)
        sheet = Image.new("RGB", (cols * tw, rows * th), "white")
        for k, im in enumerate(ims):
            sheet.paste(im.resize((tw, th)), ((k % cols) * tw, (k // cols) * th))
        sheet.save(out_mp4)
        return total
    wav = out_mp4 + ".wav"
    make_audio(wav, tl, total, intro)
    N = int(total * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W()}x{H()}",
                           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_mp4],
                          stdin=subprocess.PIPE)
    with Pool(os.cpu_count() or 2) as pool:
        for k, fr in enumerate(pool.imap(render_frame, range(N), chunksize=6)):
            ff.stdin.write(fr)
            if k % 300 == 0: print(f"  frame {k}/{N}", flush=True)
    ff.stdin.close(); ff.wait()
    os.remove(wav)
    return total



# ----------------------------------------------------------------- funny gags (no lesson, just giggles)
# Beat: {"type": "gag", "gag": "bonk"|"sneeze"|"peekaboo"|"hiccup"|"bubble", "caption": "...", "punch": "...", "after": "..."}
GAG_DUR = {"bonk": 7.0, "sneeze": 8.0, "peekaboo": 7.0, "hiccup": 8.5, "bubble": 7.5}


def burst(d, x, y, word, lt, t0, px=None, fill="#ffd60a", color="#ff595e", life=1.6):
    a = ease_out_back((lt - t0) / 0.25)
    if a <= 0.02 or lt - t0 > life: return
    px = px or 92 * U()
    f = font(int(px)); tw = f.getlength(word) / S
    ro = (tw / 2 + 50 * U()) * a; ri = ro * 0.78
    wob = 0.05 * math.sin(lt * 30)
    pts = [(x + math.cos(k * math.pi / 8 + wob) * (ro if k % 2 == 0 else ri) * 1.0,
            y + math.sin(k * math.pi / 8 + wob) * (ro if k % 2 == 0 else ri) * 0.62) for k in range(16)]
    poly(d, pts, fill, ow=6)
    text(d, x, y + 4, word, px * a, color, stroke=8 * U())


def dizzy(d, cx, cy, r, lt):
    for k in range(3):
        a = lt * 5 + k * 2 * math.pi / 3
        x, y = cx + math.cos(a) * r * 0.75, cy + math.sin(a) * r * 0.22
        poly(d, star_pts(x, y, 0.16 * r, 0.07 * r, a), "#ffd60a", ow=4)


def caption(d, s, lt, t0=0.0, color="white"):
    if not s or lt < t0: return
    px = (80 if VERT() else 74) * U()
    lines = wrap(s, px, W() * (0.88 if VERT() else 0.7))
    y0 = H() * (0.15 if VERT() else 0.13)
    for i, l in enumerate(lines):
        big_word(d, W() / 2, y0 + i * px * 1.15, l, px, color, t0, lt, stroke=11)


def small_word(d, x, y, s, lt, t0, t1, color="white", px=None):
    if not (t0 <= lt < t1): return
    a = ease_out_back((lt - t0) / 0.2)
    text(d, x, y - (lt - t0) * 40 * U(), s, (px or 64 * U()) * max(a, 0.3), color, stroke=8 * U())


def bump(lt, t0, up=0.18, down=0.32):
    """0 -> 1 -> 0 hop curve starting at t0."""
    x = lt - t0
    if x < 0 or x > up + down: return 0.0
    return math.sin(math.pi / 2 * x / up) if x < up else math.cos(math.pi / 2 * (x - up) / down)


def r_gag(d, b, lt, t):
    g = b["gag"]
    if VERT():
        (bx, by), (px, py) = (W() * 0.3, H() * 0.64), (W() * 0.75, H() * 0.635)
        rb, rp = 230 * U(), 150 * U()
    else:
        (bx, by), (px, py) = cast_pos(b)
        rb, rp = 175 * U(), 115 * U()
    head = by - rb * 1.55
    cap = b.get("caption", ""); after = b.get("after", "")
    if g == "bonk":
        hit = 2.3
        caption(d, cap if lt < 4.6 else after, lt, 0.0 if lt < 4.6 else 4.6)
        sq = 0.28 * math.exp(-(lt - hit) * 5) * abs(math.cos((lt - hit) * 14)) if lt > hit else 0
        mood = "happy" if lt < 1.2 else ("surprised" if lt < 4.4 else "excited")
        bobo(d, bx, by, rb, t, mood=mood, look=0 if lt > hit else -0.2, squash=sq, hop=lt > 4.4,
             hold="apple" if lt > 5.2 else None)
        pip(d, px, py, rp, t, mood="excited" if lt > hit + 0.3 else "happy", look=-0.6, flap=lt > hit + 0.3, hop=lt > hit + 0.3)
        if lt < hit:
            k = clamp01((lt - 1.2) / (hit - 1.2)) if lt > 1.2 else 0
            ay = H() * 0.22 + (head - H() * 0.22) * k * k
            if lt > 0.2: DRAW["apple"](d, bx, ay, 62 * U(), 0, 0)
        elif lt < 5.2:
            x = lt - hit
            ax = bx + x * 260 * U(); ay = head - 260 * U() * math.sin(min(x, 1.0) * math.pi) * (1 if x < 1 else 0) + (0 if x < 1 else 0)
            ay = min(ay, by + rb * 0.7) if x < 1 else by + rb * 0.7
            DRAW["apple"](d, min(ax, px - rp * 1.6), ay, 62 * U(), t, 0)
        if hit < lt < 4.4: dizzy(d, bx, head + rb * 0.15, rb, lt)
        burst(d, bx, head - 70 * U(), b.get("punch", "BONK!"), lt, hit)
        small_word(d, px, py - rp * 1.7, "Hee hee!", lt, 3.0, 4.4, "#ffca3a")
        small_word(d, bx, by - rb * 2.1, "Ha ha ha!", lt, 4.6, 6.4, "#ffca3a", 72 * U())
    elif g == "sneeze":
        ach = 2.9; land = 4.6
        caption(d, cap if lt < land + 0.3 else after, lt, 0.0 if lt < land + 0.3 else land + 0.3)
        lean = min(1, lt / ach) if lt < ach else max(0, 1 - (lt - ach) * 6)
        pip(d, px + lean * 25 * U(), py, rp, t, mood="surprised" if lt < land else "excited", look=-0.6,
            hop=lt > land, flap=lt > land)
        if lt < ach:
            ah = "Ah..." if lt < 1.4 else "Ah... ah..."
            text(d, px, py - rp * 1.8, ah, (58 + 20 * lean) * U(), "white", stroke=8 * U())
        bobo(d, bx, by, rb, t, mood="happy" if lt < ach else ("surprised" if lt < land + 0.5 else "excited"),
             hat=lt < ach, hop=lt > land + 0.5, look=0.6)
        if ach <= lt:
            for k in range(4):
                yy = by - rb * 1.75 + (k - 1.5) * 30 * U(); ph = clamp01((lt - ach) * 3 - k * 0.1)
                x0 = px - rp * 1.0 - ph * (px - bx - rp) * 0.9
                if 0 < ph < 1:
                    line(d, [(x0, yy), (x0 - 110 * U(), yy)], fill="white", w=9 * U())
            burst(d, px, py - rp * 2.3, b.get("punch", "ACHOO!"), lt, ach, life=1.0)
            k = clamp01((lt - ach) / (land - ach))
            hx = bx + (px - bx) * k
            hy0 = by - rb * 0.93; hy1 = py - rp * 0.8
            hy = hy0 + (hy1 - hy0) * k - math.sin(k * math.pi) * H() * 0.18
            draw_hat(d, hx, hy, rb * (1 - 0.15 * k), ang=(0 if k >= 1 else k * 4 * math.pi))
        small_word(d, bx, by - rb * 1.6, "Ha ha!", lt, land + 0.6, 7.5, "#ffca3a", 72 * U())
    elif g == "peekaboo":
        boo = 3.6
        caption(d, cap if lt < boo else after, lt, 0.0 if lt < boo else boo + 0.6)
        hiding = lt < boo
        bobo(d, bx, by, rb, t, mood="excited" if not hiding else "happy", hop=not hiding,
             lift=bump(lt, boo, 0.2, 0.35) * 90 * U())
        if hiding:
            rock = math.sin(lt * 4) * 0.05 * rb
            for s_ in (-1, 1):
                ell(d, bx + s_ * 0.3 * rb + rock, by - 0.2 * rb, 0.3 * rb, 0.26 * rb, "#ff8c42", ow=5)
        look = math.sin(lt * 2.2) if hiding else -0.6
        pip(d, px, py, rp, t, mood="happy" if hiding else ("surprised" if lt < boo + 0.6 else "excited"),
            look=look, flap=lt > boo + 0.6, hop=lt > boo + 0.6)
        if hiding and int(lt * 1.6) % 2 == 0:
            text(d, px, py - rp * 1.7, "?", 90 * U(), "#ffca3a", stroke=8 * U())
        burst(d, W() / 2, by - rb * 2.75, b.get("punch", "PEEK-A-BOO!"), lt, boo, px=84 * U(), life=1.3)
        small_word(d, px, py - rp * 1.7, "Hee hee!", lt, boo + 1.3, 6.5, "#ffca3a")
    elif g == "hiccup":
        hics = [0.9, 2.0, 3.0, 3.8]; boo = 5.0
        caption(d, cap if lt < boo + 1.0 else after, lt, 0.0 if lt < boo + 1.0 else boo + 1.0)
        lift = sum(bump(lt, h) for h in hics) * 110 * U() + bump(lt, boo + 0.1, 0.3, 0.6) * 260 * U()
        mood = "surprised" if lt < boo + 1.0 else "excited"
        bobo(d, bx, by, rb, t, mood=mood, hop=lt > boo + 1.0, lift=lift)
        for h in hics:
            small_word(d, bx + rb * 1.0, by - rb * 1.7 - 60 * U(), "hic!", lt, h, h + 0.7, "white", 70 * U())
        pip(d, px - (40 * U() if boo - 0.6 < lt < boo + 0.6 else 0), py, rp, t,
            mood="happy" if lt < boo - 0.6 else "excited", look=-0.6, hop=lt > boo + 0.6, flap=lt > boo + 0.6)
        burst(d, px - 40 * U(), py - rp * 2.0, b.get("punch", "BOO!"), lt, boo)
        small_word(d, bx, by - rb * 2.0, "Ha ha! All gone!", lt, boo + 1.2, 8.0, "#ffca3a", 66 * U())
    elif g == "bubble":
        pop_t = 4.8
        caption(d, cap if lt < pop_t else after, lt, 0.0 if lt < pop_t else pop_t + 0.6)
        bobo(d, bx, by, rb, t, mood="happy" if lt < pop_t else ("surprised" if lt < pop_t + 0.6 else "excited"),
             hop=lt > pop_t + 0.6, look=0.6)
        pip(d, px, py, rp, t, mood="happy" if lt < pop_t else ("surprised" if lt < pop_t + 0.6 else "excited"),
            look=-0.8, hop=lt > pop_t + 0.6, flap=lt > pop_t + 0.6)
        mx, my = bx + rb * 0.75, by + rb * 0.05
        if lt < pop_t:
            if lt < 3.0:
                rr = rb * 0.08 + rb * 0.55 * clamp01((lt - 0.5) / 2.5); cx, cy = mx + rr, my - rr * 0.4
            else:
                k = ease_in_out((lt - 3.0) / (pop_t - 3.0)); rr = rb * 0.63 * (1 - 0.3 * k)
                sx0, sy0 = mx + rb * 0.63, my - rb * 0.25
                cx = sx0 + (px - sx0) * k
                cy = sy0 + ((py + rp * 0.15) - sy0) * k - math.sin(k * math.pi) * H() * 0.12
            if lt > 0.5:
                wob = 1 + 0.04 * math.sin(lt * 9)
                bb = [P(cx - rr * wob), P(cy - rr / wob), P(cx + rr * wob), P(cy + rr / wob)]
                d.ellipse(bb, fill="#c6ecff", outline=INK, width=int(P(5)))
                d.arc([P(cx - rr * 0.82), P(cy - rr * 0.82), P(cx + rr * 0.82), P(cy + rr * 0.82)], 20, 80, fill="#f9a8d4", width=int(P(8)))
                d.arc([P(cx - rr * 0.72), P(cy - rr * 0.72), P(cx + rr * 0.72), P(cy + rr * 0.72)], 195, 250, fill="white", width=int(P(11)))
        else:
            x = lt - pop_t
            if x < 0.5:
                for k in range(10):
                    a = k * math.pi / 5
                    ell(d, px + math.cos(a) * (60 + x * 400) * U(), py + rp * 0.15 + math.sin(a) * (60 + x * 400) * U(), 9 * U(), 9 * U(), "#7fd7ff", ow=2)
        burst(d, px, py - rp * 1.9, b.get("punch", "POP!"), lt, pop_t)
        small_word(d, px, py - rp * 1.8, "Hee hee!", lt, pop_t + 0.8, 7.5, "#ffca3a")
        small_word(d, bx, by - rb * 1.8, "Ha ha!", lt, pop_t + 1.1, 7.5, "#ffca3a", 72 * U())


RENDER["gag"] = r_gag


def gag_sfx(add, b, t0, tone_, mtof_, boing_, pop_, bell_):
    rng = np.random.default_rng(abs(hash(b["gag"])) % 1000)

    def giggle(base, n=6, gap=0.11, amp=0.13):
        out = np.zeros(int((n * gap + 0.3) * SR))
        for k in range(n):
            f = mtof_(base + (2 if k % 2 == 0 else 0)) * (1 - 0.03 * k)
            tt = np.arange(int(0.09 * SR)) / SR
            s = np.sin(2 * np.pi * f * tt + 3 * np.sin(2 * np.pi * 28 * tt)) * np.exp(-tt * 28) * amp
            i = int(k * gap * SR); out[i:i + len(s)] += s
        return out

    def sweep(f0, f1, dur, amp=0.12):
        tt = np.arange(int(dur * SR)) / SR
        ph = 2 * np.pi * np.cumsum(f0 + (f1 - f0) * tt / dur) / SR
        return np.sin(ph) * amp * np.minimum(1, tt / 0.01) * np.minimum(1, (dur - tt) / 0.05)

    def noise(dur, amp=0.15, decay=8):
        n = rng.standard_normal(int(dur * SR)); tt = np.arange(len(n)) / SR
        return n * np.exp(-tt * decay) * amp

    def thud():
        tt = np.arange(int(0.25 * SR)) / SR
        ph = 2 * np.pi * np.cumsum(150 * np.exp(-tt * 9) + 50) / SR
        return np.sin(ph) * np.exp(-tt * 12) * 0.5

    g = b["gag"]
    if g == "bonk":
        add(sweep(1800, 500, 1.1, 0.07), t0 + 1.2)
        add(thud(), t0 + 2.3); add(boing_(), t0 + 2.32, 1.4)
        for k in range(4): add(bell_(mtof_(96 + k * 2), 0.05, 0.4), t0 + 2.5 + k * 0.35)
        add(giggle(84), t0 + 3.0); add(giggle(62, 7, 0.13, 0.16), t0 + 4.6)
    elif g == "sneeze":
        add(sweep(500, 800, 0.5, 0.08), t0 + 0.6); add(sweep(550, 1000, 0.6, 0.09), t0 + 1.6)
        add(noise(0.5, 0.25, 6), t0 + 2.9); add(tone_(mtof_(70), 0.3, 8, 0.15), t0 + 2.9)
        add(sweep(300, 1400, 1.4, 0.05), t0 + 3.0)
        add(pop_(mtof_(60), 0.3), t0 + 4.6)
        add(giggle(62, 7, 0.13, 0.16), t0 + 5.1); add(giggle(84), t0 + 5.4)
    elif g == "peekaboo":
        for k in range(6): add(tone_(mtof_([67, 71, 67, 74, 67, 71][k]), 0.2, 14, 0.08), t0 + 0.4 + k * 0.5)
        add(pop_(mtof_(79), 0.35), t0 + 3.6); add(bell_(mtof_(88)), t0 + 3.65)
        add(giggle(84), t0 + 4.5); add(giggle(62, 6, 0.13, 0.15), t0 + 4.9)
    elif g == "hiccup":
        for h in [0.9, 2.0, 3.0, 3.8]:
            add(sweep(400, 1100, 0.12, 0.18), t0 + h)
        add(noise(0.35, 0.22, 7), t0 + 5.0); add(tone_(mtof_(50), 0.4, 6, 0.2), t0 + 5.0)
        add(boing_(), t0 + 5.1, 1.3)
        add(giggle(62, 7, 0.13, 0.16), t0 + 6.2); add(giggle(84), t0 + 6.5)
    elif g == "bubble":
        add(sweep(300, 900, 2.5, 0.05), t0 + 0.5)
        for k in range(4): add(tone_(mtof_(79 + k * 3), 0.25, 10, 0.05), t0 + 3.0 + k * 0.4)
        add(pop_(mtof_(84), 0.45), t0 + 4.8); add(noise(0.08, 0.2, 40), t0 + 4.8)
        add(giggle(84), t0 + 5.6); add(giggle(62, 6, 0.13, 0.15), t0 + 5.9)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("episode"); ap.add_argument("--out", default=None)
    ap.add_argument("--stills", action="store_true"); ap.add_argument("--short", type=int, default=0)
    a = ap.parse_args()
    ep = load_episode(a.episode)
    slug = os.path.splitext(os.path.basename(a.episode))[0]
    outdir = a.out or os.path.join(os.path.dirname(HERE), "videos")
    os.makedirs(outdir, exist_ok=True)
    if a.short:
        beats = ep.SHORTS[a.short - 1]
        if a.stills:
            build(a.episode, os.path.join(outdir, f"{slug}_short{a.short}_sheet.png"), beats, vertical=True, intro=False, stills=True)
        else:
            tot = build(a.episode, os.path.join(outdir, f"{slug}_short{a.short}.mp4"), beats, vertical=True, intro=False)
            print("short", a.short, round(tot, 1), "s")
    elif a.stills:
        build(a.episode, os.path.join(outdir, f"{slug}_sheet.png"), stills=True)
    else:
        tot = build(a.episode, os.path.join(outdir, f"{slug}.mp4"))
        thumbnail(ep, os.path.join(outdir, f"{slug}_thumbnail.png"))
        print("episode", round(tot, 1), "s")
