# Funny Short 2: Bobo's hiccups won't stop!
# Pure giggles, no lesson. Rendered vertical with:
#   python3 generator/episode_engine.py funny/f002_hiccup_bubble.py --short 1

TITLE = "HIC! Bobo Can't Stop Hiccuping 😂 #shorts"
SCENE = "orchard"
BEATS = []

SHORTS = [
    [
        {"type": "gag", "gag": "hiccup", "scene": "orchard", "caption": "Uh oh... HICCUPS!",
         "punch": "BOO!", "after": "Thank you, Pip!"},
        {"type": "gag", "gag": "bubble", "scene": "beach", "caption": "Bobo's big bubble...",
         "punch": "POP!", "after": "Pop! Right on Pip!"},
        {"type": "gag", "gag": "peekaboo", "scene": "room", "caption": "Pip, can you find Bobo?",
         "punch": "BOO-BOO!", "after": "Found you, Bobo!"},
        {"type": "bye", "scene": "room", "next": "More giggles on Tiny Explorer!"},
    ],
]
