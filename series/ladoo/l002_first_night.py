# Ladoo Comes Home, Episode 2: Ladoo's First Night
# New home, new sounds: Ladoo cries on his first night. Kabir and Anya (with Mumma) bring
# his shelter blanket and a ticking clock, and love helps him fall asleep.
# Lesson: when you're scared, love helps.

SERIES = "Ladoo Comes Home"
TITLE = "Ladoo Comes Home 🐶 Ep 2: Ladoo's First Night | Puppy Story for Kids | Tiny Explorer"
SCENE = "home"
COLLAR = True
LESSON = "When you're scared, love helps!"

FAM = ["mumma", "papa", "ladoo", "anya", "kabir"]
N = {"scene": "home_night"}

# props sized for a 3-person cast (Ladoo in the middle) and for Ladoo alone
BED3 = {"kind": "bed", "x": 0.5}
BED1 = {"kind": "bed", "x": 0.5, "s": 1.45}
BLANKET3 = {"kind": "blanket", "x": 0.5, "front": True}
BLANKET1 = {"kind": "blanket", "x": 0.5, "front": True, "s": 1.45}
CLOCK3 = {"kind": "clock", "x": 0.61}
P3 = {"pos": {"anya": 0.3, "mumma": 0.3, "ladoo": 0.5, "kabir": 0.72}}
CLOCK1 = {"kind": "clock", "x": 0.7, "s": 1.3}

BEATS = [
    {"type": "title", "text": "Episode 2: Ladoo's First Night"},
    {"type": "narrate", "text": "Ladoo played all day in his new home. Now it was bedtime!",
     "cast": FAM, "act": {"ladoo": "wag"}, "props": [BED3]},
    {"type": "say", "who": "mumma", "text": "Goodnight, Ladoo! Here is your cosy bed.",
     "cast": FAM, "act": {"ladoo": "sniff", "mumma": "wave"}, "props": [BED3]},
    {"type": "say", "who": "kabir", "text": "Goodnight, Ladoo! See you in the morning!",
     "cast": FAM, "act": {"kabir": "wave", "ladoo": "wag"}, "props": [BED3]},

    {"type": "narrate", "text": "The lights went off. The house was dark and very quiet...",
     "cast": ["ladoo"], "mood": {"ladoo": "surprised"}, "props": [BED1], **N},
    {"type": "say", "who": "ladoo", "think": True, "text": "What was that sound? Where is everyone?",
     "cast": ["ladoo"], "mood": {"ladoo": "surprised"}, "props": [BED1], **N},
    {"type": "say", "who": "ladoo", "think": True, "text": "I miss my shelter friends... I feel all alone.",
     "cast": ["ladoo"], "mood": {"ladoo": "sad"}, "act": {"ladoo": "sad"}, "sad": True, "props": [BED1], **N},
    {"type": "ask", "q": "How is Ladoo feeling?", "a": "Scared and lonely",
     "cast": ["ladoo"], "mood": {"ladoo": "sad"}, "act": {"ladoo": "sad"}, "sad": True, "props": [BED1], **N},
    {"type": "say", "who": "ladoo", "text": "Woof... woof...",
     "cast": ["ladoo"], "mood": {"ladoo": "sad"}, "act": {"ladoo": "sad"}, "sad": True, "props": [BED1], **N},

    {"type": "narrate", "text": "Anya and Kabir heard him. They went to wake up Mumma.",
     "cast": ["mumma", "anya", "kabir"], "mood": {"kabir": "surprised"}, **N},
    {"type": "say", "who": "anya", "text": "Mumma, Ladoo is crying. I think he's scared!",
     "cast": ["mumma", "anya", "kabir"], "mood": {"anya": "sad", "kabir": "sad"}, **N},
    {"type": "say", "who": "mumma", "text": "A new home can feel big and scary. Let's help him.",
     "cast": ["mumma", "anya", "kabir"], "act": {"mumma": "pat"}, **N},
    {"type": "ask", "q": "What can help Ladoo sleep?", "a": "Love and a cosy blanket!",
     "cast": ["anya", "ladoo", "kabir"], **P3, "mood": {"ladoo": "sad"}, "act": {"ladoo": "sad"}, "props": [BED3], **N},

    {"type": "say", "who": "anya", "text": "Meera Didi gave us your shelter blanket!",
     "cast": ["anya", "ladoo", "kabir"], **P3, "mood": {"ladoo": "surprised"}, "act": {"ladoo": "sniff"},
     "props": [BED3, BLANKET3], **N},
    {"type": "say", "who": "ladoo", "think": True, "text": "It smells like my old friends... so cosy!",
     "cast": ["anya", "ladoo", "kabir"], **P3, "act": {"ladoo": "wag"}, "props": [BED3, BLANKET3], **N},
    {"type": "say", "who": "kabir", "text": "And a ticking clock, like a heartbeat. Tick, tock!",
     "cast": ["anya", "ladoo", "kabir"], **P3, "act": {"ladoo": "wag"}, "mood": {"kabir": "excited"},
     "props": [BED3, BLANKET3, CLOCK3], **N},
    {"type": "say", "who": "mumma", "text": "Gentle hands and soft voices. Puppies need sleep.",
     "cast": ["mumma", "ladoo", "kabir"], **P3, "act": {"mumma": "pat", "ladoo": "wag"},
     "props": [BED3, BLANKET3, CLOCK3], **N},
    {"type": "moment", "text": "Safe and loved!", "hearts": "ladoo",
     "cast": ["anya", "ladoo", "kabir"], **P3, "act": {"anya": "pat", "kabir": "pat", "ladoo": "lick"},
     "mood": {"ladoo": "love", "kabir": "excited", "anya": "excited"},
     "props": [BED3, BLANKET3, CLOCK3], **N},
    {"type": "say", "who": "ladoo", "think": True, "text": "I'm not alone. I have a family who loves me!",
     "cast": ["anya", "ladoo", "kabir"], **P3, "mood": {"ladoo": "love"}, "act": {"ladoo": "wag"}, "hearts": "ladoo",
     "props": [BED3, BLANKET3, CLOCK3], **N},
    {"type": "say", "who": "mumma", "text": "Now back to bed, my sleepy explorers!",
     "cast": ["mumma", "anya", "kabir"], "act": {"anya": "wave", "kabir": "wave"}, **N},

    {"type": "narrate", "text": "Tick, tock... soon Ladoo was fast asleep. Goodnight, Ladoo!",
     "cast": ["ladoo"], "act": {"ladoo": "sleep"}, "props": [BED1, BLANKET1, CLOCK1], **N},
    {"type": "ask", "q": "Is Ladoo awake or asleep?", "a": "Asleep!",
     "cast": ["ladoo"], "act": {"ladoo": "sleep"}, "props": [BED1, BLANKET1, CLOCK1], **N},

    {"type": "narrate", "text": "In the morning, the sun came up. Ladoo woke up happy!",
     "cast": FAM, "mood": {"ladoo": "excited"}, "act": {"ladoo": "hop"}, "props": [BED3]},
    {"type": "say", "who": "ladoo", "text": "Woof! Woof! Woof!", "hearts": "ladoo",
     "cast": FAM, "mood": {"ladoo": "excited", "kabir": "excited", "anya": "excited"}, "act": {"ladoo": "hop"}},
    {"type": "say", "who": "papa", "text": "Good morning, Ladoo! Did you sleep well?",
     "cast": FAM, "act": {"papa": "wave", "ladoo": "wag"}},
    {"type": "lesson", "text": LESSON,
     "cast": FAM, "mood": {"ladoo": "excited"}, "act": {"ladoo": "hop"}},
    {"type": "grownup", "who": "anya", "text": "Let a sleeping puppy rest. Don't wake him up!",
     "cast": ["anya", "ladoo", "kabir"], **P3, "act": {"ladoo": "sleep"}, "props": [BED3, BLANKET3], **N},
    {"type": "bye", "next": "Next time: Gentle Hands!", "cast": FAM},
]

SHORTS = [
    [
        {"type": "say", "who": "ladoo", "think": True, "text": "It's so dark... I feel all alone.",
         "cast": ["ladoo"], "mood": {"ladoo": "sad"}, "act": {"ladoo": "sad"}, "sad": True, "props": [BED1], **N},
        {"type": "say", "who": "anya", "text": "Here's your cosy shelter blanket!",
         "cast": ["anya", "ladoo"], "act": {"ladoo": "sniff"}, "mood": {"ladoo": "surprised"},
         "pos": {"anya": 0.27, "ladoo": 0.66}, "props": [{"kind": "bed", "x": 0.66, "s": 1.25}, {"kind": "blanket", "x": 0.66, "front": True, "s": 1.25}], **N},
        {"type": "say", "who": "kabir", "text": "And a ticking clock. Tick, tock!",
         "cast": ["kabir", "ladoo"], "act": {"ladoo": "wag"}, "mood": {"kabir": "excited"},
         "pos": {"kabir": 0.27, "ladoo": 0.66}, "props": [{"kind": "bed", "x": 0.66, "s": 1.25}, {"kind": "blanket", "x": 0.66, "front": True, "s": 1.25}], **N},
        {"type": "moment", "text": "Love helps!", "hearts": "ladoo",
         "cast": ["ladoo"], "act": {"ladoo": "sleep"}, "props": [BED1, BLANKET1, {"kind": "clock", "x": 0.8, "s": 1.3}], **N},
        {"type": "bye", "next": "Full episode on Tiny Explorer!", "cast": ["kabir", "ladoo"]},
    ],
]

THUMB = {"big": "LADOO COMES HOME", "small": "First Night!", "scene": "home_night", "cast": ["anya", "kabir"]}
