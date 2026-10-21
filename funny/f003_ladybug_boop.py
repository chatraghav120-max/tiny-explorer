# Funny Short 3: Boop! A ladybug lands on Bobo's nose
# Pure giggles, no lesson. New gag: "ladybug" (Bobo goes cross-eyed, then Pip does too).
# Rendered vertical with:
#   python3 generator/episode_engine.py funny/f003_ladybug_boop.py --short 1

TITLE = "BOOP! A Ladybug Lands on Bobo's Nose 🐞 #shorts"
SCENE = "meadow"
BEATS = []

SHORTS = [
    [
        {"type": "gag", "gag": "ladybug", "scene": "meadow", "caption": "Look! A tiny ladybug!",
         "mid": "Bobo goes cross-eyed!", "punch": "BOOP!", "punch2": "BOOP!", "after": "Now Pip is cross-eyed too!"},
        {"type": "gag", "gag": "bonk", "scene": "orchard", "caption": "Bobo, what's up there?",
         "punch": "BOINK!", "after": "Apple snack time!"},
        {"type": "gag", "gag": "bubble", "scene": "room", "caption": "Bobo blows a giant bubble...",
         "punch": "PLOP!", "after": "Bubbly Pip! Hee hee!"},
        {"type": "bye", "scene": "room", "next": "More giggles on Tiny Explorer!"},
    ],
]
