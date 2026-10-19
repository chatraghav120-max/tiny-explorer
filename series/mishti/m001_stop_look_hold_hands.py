# Mishti to the Rescue!, Episode 1: Stop, Look, Hold Hands!
# Grumbo blows Tara's ball towards the road; Mishti's bell glows and she stops Tara; Appa holds her hand to cross.
# Lesson: stop, look and hold a grown-up's hand near the road.

SERIES = "Mishti to the Rescue!"
HERO = "mishti"
COLOR = "#ff595e"
TITLE = "Mishti to the Rescue! 🐱 Ep 1: Stop, Look, Hold Hands! | Road Safety for Kids | Tiny Explorer"
SCENE = "park"
LESSON = "Stop, look and hold a grown-up's hand!"

TM = ["tara", "mishti"]
BALL = [{"kind": "ball", "x": 0.55}]
ROLL = [{"kind": "ball", "x": 0.5, "x2": 0.97, "t0": 0.3}]
ST = {"scene": "street"}

BEATS = [
    {"type": "title", "text": "Episode 1: Stop, Look, Hold Hands!"},
    {"type": "narrate", "text": "This is Tara, and her best friend Mishti, the hero cat!",
     "cast": TM, "act": {"mishti": "swish", "tara": "wave"}, "pos": {"tara": 0.32, "mishti": 0.66}},
    {"type": "say", "who": "mishti", "think": True, "text": "I love Tara more than all the fish in the sea!", "hearts": "mishti",
     "cast": TM, "mood": {"mishti": "love"}, "act": {"mishti": "swish"}, "pos": {"tara": 0.32, "mishti": 0.66}},
    {"type": "say", "who": "tara", "text": "Mishti, let's play ball in the park!",
     "cast": TM, "props": BALL, "mood": {"tara": "excited"}, "pos": {"tara": 0.28, "mishti": 0.75}},
    {"type": "say", "who": "mishti", "text": "Meow! Meow!", "cast": TM, "props": BALL,
     "act": {"mishti": "hop"}, "mood": {"mishti": "excited"}, "pos": {"tara": 0.28, "mishti": 0.75}},
    {"type": "ask", "q": "What colours are on the ball?", "a": "Red, yellow, blue!",
     "cast": TM, "props": BALL, "pos": {"tara": 0.28, "mishti": 0.75}},
    {"type": "narrate", "text": "But someone was watching from the sky...",
     "cast": ["tara", "grumbo", "mishti"], "props": BALL, "pos": {"tara": 0.2, "grumbo": 0.55, "mishti": 0.82}},
    {"type": "say", "who": "grumbo", "text": "Hmph! Too much fun! I'll blow that ball away!",
     "cast": ["tara", "grumbo", "mishti"], "props": BALL, "mood": {"tara": "surprised", "mishti": "surprised"},
     "pos": {"tara": 0.2, "grumbo": 0.55, "mishti": 0.82}},
    {"type": "narrate", "text": "WHOOSH! The ball rolled towards the road!",
     "cast": TM, "props": ROLL, "mood": {"tara": "surprised", "mishti": "surprised"}, "pos": {"tara": 0.22, "mishti": 0.42}, **ST},
    {"type": "say", "who": "tara", "text": "My ball! I'll run and get it!",
     "cast": TM, "props": [{"kind": "ball", "x": 0.97}], "mood": {"tara": "surprised"}, "pos": {"tara": 0.3, "mishti": 0.5}, **ST},
    {"type": "ask", "q": "Should Tara run into the road?", "a": "No! Stop!",
     "cast": TM, "props": [{"kind": "ball", "x": 0.97}], "mood": {"tara": "surprised", "mishti": "surprised"}, "pos": {"tara": 0.3, "mishti": 0.5}, **ST},
    {"type": "rescue", "burst": "STOP!", "text": "Mishti to the rescue!", "at": 0.6,
     "cast": TM, "props": [{"kind": "ball", "x": 0.97}], "act": {"mishti": "glow"}, "mood": {"tara": "surprised"},
     "pos": {"tara": 0.32, "mishti": 0.6}, **ST},
    {"type": "say", "who": "mishti", "think": True, "text": "Roads have cars! Wait for a grown-up!",
     "cast": TM, "act": {"mishti": "glow"}, "pos": {"tara": 0.32, "mishti": 0.6}, **ST},
    {"type": "say", "who": "tara", "text": "You're right, Mishti. I'll ask Appa!",
     "cast": TM, "act": {"mishti": "swish"}, "pos": {"tara": 0.32, "mishti": 0.6}, **ST},
    {"type": "say", "who": "appa", "text": "Good stopping, Tara! Let's hold hands.",
     "cast": ["appa", "tara", "mishti"], "act": {"appa": "pat"}, "mood": {"tara": "excited"}, "pos": {"appa": 0.2, "tara": 0.38, "mishti": 0.56}, **ST},
    {"type": "narrate", "text": "Stop. Look left. Look right. Then cross, holding hands.",
     "cast": ["appa", "tara", "mishti"], "act": {"appa": "pat"}, "pos": {"appa": 0.2, "tara": 0.38, "mishti": 0.56}, **ST},
    {"type": "ask", "q": "Who saved Tara today?", "a": "Mishti!",
     "cast": ["appa", "tara", "mishti"], "act": {"mishti": "glow"}, "props": [{"kind": "ball", "x": 0.8}], "pos": {"appa": 0.2, "tara": 0.38, "mishti": 0.56}, **ST},
    {"type": "say", "who": "tara", "text": "Thank you, Mishti! I love you!", "hearts": "mishti",
     "cast": TM, "act": {"tara": "hug"}, "mood": {"mishti": "love", "tara": "excited"}, "pos": {"tara": 0.4, "mishti": 0.6}, **ST},
    {"type": "say", "who": "mishti", "text": "Meow! Purrrr...", "hearts": "mishti",
     "cast": TM, "act": {"mishti": "hop"}, "mood": {"mishti": "love", "tara": "excited"}, "pos": {"tara": 0.4, "mishti": 0.6}, **ST},
    {"type": "say", "who": "grumbo", "text": "Hmph! That cat always saves the day!",
     "cast": ["tara", "grumbo", "mishti"], "act": {"mishti": "swish"}, "pos": {"tara": 0.2, "grumbo": 0.66, "mishti": 0.84}},
    {"type": "say", "who": "tara", "text": "Grumbo, that wasn't kind! Want to play with us?",
     "cast": ["tara", "grumbo", "mishti"], "pos": {"tara": 0.2, "grumbo": 0.66, "mishti": 0.84}},
    {"type": "say", "who": "grumbo", "text": "Maybe... next time! Hmph!",
     "cast": ["tara", "grumbo", "mishti"], "pos": {"tara": 0.2, "grumbo": 0.66, "mishti": 0.84}},
    {"type": "moment", "text": "My hero, Mishti!", "hearts": "mishti",
     "cast": TM, "act": {"tara": "hug", "mishti": "hop"}, "mood": {"tara": "excited", "mishti": "love"}, "pos": {"tara": 0.4, "mishti": 0.6}},
    {"type": "lesson", "text": LESSON, "cast": ["appa", "tara", "mishti"], "mood": {"mishti": "excited"}, "act": {"mishti": "hop"}},
    {"type": "grownup", "who": "appa", "text": "Always hold a grown-up's hand near the road!",
     "cast": ["appa", "tara", "mishti"], "act": {"appa": "pat"}, **ST},
    {"type": "bye", "next": "Next time: Mishti and the Hot Pot!", "cast": ["amma", "tara", "mishti", "appa"]},
]

SHORTS = [
    [
        {"type": "say", "who": "tara", "text": "My ball! I'll run and get it!",
         "cast": TM, "props": ROLL, "mood": {"tara": "surprised"}, **ST},
        {"type": "ask", "q": "Should Tara run into the road?", "a": "No! Stop!",
         "cast": TM, "mood": {"tara": "surprised", "mishti": "surprised"}, **ST},
        {"type": "rescue", "burst": "STOP!", "text": "Mishti to the rescue!", "cast": TM, "act": {"mishti": "glow"}, "mood": {"tara": "surprised"}, **ST},
        {"type": "moment", "text": "My hero, Mishti!", "hearts": "mishti",
         "cast": TM, "act": {"tara": "hug", "mishti": "hop"}, "mood": {"tara": "excited", "mishti": "love"}},
        {"type": "bye", "next": "Full episode on Tiny Explorer!", "cast": TM},
    ],
]

THUMB = {"big": "MISHTI TO THE RESCUE!", "small": "Stop, Look, Hold Hands!", "scene": "street", "cast": ["tara", "appa"], "px": 120}
