# Ladoo Comes Home, Episode 1: Adoption Day
# A lonely shelter puppy meets a family who take him home and name him Ladoo.
# Lesson: every puppy needs love and a home.

SERIES = "Ladoo Comes Home"
TITLE = "Ladoo Comes Home 🐶 Ep 1: Adoption Day | Puppy Story for Kids | Tiny Explorer"
SCENE = "shelter"
COLLAR = True
LESSON = "Every puppy needs love and a home!"

FAM = ["mumma", "papa", "anya", "kabir", "ladoo"]
SH = {"scene": "shelter", "collar": False}

BEATS = [
    {"type": "title", "text": "Episode 1: Adoption Day", **SH},
    {"type": "narrate", "text": "At the Happy Paws shelter lived a little puppy with no name.",
     "cast": ["meera", "ladoo"], "mood": {"ladoo": "sad"}, "act": {"ladoo": "sad"}, "sad": True, **SH},
    {"type": "say", "who": "ladoo", "think": True, "text": "All my friends found homes... will anyone pick me?",
     "cast": ["ladoo"], "mood": {"ladoo": "sad"}, "act": {"ladoo": "sad"}, "sad": True, **SH},
    {"type": "ask", "q": "How is the puppy feeling?", "a": "Sad and lonely",
     "cast": ["ladoo"], "mood": {"ladoo": "sad"}, "act": {"ladoo": "sad"}, "sad": True, **SH},
    {"type": "narrate", "text": "Then one sunny morning, the door opened...",
     "cast": ["ladoo"], "mood": {"ladoo": "surprised"}, **SH},
    {"type": "say", "who": "kabir", "text": "Look, Mumma! That puppy is all alone!",
     "cast": FAM, "mood": {"ladoo": "surprised", "kabir": "surprised"}, **SH},
    {"type": "say", "who": "meera", "text": "He's an indie pup. He has waited a long time for a family.",
     "cast": ["meera", "anya", "kabir", "ladoo"], "mood": {"ladoo": "sad"}, **SH},
    {"type": "say", "who": "anya", "text": "Hello, puppy! You can sniff my hand first.",
     "cast": ["meera", "kabir", "anya", "ladoo"], "act": {"anya": "pat", "ladoo": "sniff"}, "mood": {"ladoo": "surprised"}, **SH},
    {"type": "say", "who": "ladoo", "think": True, "text": "She's so gentle... I like her!",
     "cast": ["kabir", "anya", "ladoo"], "act": {"anya": "pat", "ladoo": "wag"}, **SH},
    {"type": "say", "who": "papa", "text": "Would you like to come home with us, little one?",
     "cast": FAM, "mood": {"ladoo": "surprised"}, **SH},
    {"type": "say", "who": "ladoo", "text": "Woof! Woof! Woof!", "hearts": "ladoo",
     "cast": FAM, "mood": {"ladoo": "excited", "kabir": "excited", "anya": "excited"}, "act": {"ladoo": "hop"}, **SH},
    {"type": "ask", "q": "Should the family take the puppy home?", "a": "Yes!",
     "cast": FAM, "mood": {"ladoo": "excited"}, "act": {"ladoo": "wag"}, **SH},

    {"type": "narrate", "text": "Home at last! A red collar, a soft bed and a big happy family.",
     "scene": "home", "cast": ["mumma", "papa", "ladoo", "anya", "kabir"], "act": {"ladoo": "wag"}},
    {"type": "say", "who": "papa", "text": "Here is your very own bed, little one!",
     "scene": "home", "cast": ["mumma", "papa", "ladoo", "anya", "kabir"], "act": {"ladoo": "sniff", "papa": "pat"}, "mood": {"ladoo": "surprised"}},
    {"type": "say", "who": "ladoo", "think": True, "text": "Is this... my home now?",
     "scene": "home", "cast": ["mumma", "papa", "ladoo", "anya", "kabir"], "mood": {"ladoo": "surprised"}},
    {"type": "ask", "q": "How many people are in the puppy's family?", "a": "Four!",
     "scene": "home", "cast": ["mumma", "papa", "ladoo", "anya", "kabir"], "act": {"ladoo": "wag"}},
    {"type": "say", "who": "kabir", "text": "He needs a name! What should we call him?",
     "scene": "home", "cast": ["mumma", "papa", "ladoo", "anya", "kabir"], "act": {"ladoo": "wag"}},
    {"type": "ask", "q": "What colour is the puppy?", "a": "Golden!",
     "scene": "home", "cast": ["mumma", "ladoo", "kabir"], "act": {"ladoo": "wag"}},
    {"type": "say", "who": "mumma", "text": "He's golden and sweet, just like a ladoo!",
     "scene": "home", "cast": ["mumma", "papa", "ladoo", "anya", "kabir"], "mood": {"anya": "excited", "kabir": "excited"}},
    {"type": "say", "who": "anya", "text": "Ladoo! Do you like your new name?",
     "scene": "home", "cast": ["mumma", "papa", "ladoo", "anya", "kabir"], "act": {"ladoo": "wag"}},
    {"type": "moment", "text": "Welcome home, Ladoo!", "hearts": "ladoo",
     "scene": "home", "cast": ["anya", "ladoo", "kabir"], "act": {"ladoo": "lick", "kabir": "hug", "anya": "pat"},
     "mood": {"ladoo": "love", "kabir": "excited", "anya": "excited"}, "pos": {"anya": 0.3, "ladoo": 0.5, "kabir": 0.68}},
    {"type": "say", "who": "ladoo", "think": True, "text": "I have a name... and a family who loves me!",
     "scene": "home", "cast": ["mumma", "papa", "ladoo", "anya", "kabir"], "mood": {"ladoo": "love"}, "act": {"ladoo": "wag"}, "hearts": "ladoo"},
    {"type": "say", "who": "kabir", "text": "I love you, Ladoo!", "hearts": "ladoo",
     "scene": "home", "cast": ["anya", "ladoo", "kabir"], "act": {"kabir": "hug", "ladoo": "wag"}, "mood": {"ladoo": "love", "kabir": "excited"}},
    {"type": "say", "who": "ladoo", "text": "Woof! Woof!", "hearts": "ladoo",
     "scene": "home", "cast": ["anya", "ladoo", "kabir"], "act": {"ladoo": "hop"}, "mood": {"ladoo": "excited", "kabir": "excited", "anya": "excited"}},
    {"type": "lesson", "text": LESSON,
     "scene": "home", "cast": ["mumma", "papa", "ladoo", "anya", "kabir"], "mood": {"ladoo": "excited"}, "act": {"ladoo": "hop"}},
    {"type": "grownup", "who": "anya", "text": "Always ask a grown-up before you pet a dog!",
     "scene": "home", "cast": ["anya", "ladoo", "kabir"], "act": {"ladoo": "wag"}},
    {"type": "bye", "next": "Next time: Ladoo's First Night!",
     "scene": "home", "cast": ["mumma", "papa", "ladoo", "anya", "kabir"]},
]

SHORTS = [
    [
        {"type": "say", "who": "ladoo", "think": True, "text": "Will anyone ever pick me?",
         "cast": ["ladoo"], "mood": {"ladoo": "sad"}, "act": {"ladoo": "sad"}, "sad": True, **SH},
        {"type": "say", "who": "papa", "text": "Would you like to come home with us?",
         "cast": ["papa", "ladoo"], "mood": {"ladoo": "surprised"}, **SH},
        {"type": "say", "who": "ladoo", "text": "Woof! Woof!", "hearts": "ladoo",
         "cast": ["papa", "ladoo"], "mood": {"ladoo": "excited"}, "act": {"ladoo": "hop"}, **SH},
        {"type": "moment", "text": "Welcome home, Ladoo!", "hearts": "ladoo",
         "scene": "home", "cast": ["kabir", "ladoo"], "act": {"ladoo": "lick", "kabir": "hug"}, "mood": {"ladoo": "love", "kabir": "excited"}},
        {"type": "bye", "next": "Full episode on Tiny Explorer!", "scene": "home", "cast": ["anya", "ladoo"]},
    ],
]

THUMB = {"big": "LADOO COMES HOME", "small": "Adoption Day!", "scene": "home", "cast": ["anya", "kabir"]}
