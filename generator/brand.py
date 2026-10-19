"""Tiny Explorer branded intro (3.5s) + branded thumbnail; joins intro onto the counting video."""
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.io import wavfile

sys.path.insert(0, "/home/claude/counting")
import make_video as mv
from make_video import ell, poly, line, text, font, DRAW, NUM_COLORS, INK, P, S, W, H, FPS, ease_out_back, clamp01

src = open("/home/claude/counting/make_banner.py").read()
start = src.index("def explorer(")
end = src.index("explorer(d, 700, 790, 130)")
ns = dict(mv.__dict__)
ns.update(dict(math=math))
exec(src[start:end], ns)
explorer = ns["explorer"]

OUT = "/home/claude/counting"
DUR = 3.5
BG = mv.make_bg()


def rainbow_title(d, cx, cy, px, t0, t, stroke=12):
    title = "Tiny Explorer"
    f = font(px)
    total = sum(f.getlength(c) for c in title) / S
    x = cx - total / 2
    for k, c in enumerate(title):
        w = f.getlength(c) / S
        a = ease_out_back((t - t0 - k * 0.06) / 0.35)
        if c != " " and a > 0.01:
            yy = cy + (1 - a) * 160 + math.sin(t * 5 + k * 0.9) * 8
            text(d, x + w / 2, yy, c, max(8, int(px * max(a, 0.25))), NUM_COLORS[k % 10], stroke=stroke)
        x += w


def frame(t):
    img = BG.copy()
    d = ImageDraw.Draw(img)
    mv.clouds(d, t + 10)
    # sparkles
    for k in range(10):
        a = ease_out_back((t - 1.6 - k * 0.05) / 0.3)
        if a > 0.01:
            ang = k * math.tau / 10 + t
            x = 960 + math.cos(ang) * (520 + 40 * math.sin(t * 3 + k))
            y = 400 + math.sin(ang) * 230
            poly(d, mv.star_pts(x, y, 22 * a, 10 * a, t), "#fff3a3", ow=3)
    # Bobo rises from the hill
    a = ease_out_back((t - 0.15) / 0.6)
    by = 1350 - a * 530 + math.sin(t * 6) * 6 * a
    explorer(d, 960, by, 140)
    rainbow_title(d, 960, 330, 170, 0.9, t)
    a2 = ease_out_back((t - 2.0) / 0.4)
    if a2 > 0.01:
        sub = "Songs  •  Counting  •  Learning"
        sw = font(50).getlength(sub) / S
        k = max(a2, 0.2)
        d.rounded_rectangle([P(960 - (sw / 2 + 40) * k), P(470 - 42 * k), P(960 + (sw / 2 + 40) * k), P(470 + 42 * k)],
                            radius=int(P(40 * k)), fill="white", outline=INK, width=int(P(5)))
        text(d, 960, 472, sub, max(8, int(50 * k)), "#ff6b35", stroke=0)
    out = img.reduce(S)
    fade_in = clamp01(t / 0.25)
    fade_out = clamp01((DUR - t) / 0.35)
    f = min(fade_in, fade_out)
    if f < 1:
        out = Image.blend(Image.new("RGB", out.size, "white"), out, f)
    return out.tobytes()


def jingle(path):
    sr = mv.SR
    buf = np.zeros(int(DUR * sr) + sr)

    def add(sig, t):
        i = int(t * sr); j = min(len(buf), i + len(sig)); buf[i:j] += sig[: j - i]

    # whoosh-up as Bobo pops
    tt = np.arange(int(0.5 * sr)) / sr
    ph = 2 * np.pi * np.cumsum(300 + 900 * tt / 0.5) / sr
    add(np.sin(ph) * np.exp(-tt * 5) * 0.25 * np.minimum(1, tt / 0.05), 0.1)
    # letter pops on a pentatonic run
    notes = [72, 74, 76, 79, 81, 84, 86, 88, 91, 93, 96, 98]
    for k in range(12):
        add(mv.tone(mv.mtof(notes[k]), 0.3, 12, 0.16, (1, 0.5, 0.2)), 0.9 + k * 0.06)
    # big happy chord + bell
    for m in [48, 60, 64, 67, 72, 76]:
        add(mv.tone(mv.mtof(m), 1.6, 1.8, 0.11, (1, 0.35, 0.1)), 1.75)
    tt = np.arange(int(1.4 * sr)) / sr
    f = mv.mtof(96)
    add((np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2.76 * f * tt) * np.exp(-tt * 4)) * np.exp(-tt * 3) * 0.2, 1.75)
    # little kick pulse
    for b in [1.75, 2.25, 2.75]:
        tt = np.arange(int(0.15 * sr)) / sr
        ph = 2 * np.pi * np.cumsum(45 + 80 * np.exp(-tt * 30)) / sr
        add(np.sin(ph) * np.exp(-tt * 16) * 0.45, b)
    buf = buf[: int(DUR * sr)]
    buf /= np.max(np.abs(buf)) + 1e-9
    buf = np.tanh(buf * 1.2) / np.tanh(1.2) * 0.85
    fl = int(0.3 * sr); buf[-fl:] *= np.linspace(1, 0, fl)
    wavfile.write(path, sr, (buf * 32767).astype(np.int16))


def thumbnail(path):
    img = mv.make_bg()
    d = ImageDraw.Draw(img)
    mv.clouds(d, 3)
    for k, (x, y, s) in enumerate([(230, 760, 95), (450, 840, 85), (1470, 830, 90), (1690, 720, 80)]):
        DRAW[["star", "apple", "duck", "heart"][k]](d, x, y, s, 0.3, k)
    text(d, 960, 230, "COUNT", 240, "#ffca3a", stroke=16)
    text(d, 960, 450, "1 to 10!", 200, "white", stroke=16)
    explorer(d, 960, 840, 150)
    # channel badge, top-left
    d.rounded_rectangle([P(40), P(36), P(560), P(126)], radius=int(P(45)), fill="white", outline=INK, width=int(P(6)))
    x = 70
    f = font(56)
    for k, c in enumerate("Tiny Explorer"):
        w = f.getlength(c) / S
        if c != " ":
            text(d, x + w / 2, 82, c, 56, NUM_COLORS[k % 10], stroke=5)
        x += w
    img.reduce(S).resize((1280, 720), Image.LANCZOS).save(path)


if __name__ == "__main__":
    if sys.argv[1:] == ["stills"]:
        for t in [0.5, 1.4, 2.6]:
            Image.frombytes("RGB", (W, H), frame(t)).save(f"{OUT}/brand_{t}.png")
        thumbnail(f"{OUT}/thumbnail.png")
        sys.exit()
    jingle(f"{OUT}/jingle.wav")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", f"{OUT}/jingle.wav",
                           "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                           "-ar", "44100", "-shortest", f"{OUT}/brand_intro.mp4"], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        ff.stdin.write(frame(i / FPS))
    ff.stdin.close(); ff.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/brand_intro.mp4", "-i", f"{OUT}/Lets_Count_1_to_10.mp4",
                    "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    f"{OUT}/Tiny_Explorer_Lets_Count_1_to_10.mp4"], check=True)
    thumbnail(f"{OUT}/thumbnail.png")
    print("done")
