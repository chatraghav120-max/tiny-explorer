"""Ladoo Comes Home: a Tiny Explorer story series about a rescue puppy and the family who adopted him.

Reuses Tiny Explorer's world (scenes, clouds, fonts, bubbles, intro sting) from episode_engine.py.

    python3 generator/ladoo_engine.py series/ladoo/l001_adoption_day.py              # 16:9 episode + thumbnail
    python3 generator/ladoo_engine.py series/ladoo/l001_adoption_day.py --stills     # contact sheet (fast check)
    python3 generator/ladoo_engine.py series/ladoo/l001_adoption_day.py --ends       # end-of-beat stills (typed text)
    python3 generator/ladoo_engine.py series/ladoo/l001_adoption_day.py --short 1    # vertical Short from SHORTS[0]
    python3 generator/ladoo_engine.py --sheet                                        # character sheet

Beats: title, narrate, say (think=True for a thought cloud), ask, moment, lesson, grownup, bye.
Every beat takes: cast (left-to-right list), mood {name: mood}, act {name: action}, scene, dur.
Ladoo actions: wag, hop, lick, sleep, sad, sniff, run.   People actions: wave, pat, hug.
"""
import math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
from multiprocessing import Pool
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import episode_engine as ee
from episode_engine import W, H, U, VERT, text, wrap, big_word, ease_in_out, confetti, countdown, badge_layer
from make_video import ell, poly, line, font, INK, P, S, ease_out_back, clamp01, tone, mtof, star_pts, NUM_COLORS

FPS = 30
SR = 44100
BEAT = 0.5
TYPE_RATE = 20.0

# ----------------------------------------------------------------- cast
COAT, COAT_DK, CREAM = "#e9a345", "#b8732a", "#fff1d6"
PEOPLE = {
    "papa":  dict(R=96, skin="#c68642", hair="#2d2340", style="short", top="#4a7bd0", bottom="#3d3a5c", body=1.0, label="Papa"),
    "mumma": dict(R=92, skin="#d9a066", hair="#2d2340", style="bun", top="#e05a8a", bottom="#e05a8a", body=1.0, dress=True, label="Mumma"),
    "anya":  dict(R=80, skin="#c98d5a", hair="#3a2a1e", style="pigtails", top="#ffca3a", bottom="#ffca3a", body=0.8, dress=True, label="Anya"),
    "kabir": dict(R=72, skin="#c68642", hair="#2d2340", style="spiky", top="#57cc04", bottom="#2ec4b6", body=0.62, label="Kabir"),
    "dadi":  dict(R=88, skin="#c98d5a", hair="#d8d4e0", style="grannybun", top="#8b5cf6", bottom="#8b5cf6", body=0.92, dress=True, glasses=True, label="Dadi"),
    "meera": dict(R=90, skin="#b97a4a", hair="#2d2340", style="ponytail", top="#2ec4b6", bottom="#3d3a5c", body=0.98, label="Meera Didi"),
}
GROUND = 0.93
PSCALE = 1.3


def rot_ell(d, cx, cy, rx, ry, ang, fill, ow=4):
    pts = [(cx + rx * math.cos(a) * math.cos(ang) - ry * math.sin(a) * math.sin(ang),
            cy + rx * math.cos(a) * math.sin(ang) + ry * math.sin(a) * math.cos(ang)) for a in np.linspace(0, 2 * math.pi, 36)]
    poly(d, pts, fill, ow=ow)


def heart(d, x, y, s, fill="#ff5d8f"):
    pts = []
    for a in np.linspace(0, 2 * math.pi, 40):
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((x + hx * s / 17, y + hy * s / 17))
    poly(d, pts, fill, ow=4)


def ladoo(d, x, gy, s, t, mood="happy", act=None, look=0.0, collar=True, talk=False):
    """Ladoo the indie puppy, sitting, front view. gy = ground line, s = head radius."""
    act = act or ""
    lift = 0.0
    if act in ("hop", "run") or mood == "excited":
        lift = abs(math.sin(t * math.pi / BEAT)) * s * (0.45 if act == "hop" else 0.25)
    sleep = act == "sleep"
    sad = mood == "sad" or act == "sad"
    y = gy - lift
    ell(d, x, gy + 2, s * (0.95 - 0.3 * min(lift / s, 1)), s * 0.14, (60, 90, 50), ow=0)
    # tail (behind)
    speed = 0 if sleep else (16 if act in ("wag", "hop", "lick", "run") or mood == "excited" else (2 if sad else 6))
    amp = 0.0 if sleep else (0.55 if speed >= 16 else 0.18)
    ang = -0.2 + amp * math.sin(t * speed) + (0.9 if sad else 0)
    base = (x + 0.5 * s, y - 0.3 * s)
    pts = []
    for k in range(10):
        u = k / 9
        a = ang * u
        px_, py_ = 0.75 * s * u, -0.95 * s * u + 0.35 * s * u * u
        pts.append((base[0] + px_ * math.cos(a) - py_ * math.sin(a), base[1] + px_ * math.sin(a) + py_ * math.cos(a)))
    line(d, pts, fill=INK, w=0.3 * s)
    line(d, pts, fill=COAT, w=0.19 * s)
    ell(d, pts[-1][0], pts[-1][1], 0.1 * s, 0.1 * s, CREAM, ow=3)
    # haunches + body
    for sx in (-1, 1):
        ell(d, x + sx * 0.52 * s, y - 0.32 * s, 0.34 * s, 0.3 * s, COAT)
        ell(d, x + sx * 0.66 * s, y - 0.06 * s, 0.22 * s, 0.11 * s, CREAM)
    ell(d, x, y - 0.82 * s, 0.66 * s, 0.88 * s, COAT)
    ell(d, x, y - 0.62 * s, 0.38 * s, 0.5 * s, CREAM, ow=0)
    for sx in (-1, 1):
        d.rounded_rectangle([P(x + sx * 0.25 * s - 0.12 * s), P(y - 0.62 * s), P(x + sx * 0.25 * s + 0.12 * s), P(y - 0.08 * s)],
                            radius=int(P(0.11 * s)), fill=COAT, outline=INK, width=int(P(4)))
        ell(d, x + sx * 0.25 * s, y - 0.07 * s, 0.18 * s, 0.11 * s, CREAM)
    # head
    hy = y - 2.0 * s + (0.35 * s if sleep else 0) + (0.12 * s if sad else 0)
    tilt = 0.0 if sleep else 0.12 * math.sin(t * 1.3)
    ear_flop = (0.5 if sad else 0.2) + 0.08 * math.sin(t * (10 if speed >= 16 else 2))
    for sx in (-1, 1):
        rot_ell(d, x + sx * 0.86 * s, hy + 0.12 * s, 0.26 * s, 0.52 * s, sx * ear_flop, COAT_DK)
    ell(d, x, hy, s, s * 0.92, COAT)
    ell(d, x, hy - 0.15 * s, 0.13 * s, 0.42 * s, CREAM, ow=0)          # blaze
    ell(d, x, hy + 0.42 * s, 0.5 * s, 0.36 * s, CREAM, ow=3)            # muzzle
    if sleep:
        for sx in (-1, 1):
            d.arc([P(x + sx * 0.36 * s - 0.15 * s), P(hy - 0.22 * s), P(x + sx * 0.36 * s + 0.15 * s), P(hy - 0.02 * s)], 20, 160, fill=INK, width=int(P(5)))
    else:
        ee.eyes(d, x + tilt * s * 0.2, hy + 0.05 * s, s * 1.05, "excited" if mood == "love" else mood, t, look, blink_seed=0.7)
    ell(d, x, hy + 0.27 * s, 0.16 * s, 0.11 * s, INK, ow=0)             # nose
    ell(d, x - 0.05 * s, hy + 0.24 * s, 0.05 * s, 0.03 * s, "#ffffff", ow=0)
    happy_open = (mood in ("happy", "excited", "love") or act in ("wag", "hop", "lick")) and not sleep and not sad
    if talk:
        happy_open = True
    if happy_open:
        op = 0.12 * s + (0.06 * s * (0.5 + 0.5 * math.sin(t * 20)) if talk else 0)
        d.chord([P(x - 0.22 * s), P(hy + 0.32 * s), P(x + 0.22 * s), P(hy + 0.42 * s + op * 2)], 0, 180, fill="#b5223b", outline=INK, width=int(P(4)))
        tl = 0.22 * s if act == "lick" else 0.1 * s
        ell(d, x + 0.04 * s, hy + 0.5 * s + op * 0.6 + tl * 0.5, 0.11 * s, 0.07 * s + tl, "#ff8fab", ow=3)
    else:
        d.arc([P(x - 0.2 * s), P(hy + 0.26 * s), P(x), P(hy + 0.46 * s)], 20, 160, fill=INK, width=int(P(4)))
        d.arc([P(x), P(hy + 0.26 * s), P(x + 0.2 * s), P(hy + 0.46 * s)], 20, 160, fill=INK, width=int(P(4)))
    ell(d, x - 0.62 * s, hy + 0.3 * s, 0.13 * s, 0.07 * s, "#ff8fab", ow=0)
    ell(d, x + 0.62 * s, hy + 0.3 * s, 0.13 * s, 0.07 * s, "#ff8fab", ow=0)
    if collar:
        d.arc([P(x - 0.62 * s), P(hy + 0.45 * s), P(x + 0.62 * s), P(hy + 1.05 * s)], 30, 150, fill="#e63946", width=int(P(0.13 * s)))
        ell(d, x, hy + 1.06 * s, 0.11 * s, 0.11 * s, "#ffd60a", ow=3)
    if sleep:
        for k in range(3):
            ph = (t * 0.6 + k / 3) % 1
            text(d, x + 0.9 * s + ph * 0.5 * s, hy - 0.9 * s - ph * 0.9 * s, "z", (30 + 22 * ph) * U(), "white", stroke=5)
    return (x, hy - s)        # top of head


def _hair_back(d, x, hy, R, c, style):
    if style == "bun":
        ell(d, x, hy - 1.02 * R, 0.42 * R, 0.36 * R, c)
    elif style == "grannybun":
        ell(d, x, hy - 1.0 * R, 0.4 * R, 0.33 * R, c)
    elif style == "pigtails":
        for sx in (-1, 1):
            ell(d, x + sx * 1.12 * R, hy + 0.1 * R, 0.3 * R, 0.42 * R, c)
            ell(d, x + sx * 0.98 * R, hy - 0.25 * R, 0.14 * R, 0.14 * R, "#ff595e")
    elif style == "ponytail":
        rot_ell(d, x + 0.95 * R, hy + 0.15 * R, 0.24 * R, 0.6 * R, -0.35, c)
    if style in ("bun",):
        rot_ell(d, x - 0.9 * R, hy + 0.35 * R, 0.2 * R, 0.55 * R, 0.1, c)
        rot_ell(d, x + 0.9 * R, hy + 0.35 * R, 0.2 * R, 0.55 * R, -0.1, c)


def _hair_front(d, x, hy, R, c, style):
    d.chord([P(x - 1.04 * R), P(hy - 1.06 * R), P(x + 1.04 * R), P(hy + 0.45 * R)], 180, 360, fill=c, outline=INK, width=int(P(4)))
    if style == "spiky":
        for k in range(5):
            bx = x - 0.7 * R + k * 0.35 * R
            poly(d, [(bx - 0.18 * R, hy - 0.75 * R), (bx + 0.05 * R, hy - 1.28 * R), (bx + 0.2 * R, hy - 0.75 * R)], c)
        d.chord([P(x - 1.04 * R), P(hy - 1.06 * R), P(x + 1.04 * R), P(hy + 0.45 * R)], 180, 360, fill=c, outline=None)
    if style == "pigtails":
        for k in range(4):
            bx = x - 0.5 * R + k * 0.33 * R
            ell(d, bx, hy - 0.42 * R, 0.2 * R, 0.14 * R, c, ow=0)


def person(d, name, x, gy, t, mood="happy", act=None, talk=False, look=0.0, scale=1.0):
    p = PEOPLE[name]
    R = p["R"] * U() * scale * (1.55 if VERT() else PSCALE)
    act = act or ""
    bob = abs(math.sin(t * math.pi / BEAT)) * (10 if mood == "excited" else 3) * U()
    y = gy - bob
    bh = p["body"]
    hip = y - 1.25 * R * bh
    sh = y - 2.75 * R * bh
    hy = sh - 0.92 * R
    ell(d, x, gy + 2, R * 0.85, R * 0.12, (60, 90, 50), ow=0)
    # legs
    for sx in (-1, 1):
        lc = p["skin"] if p.get("dress") else p["bottom"]
        d.rounded_rectangle([P(x + sx * 0.3 * R - 0.17 * R), P(hip - 0.1 * R), P(x + sx * 0.3 * R + 0.17 * R), P(y - 0.08 * R)],
                            radius=int(P(0.12 * R)), fill=lc, outline=INK, width=int(P(4)))
        ell(d, x + sx * 0.34 * R, y - 0.06 * R, 0.26 * R, 0.13 * R, "#3d3a5c")
    # torso
    if p.get("dress"):
        poly(d, [(x - 0.62 * R, sh + 0.1 * R), (x + 0.62 * R, sh + 0.1 * R), (x + 0.95 * R, hip + 0.25 * R), (x - 0.95 * R, hip + 0.25 * R)], p["top"])
        d.rounded_rectangle([P(x - 0.66 * R), P(sh), P(x + 0.66 * R), P(sh + 0.7 * R)], radius=int(P(0.3 * R)), fill=p["top"], outline=INK, width=int(P(4)))
        d.rectangle([P(x - 0.6 * R), P(sh + 0.5 * R), P(x + 0.6 * R), P(sh + 0.9 * R)], fill=p["top"])
    else:
        d.rounded_rectangle([P(x - 0.72 * R), P(sh), P(x + 0.72 * R), P(hip + 0.1 * R)], radius=int(P(0.32 * R)), fill=p["top"], outline=INK, width=int(P(4)))
    # arms
    for sx in (-1, 1):
        wave = act == "wave" and sx == 1
        reach = act in ("pat", "hug") and (sx == -1 if act == "pat" else True)
        if wave:
            a = -1.0 + 0.45 * math.sin(t * 9)
            ax, ay = x + 0.8 * R, sh + 0.25 * R
            hx, hy2 = ax + math.cos(a) * 0.95 * R, ay + math.sin(a) * 0.95 * R
        elif reach:
            ax, ay = x + sx * 0.75 * R, sh + 0.3 * R
            hx, hy2 = ax + sx * 0.75 * R, ay + 0.75 * R + (0.08 * R * math.sin(t * 6) if act == "pat" else 0)
        else:
            ax, ay = x + sx * 0.78 * R, sh + 0.3 * R
            hx, hy2 = ax + sx * 0.18 * R, ay + 0.95 * R
        line(d, [(ax, ay), (hx, hy2)], fill=INK, w=0.36 * R)
        line(d, [(ax, ay), (hx, hy2)], fill=p["top"], w=0.26 * R)
        ell(d, hx, hy2, 0.16 * R, 0.16 * R, p["skin"])
    # head
    ell(d, x, sh + 0.02 * R, 0.2 * R, 0.14 * R, p["skin"], ow=0)
    _hair_back(d, x, hy, R, p["hair"], p["style"])
    ell(d, x - 0.98 * R, hy + 0.1 * R, 0.16 * R, 0.2 * R, p["skin"])
    ell(d, x + 0.98 * R, hy + 0.1 * R, 0.16 * R, 0.2 * R, p["skin"])
    ell(d, x, hy, R, R * 0.98, p["skin"])
    _hair_front(d, x, hy, R, p["hair"], p["style"])
    ee.eyes(d, x, hy + 0.2 * R, R * 0.82, mood, t, look, blink_seed=hash(name) % 7 * 0.4)
    ee.mouth(d, x, hy + 0.36 * R, R * 0.62, mood, talk, t)
    ell(d, x - 0.55 * R, hy + 0.42 * R, 0.12 * R, 0.07 * R, "#ff8fab", ow=0)
    ell(d, x + 0.55 * R, hy + 0.42 * R, 0.12 * R, 0.07 * R, "#ff8fab", ow=0)
    if name == "mumma":
        ell(d, x, hy - 0.08 * R, 0.05 * R, 0.05 * R, "#e63946", ow=0)
    if name == "papa":
        d.chord([P(x - 0.25 * R), P(hy + 0.22 * R), P(x + 0.25 * R), P(hy + 0.42 * R)], 180, 360, fill=p["hair"])
    if p.get("glasses"):
        for sx in (-1, 1):
            d.ellipse([P(x + sx * 0.28 * R - 0.24 * R), P(hy - 0.03 * R), P(x + sx * 0.28 * R + 0.24 * R), P(hy + 0.42 * R)], outline=INK, width=int(P(4)))
        line(d, [(x - 0.04 * R, hy + 0.18 * R), (x + 0.04 * R, hy + 0.18 * R)], w=4)
    return (x, hy - R * (1.3 if p["style"] == "spiky" else 1.1))


def character(d, name, x, gy, t, mood="happy", act=None, talk=False, look=0.0, n=3):
    if name == "ladoo":
        return ladoo(d, x, gy, (150 if n == 1 else (128 if n == 2 else 100)) * U() * (1.3 if VERT() else 1.0), t, mood=mood, act=act, look=look, collar=EP.get("collar", True), talk=talk)
    return person(d, name, x, gy, t, mood=mood, act=act, talk=talk, look=look)


# ----------------------------------------------------------------- scenes
_BG = {}


def scene_bg(name):
    key = (name, W(), H())
    if key in _BG:
        return _BG[key]
    w, h = W(), H()
    if name == "shelter":
        img = ee._grad((205, 238, 232), (170, 222, 214)); d = ImageDraw.Draw(img)
        d.rectangle([0, P(h * 0.74), P(w), P(h)], fill="#d9c7a5", outline=INK, width=int(P(4)))
        for k in range(10):
            line(d, [(w * k / 9, h * 0.74), (w * k / 9 - w * 0.05, h)], fill="#c7b38f", w=3)
        sx, sy = (w * 0.5, h * 0.42) if VERT() else (w * 0.17, h * 0.4)
        d.rounded_rectangle([P(sx - 210 * U()), P(sy - 44 * U()), P(sx + 210 * U()), P(sy + 44 * U())], radius=int(P(24)), fill="#fff7e8", outline=INK, width=int(P(5)))
        text(d, sx, sy + 3, "Happy Paws Shelter", 40 * U(), "#e9a345", stroke=5)
        rnd = random.Random(5)
        for _ in range(14):
            px_, py_ = rnd.uniform(0.04, 0.96) * w, rnd.uniform(0.3, 0.55) * h
            if abs(px_ - sx) < 240 * U() and abs(py_ - sy) < 70 * U(): continue
            r = 14 * U()
            ell(d, px_, py_, r, r * 0.85, "#9fd3c7", ow=0)
            for k in range(4):
                ell(d, px_ + (k - 1.5) * r * 0.75, py_ - r * 1.15 - (0.25 * r if k in (1, 2) else 0), r * 0.33, r * 0.38, "#9fd3c7", ow=0)
        fy = h * 0.6
        d.rectangle([0, P(fy), P(w), P(fy + 14 * U())], fill="#c98d5a", outline=INK, width=int(P(4)))
        d.rectangle([0, P(fy + 70 * U()), P(w), P(fy + 84 * U())], fill="#c98d5a", outline=INK, width=int(P(4)))
        for k in range(13):
            x = w * (k + 0.5) / 13
            d.rounded_rectangle([P(x - 12 * U()), P(fy - 20 * U()), P(x + 12 * U()), P(h * 0.76)], radius=int(P(8)), fill="#dba06b", outline=INK, width=int(P(4)))
    elif name in ("home", "home_night"):
        night = name == "home_night"
        img = ee._grad((255, 236, 205), (255, 214, 170)) if not night else ee._grad((70, 70, 130), (110, 95, 160))
        d = ImageDraw.Draw(img)
        d.rectangle([0, P(h * 0.72), P(w), P(h)], fill="#e8a86c" if not night else "#8a6a8a", outline=INK, width=int(P(4)))
        for i in range(9):
            line(d, [(w * i / 8, h * 0.72), (w * i / 8 - w * 0.06, h)], fill="#d18f55" if not night else "#7a5a7a", w=3)
        wx, wy, ww, wh = (w * 0.8, h * 0.3, w * 0.16, h * 0.24) if not VERT() else (w * 0.6, h * 0.36, w * 0.32, h * 0.14)
        d.rounded_rectangle([P(wx), P(wy), P(wx + ww), P(wy + wh)], radius=int(P(18)), fill="#9fdcff" if not night else "#2b2f6b", outline=INK, width=int(P(5)))
        if night:
            ell(d, wx + ww * 0.7, wy + wh * 0.3, 34 * U(), 34 * U(), "#fff1a8", ow=3)
            for k in range(5):
                ell(d, wx + ww * (0.15 + 0.15 * k), wy + wh * (0.6 + 0.07 * (k % 2)), 4 * U(), 4 * U(), "#fff6c4", ow=0)
        line(d, [(wx + ww / 2, wy), (wx + ww / 2, wy + wh)], w=5)
        line(d, [(wx, wy + wh / 2), (wx + ww, wy + wh / 2)], w=5)
        fx, fy = (w * 0.04, h * 0.36) if not VERT() else (w * 0.06, h * 0.4)
        d.rounded_rectangle([P(fx), P(fy), P(fx + 170 * U()), P(fy + 130 * U())], radius=int(P(10)), fill="#fff7e8", outline=INK, width=int(P(5)))
        heart(d, fx + 85 * U(), fy + 68 * U(), 40 * U(), "#ff8fab")
        ell(d, w * 0.5, h * 0.9, w * 0.34, h * 0.06, "#8b5cf6" if not night else "#5b3fa6", ow=4)
        if night:
            lx, ly = w * 0.06, h * 0.5
            ell(d, lx, ly, 130 * U(), 130 * U(), (255, 230, 160), ow=0)
    elif name == "park":
        img = ee._grad((110, 200, 255), (220, 245, 255)); d = ImageDraw.Draw(img)
        ee._hills(d)
        ee._tree(d, w * 0.08, h * 0.6, 150 * U())
        bx, by = w * 0.86, h * 0.7
        d.rounded_rectangle([P(bx - 130 * U()), P(by - 30 * U()), P(bx + 130 * U()), P(by)], radius=int(P(8)), fill="#c98d5a", outline=INK, width=int(P(4)))
        for sx in (-1, 1):
            d.rectangle([P(bx + sx * 100 * U() - 8 * U()), P(by), P(bx + sx * 100 * U() + 8 * U()), P(by + 50 * U())], fill="#8a5a2b", outline=INK, width=int(P(3)))
    else:
        img = ee.scene_bg(name).copy()
    _BG[key] = img
    return img


def outdoor(name):
    return name in ("park", "meadow", "orchard", "beach")


# ----------------------------------------------------------------- layout + ui
def cast_x(cast, b):
    pos = b.get("pos", {})
    n = len(cast)
    lo, hi = (0.27, 0.73) if VERT() else (0.12, 0.88)
    out = {}
    for i, c in enumerate(cast):
        out[c] = W() * pos.get(c, lo + (hi - lo) * (i / (n - 1) if n > 1 else 0.5))
    return out


def ground():
    return H() * (0.82 if VERT() else GROUND)


def draw_cast(d, b, t, speaker=None, lt=0.0):
    cast = b.get("cast", [])
    xs = cast_x(cast, b)
    moods, acts = b.get("mood", {}), b.get("act", {})
    tops = {}
    talking = speaker if lt < len(b.get("text", "")) / TYPE_RATE + 0.2 else None
    for c in cast:
        look = 0.0
        if speaker and c != speaker and speaker in xs:
            look = 0.6 if xs[speaker] > xs[c] else -0.6
        tops[c] = character(d, c, xs[c], ground(), t, mood=moods.get(c, "happy"), act=acts.get(c), talk=(c == talking and not b.get("think")), look=look, n=len(cast))
    return xs, tops


def think_bubble(d, x, y, s, px, shown, tail):
    maxw = W() * (0.8 if VERT() else 0.48)
    lines = wrap(s, px, maxw)
    f = font(int(px))
    bw = max(f.getlength(l) / S for l in lines) + 80 * U()
    bh = len(lines) * px * 1.25 + 56 * U()
    x0 = min(max(x - bw / 2, 24 * U()), W() - bw - 24 * U())
    y0 = y - bh
    tx, ty = tail
    for k, r in enumerate((20, 13, 8)):
        u = (k + 1) / 4
        ell(d, x0 + bw / 2 + (tx - x0 - bw / 2) * u, y + (ty - y) * u, r * U(), r * U(), "#f3ecff", ow=4)
    for k in range(int(bw / (70 * U())) + 1):
        cx = x0 + 35 * U() + k * (bw - 70 * U()) / max(1, int(bw / (70 * U())))
        ell(d, cx, y0 + 8 * U(), 40 * U(), 34 * U(), "#f3ecff", ow=4)
        ell(d, cx, y - 6 * U(), 40 * U(), 30 * U(), "#f3ecff", ow=4)
    d.rounded_rectangle([P(x0), P(y0), P(x0 + bw), P(y)], radius=int(P(40 * U())), fill="#f3ecff", outline=INK, width=int(P(4)))
    for k in range(int(bw / (70 * U())) + 1):
        cx = x0 + 35 * U() + k * (bw - 70 * U()) / max(1, int(bw / (70 * U())))
        ell(d, cx, y0 + 10 * U(), 36 * U(), 30 * U(), "#f3ecff", ow=0)
        ell(d, cx, y - 8 * U(), 36 * U(), 26 * U(), "#f3ecff", ow=0)
    left = shown
    for i, l in enumerate(lines):
        vis = l[:max(0, left)]; left -= len(l) + 1
        if vis:
            d.text((P(x0 + 40 * U()), P(y0 + 28 * U() + i * px * 1.25)), vis, font=f, fill=INK)


def caption_box(d, s, lt, y=None):
    px = 56 * U()
    lines = wrap(s, px, W() * (0.84 if VERT() else 0.62))
    f = font(int(px))
    bw = max(f.getlength(l) / S for l in lines) + 80 * U()
    bh = len(lines) * px * 1.3 + 44 * U()
    a = ease_out_back(lt / 0.4)
    if a <= 0.02: return 0
    y0 = y if y is not None else H() * (0.07 if not VERT() else 0.1)
    x0 = W() / 2 - bw / 2
    d.rounded_rectangle([P(x0), P(y0 - (1 - a) * 40), P(x0 + bw), P(y0 + bh - (1 - a) * 40)], radius=int(P(26)), fill="#fff7e8", outline=INK, width=int(P(5)))
    for i, l in enumerate(lines):
        text(d, W() / 2, y0 + 22 * U() + px * 0.62 + i * px * 1.3 - (1 - a) * 40, l, px, "#7a4b2a", stroke=0)
    return y0 + bh


def floating_hearts(d, x, y, lt, n=7, spread=1.0, seed=3):
    rnd = random.Random(seed)
    for k in range(n):
        d0 = rnd.uniform(0, 1.2); sp = rnd.uniform(70, 120)
        ph = lt - d0
        if ph < 0: continue
        ph %= 2.2
        hx = x + rnd.uniform(-160, 160) * U() * spread + math.sin(ph * 3 + k) * 18 * U()
        hy = y - ph * sp * U()
        s = rnd.uniform(18, 30) * U() * min(1, ph * 3) * (1 - max(0, ph - 1.7) * 2)
        if s > 2:
            heart(d, hx, hy, s, ["#ff5d8f", "#ff8fab", "#e63946"][k % 3])


# ----------------------------------------------------------------- beats
def beat_len(b):
    k = b["type"]
    if "dur" in b: return b["dur"]
    if k in ("say", "grownup"):
        return max(3.0, len(b["text"]) / TYPE_RATE + 1.8)
    if k == "narrate":
        return max(3.6, len(b["text"]) / TYPE_RATE + 2.0)
    if k == "ask": return 8.2
    if k == "title": return 5.0
    if k == "moment": return 5.5
    if k == "lesson": return 6.5
    if k == "bye": return 6.0
    return 3.0


def r_title(d, b, lt, t):
    w, h = W(), H()
    a = ease_out_back((lt - 0.2) / 0.5)
    ty = h * (0.2 if VERT() else 0.18)
    series = EP.get("series", "Ladoo Comes Home")
    if a > 0.02:
        text(d, w / 2, ty + (1 - a) * 80, series, (110 if VERT() else 120) * U() * max(a, 0.3), COAT, stroke=14 * U())
    big_word(d, w / 2, ty + 135 * U(), b.get("text", ""), 62 * U(), "white", 0.8, lt, stroke=10)
    ladoo(d, w / 2, ground(), 110 * U(), t, mood="excited", act="hop", collar=EP.get("collar", True))
    floating_hearts(d, w / 2, ground() - 300 * U(), lt, n=8, spread=1.6)


def r_say(d, b, lt, t):
    who = b["who"]
    xs, tops = draw_cast(d, b, t, speaker=who, lt=lt)
    shown = int(lt * TYPE_RATE)
    top_all = min(v[1] for v in tops.values()) if tops else H() * 0.6
    sx, sy = tops.get(who, (W() / 2, top_all))
    px = 54 * U()
    yb = top_all - 34 * U()
    if b.get("think"):
        think_bubble(d, sx, yb, b["text"], px, shown, (sx, sy - 8 * U()))
    else:
        ee.bubble(d, sx, yb, b["text"], px, shown, (sx, sy - 6 * U()), maxw=W() * (0.8 if VERT() else 0.5))
    if b.get("hearts"):
        floating_hearts(d, xs.get(b["hearts"], W() / 2), ground() - 160 * U(), lt)


def r_narrate(d, b, lt, t):
    draw_cast(d, b, t)
    caption_box(d, b["text"], lt)


def r_ask(d, b, lt, t):
    w, h = W(), H()
    draw_cast(d, dict(b, mood=b.get("mood", {})), t)
    ty = h * (0.135 if not VERT() else 0.14)
    lines = wrap(b["q"], 70 * U(), w * (0.86 if VERT() else 0.72))
    for i, l in enumerate(lines):
        big_word(d, w / 2, ty + i * 82 * U(), l, 70 * U(), "white", 0.0, lt, stroke=10)
    cy = ty + len(lines) * 82 * U() + 90 * U()
    t_your, t_reveal = 2.2, 5.2
    if t_your <= lt < t_reveal:
        frac = (lt - t_your) / 3.0
        countdown(d, w / 2 + 240 * U(), cy, 3 - int(frac * 3), frac, 54 * U())
        big_word(d, w / 2 - 60 * U(), cy, "Your turn!", 76 * U(), "#ffca3a", t_your, lt)
    if lt >= t_reveal:
        a = ease_out_back((lt - t_reveal) / 0.35)
        bw = max(280 * U(), font(int(76 * U())).getlength(b["a"]) / S / 2 + 70 * U())
        d.rounded_rectangle([P(w / 2 - bw * a), P(cy - 60 * U()), P(w / 2 + bw * a), P(cy + 60 * U())], radius=int(P(60 * U())), fill="#8ac926", outline=INK, width=int(P(6)))
        text(d, w / 2, cy + 3, b["a"], 72 * U() * max(a, 0.3), "white", stroke=8 * U())
        big_word(d, w / 2, cy + 105 * U(), "Yay, you did it!", 52 * U(), "#ffca3a", t_reveal + 0.3, lt)


def r_moment(d, b, lt, t):
    xs, tops = draw_cast(d, b, t)
    tgt = b.get("hearts", "ladoo")
    floating_hearts(d, xs.get(tgt, W() / 2), ground() - 140 * U(), lt, n=12, spread=1.4)
    if b.get("text"):
        px = (80 if VERT() else 84) * U()
        for i, l in enumerate(wrap(b["text"], px, W() * 0.86)):
            big_word(d, W() / 2, H() * (0.13 if not VERT() else 0.16) + i * px * 1.15, l, px, "#ff5d8f", 0.3, lt, stroke=12)


def r_lesson(d, b, lt, t):
    xs, tops = draw_cast(d, b, t)
    w, h = W(), H()
    a = ease_out_back((lt - 0.4) / 0.5)
    if a > 0.02:
        lines = wrap(b["text"], 74 * U(), w * (0.84 if VERT() else 0.7))
        f = font(int(74 * U()))
        bw = max(f.getlength(l) / S for l in lines) + 120 * U()
        bh = len(lines) * 90 * U() + 60 * U()
        y0 = h * (0.08 if not VERT() else 0.12)
        d.rounded_rectangle([P(w / 2 - bw / 2 * a), P(y0), P(w / 2 + bw / 2 * a), P(y0 + bh)], radius=int(P(40)), fill="#ff8fab", outline=INK, width=int(P(6)))
        for i, l in enumerate(lines):
            text(d, w / 2, y0 + 30 * U() + 45 * U() + i * 90 * U(), l, 74 * U() * max(a, 0.3), "white", stroke=8 * U())
        heart(d, w / 2 - bw / 2 * a - 10 * U(), y0 + 10 * U(), 34 * U())
        heart(d, w / 2 + bw / 2 * a + 10 * U(), y0 + 10 * U(), 34 * U())
    floating_hearts(d, xs.get("ladoo", w / 2), ground() - 140 * U(), lt, n=8)


def r_grownup(d, b, lt, t):
    r_say(d, b, lt, t)
    big_word(d, W() / 2, H() * (0.13 if not VERT() else 0.12), "With your grown-up!", 70 * U(), "#ffca3a", 0.2, lt)


def r_bye(d, b, lt, t):
    b = dict(b, act={**{c: "wave" for c in b.get("cast", []) if c != "ladoo"}, "ladoo": "hop", **b.get("act", {})})
    draw_cast(d, b, t)
    w, h = W(), H()
    px = (88 if VERT() else 104) * U()
    tl_ = wrap("Bye-bye, explorers!", px, w * 0.88)
    y0 = h * (0.13 if not VERT() else 0.16)
    for i, l in enumerate(tl_):
        big_word(d, w / 2, y0 + i * px * 1.1, l, px, COAT, 0.2, lt, stroke=14)
    if b.get("next"):
        nl = wrap(b["next"], 50 * U(), w * 0.86)
        for i, l in enumerate(nl):
            big_word(d, w / 2, y0 + (len(tl_) - 1) * px * 1.1 + (100 + i * 62) * U(), l, 50 * U(), "white", 1.0, lt, stroke=8)
    confetti(d, lt)


RENDER = {"title": r_title, "say": r_say, "narrate": r_narrate, "ask": r_ask, "moment": r_moment,
          "lesson": r_lesson, "grownup": r_grownup, "bye": r_bye}


# ----------------------------------------------------------------- frames
EP = {}


def timeline(beats, intro=True):
    out, t = [], (3.5 if intro else 0.0)
    for b in beats:
        L = beat_len(b); out.append((t, t + L, b)); t += L
    return out, t


def camera_crop(lt, L, b):
    if b["type"] in ("say", "grownup") and b.get("who") in b.get("cast", []):
        z = 1.0 + 0.05 * ease_in_out(lt / max(L, 0.1))
        xs = cast_x(b["cast"], b)
        fx = xs[b["who"]] * 0.3 + W() / 2 * 0.7
        fy = H() * 0.6
    elif b["type"] == "moment":
        z = 1.0 + 0.07 * ease_in_out(lt / max(L, 0.1))
        xs = cast_x(b.get("cast", []), b)
        fx = xs.get(b.get("hearts", "ladoo"), W() / 2) * 0.4 + W() / 2 * 0.6
        fy = H() * 0.65
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
        return brand.frame(t) if not VERT() else ee._vertical_intro(t)
    seg = next((s for s in tl if s[0] <= t < s[1]), tl[-1])
    t0, t1, b = seg
    lt = t - t0
    scene = b.get("scene", EP["scene"])
    EP["collar"] = b.get("collar", EP["collar_default"])
    img = scene_bg(scene).copy()
    d = ImageDraw.Draw(img)
    if outdoor(scene):
        ee.clouds(d, t)
    RENDER[b["type"]](d, b, lt, t)
    out = img.resize((W(), H()), Image.BILINEAR, box=camera_crop(lt, t1 - t0, b), reducing_gap=2.0)
    out.paste(*badge_layer())
    prev = next((s for s in tl if s[1] == t0), None)
    cut = prev is not None and prev[2].get("scene", EP["scene"]) != scene
    fade = 1.0
    if cut and lt < 0.35: fade = min(fade, lt / 0.35)
    if t < (3.6 if intro else 0.3): fade = min(fade, clamp01((t - (3.5 if intro else 0)) / 0.3))
    fade = min(fade, clamp01((total - t) / 0.6))
    if fade < 1:
        out = Image.blend(Image.new("RGB", out.size, "white"), out, fade)
    return out.tobytes()


# ----------------------------------------------------------------- audio
VOICE = {"papa": [52, 55, 57, 59], "mumma": [64, 67, 69, 71], "anya": [72, 74, 76, 79], "kabir": [76, 79, 81, 83],
         "dadi": [62, 64, 65, 67], "meera": [65, 67, 69, 72], "ladoo": [79, 81, 84]}


def make_audio(path, tl, total, intro, seed=5):
    rng = np.random.default_rng(seed)
    buf = np.zeros(int((total + 1) * SR))

    def add(sig, t, g=1.0):
        i = int(t * SR); j = min(len(buf), i + len(sig))
        if i < len(buf) and j > i: buf[i:j] += sig[: j - i] * g

    def blip(f, amp=0.1):
        tt = np.arange(int(0.07 * SR)) / SR
        return (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 30) * amp * np.minimum(1, tt / 0.004)

    def woof(pitch=1.0, amp=0.32):
        tt = np.arange(int(0.2 * SR)) / SR
        f = (420 * np.exp(-tt * 9) + 180) * pitch
        ph = 2 * np.pi * np.cumsum(f) / SR
        sig = np.sign(np.sin(ph)) * 0.35 + np.sin(ph) + 0.25 * rng.standard_normal(len(tt)) * np.exp(-tt * 30)
        return sig * np.exp(-tt * 13) * amp * np.minimum(1, tt / 0.005)

    def whimper():
        tt = np.arange(int(0.5 * SR)) / SR
        f = 900 - 350 * tt / 0.5 + 25 * np.sin(tt * 40)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3) * 0.09 * np.minimum(1, tt / 0.03)

    def bell(f, amp=0.18, dur=1.2):
        tt = np.arange(int(dur * SR)) / SR
        return (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2.76 * f * tt) * np.exp(-tt * 4)) * np.exp(-tt * 3) * amp

    def chime_up(base=72, gap=0.07, amp=0.12):
        out = np.zeros(int(1.0 * SR))
        for k, m in enumerate([0, 4, 7, 12, 16]):
            s = tone(mtof(base + m), 0.6, 5, amp); i = int(k * gap * SR); out[i:i + len(s)] += s[: len(out) - i]
        return out

    # gentle waltz-ish bed: 3/4 at 120 bpm (beat 0.5 s), warm piano-ish tones
    prog = [([48], [60, 64, 67]), ([45], [60, 64, 69]), ([41], [60, 65, 69]), ([43], [59, 62, 67])]
    theme = [(0, 76, 1), (1, 79, 1), (2, 81, 1), (3, 79, 2), (5, 76, 1), (6, 74, 1), (7, 76, 1), (8, 72, 2),
             (12, 76, 1), (13, 79, 1), (14, 84, 1), (15, 83, 2), (17, 81, 1), (18, 79, 1), (19, 76, 1), (20, 79, 3)]

    def level(t):
        seg = next((s for s in tl if s[0] <= t < s[1]), None)
        if seg is None or (intro and t < 3.5): return 0.0
        k = seg[2]["type"]
        if seg[2].get("sad"): return 0.25
        return 0.9 if k in ("title", "moment", "bye", "lesson") else 0.38

    start = 3.5 if intro else 0.0
    for bi in range(int((total - start) / BEAT)):
        t = start + bi * BEAT
        g = level(t)
        if g <= 0: continue
        bar = (bi // 3) % 4
        root, ch = prog[bar]
        if bi % 3 == 0:
            add(tone(mtof(root[0]), 1.2, 3, 0.22, (1, 0.25, 0.05)), t, g)
        else:
            for m in ch:
                add(tone(mtof(m), 0.4, 7, 0.045), t, g)
    for (t0, t1, b) in tl:
        if b["type"] in ("title", "moment", "bye", "lesson"):
            tt0 = t0
            while tt0 < t1 - 0.3:
                for bb, m, du in theme:
                    tt = tt0 + bb * BEAT
                    if tt < t1 - 0.2:
                        add(tone(mtof(m), du * BEAT + 0.3, 4, 0.1, (1, 0.5, 0.2)), tt)
                tt0 += 24 * BEAT
    for (t0, t1, b) in tl:
        k = b["type"]
        if k in ("say", "grownup"):
            who = b["who"]
            if who == "ladoo" and not b.get("think"):
                n = max(1, b["text"].lower().count("woof"))
                for j in range(min(n, 4)):
                    add(woof(1.0 + 0.05 * j), t0 + 0.15 + j * 0.32)
            elif who == "ladoo":
                add(whimper() if "sad" in str(b.get("mood", {}).get("ladoo", "")) else bell(mtof(88), 0.08), t0 + 0.1)
                r = random.Random(hash(b["text"]) & 0xffff); tt = t0 + 0.4
                while tt < t0 + len(b["text"]) / TYPE_RATE:
                    add(blip(mtof(r.choice(VOICE["ladoo"])), 0.05), tt); tt += r.uniform(0.09, 0.13)
            else:
                base = VOICE.get(who, [67, 69, 72])
                r = random.Random(hash(b["text"]) & 0xffff); tt = t0
                while tt < t0 + len(b["text"]) / TYPE_RATE:
                    add(blip(mtof(r.choice(base))), tt); tt += r.uniform(0.075, 0.11)
            if b.get("hearts"):
                add(chime_up(79, 0.06, 0.07), t0 + 0.5)
        elif k == "ask":
            add(bell(mtof(84), 0.15), t0 + 0.1)
            for s_ in range(3):
                add(tone(1400, 0.08, 40, 0.16, (1, 0, 0)), t0 + 2.2 + s_)
            add(bell(mtof(88)), t0 + 5.2); add(chime_up(), t0 + 5.3)
        elif k == "moment":
            add(chime_up(72, 0.09, 0.1), t0 + 0.3)
            if b.get("act", {}).get("ladoo") in ("lick", "wag", "hop"):
                add(woof(1.15, 0.22), t0 + 1.2)
        elif k == "lesson":
            add(chime_up(), t0 + 0.5); add(bell(mtof(84)), t0 + 1.2)
        elif k == "title":
            add(woof(1.1, 0.25), t0 + 0.6); add(woof(1.15, 0.25), t0 + 0.9)
        elif k == "bye":
            for m in [48, 60, 64, 67, 72]:
                add(tone(mtof(m), 2.5, 1.2, 0.09), t1 - 2.6)
        if b.get("sad"):
            out = np.zeros(int(1.4 * SR))
            for j, m in enumerate([67, 65, 64, 60]):
                s = tone(mtof(m), 0.45, 5, 0.08, (1, 0.2, 0.05)); i = int(j * 0.28 * SR); out[i:i + len(s)] += s[: len(out) - i]
            add(out, t0 + 0.2)
    if intro:
        import brand
        brand.jingle(path + ".jingle.wav")
        _, jg = wavfile.read(path + ".jingle.wav")
        add(jg.astype(np.float64) / 32767 * 0.9, 0.0)
        os.remove(path + ".jingle.wav")
    buf = buf[: int(total * SR)]
    buf /= np.max(np.abs(buf)) + 1e-9
    buf = np.tanh(buf * 1.2) / np.tanh(1.2) * 0.89
    fl = int(0.6 * SR); buf[-fl:] *= np.linspace(1, 0, fl)
    wavfile.write(path, SR, (buf * 32767).astype(np.int16))


# ----------------------------------------------------------------- thumbnail, sheet, build
def thumbnail(ep, path):
    ee.CFG.update(W=1920, H=1080)
    th = getattr(ep, "THUMB", {})
    img = scene_bg(th.get("scene", getattr(ep, "SCENE", "home"))).copy(); d = ImageDraw.Draw(img)
    text(d, 1000, 215, th.get("big", "LADOO COMES HOME"), th.get("px", 140), COAT, stroke=16)
    if th.get("small"): text(d, 1000, 360, th["small"], 96, "white", stroke=12)
    cast = th.get("cast", ["anya", "kabir"])
    xs = {c: x for c, x in zip(cast, [430, 1490, 260, 1660])}
    for c in cast:
        person(d, c, xs[c], 1010, 0.2, mood="excited", act="wave" if c == cast[0] else None)
    ladoo(d, 960, 1010, 150, 0.1, mood="love", act="wag", collar=th.get("collar", True))
    for k, (hx, hy, s) in enumerate([(740, 560, 50), (1190, 540, 58), (1270, 680, 38), (680, 700, 34)]):
        heart(d, hx, hy, s)
    ee.badge(d)
    img.reduce(S).resize((1280, 720), Image.LANCZOS).save(path)


def char_sheet(path):
    ee.CFG.update(W=1920, H=1080)
    EP["collar"] = True
    img = scene_bg("home").copy(); d = ImageDraw.Draw(img)
    names = ["papa", "mumma", "dadi", "anya", "kabir", "meera"]
    for i, n in enumerate(names):
        x = 170 + i * 300
        person(d, n, x, 900, 0.3, mood="happy", act="wave" if n == "kabir" else None)
        text(d, x, 960, PEOPLE[n]["label"], 44, "white", stroke=6)
    ladoo(d, 960, 1060, 70, 0.2, mood="excited", act="wag")
    for k, (m, a) in enumerate([("sad", "sad"), ("love", "lick"), ("happy", "sleep")]):
        ladoo(d, 1480 + k * 150, 1060, 46, 0.4, mood=m, act=a, collar=k > 0)
    img.reduce(S).save(path)


def load_episode(path):
    return ee.load_episode(path)


def build(ep_path, out, beats=None, vertical=False, intro=True, stills=None):
    ep = load_episode(ep_path)
    ee.CFG.update(W=1080, H=1920) if vertical else ee.CFG.update(W=1920, H=1080)
    tl, total = timeline(beats if beats is not None else ep.BEATS, intro=intro)
    EP.update(tl=tl, total=total, intro=intro, scene=getattr(ep, "SCENE", "home"),
              series=getattr(ep, "SERIES", "Ladoo Comes Home"), collar=getattr(ep, "COLLAR", True), collar_default=getattr(ep, "COLLAR", True))
    if stills is not None:
        times = stills if isinstance(stills, list) else [(s[0] + s[1]) / 2 + 0.4 for s in tl]
        ims = [Image.frombytes("RGB", (W(), H()), render_frame(int(tt * FPS))) for tt in times]
        cols = 3 if not vertical else 4
        tw = 640 if not vertical else 270
        th = int(tw * H() / W())
        sheet = Image.new("RGB", (cols * tw, math.ceil(len(ims) / cols) * th), "white")
        for k, im in enumerate(ims):
            sheet.paste(im.resize((tw, th)), ((k % cols) * tw, (k // cols) * th))
        sheet.save(out)
        return total
    wav = out + ".wav"
    make_audio(wav, tl, total, intro)
    N = int(total * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W()}x{H()}",
                           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    with Pool(os.cpu_count() or 2) as pool:
        for k, fr in enumerate(pool.imap(render_frame, range(N), chunksize=6)):
            ff.stdin.write(fr)
            if k % 600 == 0: print(f"  frame {k}/{N}", flush=True)
    ff.stdin.close(); ff.wait()
    os.remove(wav)
    return total


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("episode", nargs="?"); ap.add_argument("--out", default=None)
    ap.add_argument("--stills", action="store_true"); ap.add_argument("--ends", action="store_true")
    ap.add_argument("--short", type=int, default=0); ap.add_argument("--sheet", action="store_true")
    a = ap.parse_args()
    outdir = a.out or os.path.join(os.path.dirname(HERE), "videos")
    os.makedirs(outdir, exist_ok=True)
    if a.sheet:
        char_sheet(os.path.join(outdir, "ladoo_character_sheet.png")); sys.exit()
    ep = load_episode(a.episode)
    slug = os.path.splitext(os.path.basename(a.episode))[0]
    beats = ep.SHORTS[a.short - 1] if a.short else None
    tag = f"_short{a.short}" if a.short else ""
    if a.stills or a.ends:
        b_ = beats if beats is not None else ep.BEATS
        ee.CFG.update(W=1080, H=1920) if a.short else ee.CFG.update(W=1920, H=1080)
        tl, _ = timeline(b_, intro=not a.short)
        times = [s[1] - 0.4 for s in tl] if a.ends else None
        build(a.episode, os.path.join(outdir, f"{slug}{tag}_{'ends' if a.ends else 'sheet'}.png"), beats,
              vertical=bool(a.short), intro=not a.short, stills=times if times else True)
    else:
        tot = build(a.episode, os.path.join(outdir, f"{slug}{tag}.mp4"), beats, vertical=bool(a.short), intro=not a.short)
        if not a.short:
            thumbnail(ep, os.path.join(outdir, f"{slug}_thumbnail.png"))
        print("built", round(tot, 1), "s")
