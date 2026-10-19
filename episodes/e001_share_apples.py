# Episode 1: Count to 5 and learn to share
# Learn: counting 1-5, first taking-away question (5 - 2 = 3)
# Lesson: sharing makes friends happy

TITLE = "Count to 5 & Learn to Share 🍎 Bobo and Pip | Kids Learning Song | Tiny Explorer"
SCENE = "orchard"
LESSON = "Sharing makes friends happy!"

BEATS = [
    {"type": "hello", "text": "Hi, explorers! It's me, Bobo!", "bobo": "excited"},
    {"type": "say", "who": "bobo", "text": "And this is my best friend, Pip! Say hello to Pip!", "bobo": "happy", "pip": "happy", "flap": True},
    {"type": "say", "who": "pip", "text": "Oh no... I'm so hungry, and I have no apples.", "pip": "sad", "bobo": "surprised"},
    {"type": "say", "who": "bobo", "text": "Don't be sad, Pip! First, let's count my apples.", "pip": "sad", "bobo": "happy", "hold": "apple"},
    {"type": "count", "n": 5, "thing": "apple", "title": "Let's explore!", "total": "Five apples!"},
    {"type": "count", "n": 5, "thing": "apple", "title": "Count with me!", "total": "One, two, three, four, five!"},
    {"type": "ask", "q": "How many apples does Bobo have?", "a": "5 apples!", "show": ("apple", 5)},
    {"type": "ask", "q": "Can you show me 5 fingers?", "a": "High five!", "show": ("star", 5)},
    {"type": "say", "who": "bobo", "text": "I have five apples, and Pip has none. Hmm... what can I do?", "pip": "sad", "bobo": "surprised"},
    {"type": "ask", "q": "Should Bobo share with Pip?", "a": "Yes, share!", "show": ("heart", 3)},
    {"type": "lesson", "item": "apple", "lesson": LESSON},
    {"type": "say", "who": "pip", "text": "Thank you, Bobo! Now we both have apples!", "pip": "excited", "bobo": "excited", "flap": True},
    {"type": "count", "n": 2, "thing": "apple", "title": "Pip's apples!", "total": "Two for Pip!"},
    {"type": "count", "n": 3, "thing": "apple", "title": "Bobo's apples!", "total": "Three for Bobo!"},
    {"type": "ask", "q": "Bobo gave Pip 2 apples. How many are left?", "a": "3 apples!", "show": ("apple", 3)},
    {"type": "ask", "q": "How many apples does Pip have now?", "a": "2 apples!", "show": ("apple", 2)},
    {"type": "say", "who": "bobo", "text": "Sharing makes my heart feel happy too!", "bobo": "excited", "pip": "happy"},
    {"type": "grownup", "who": "bobo", "text": "Can you share a toy with someone today?", "bobo": "happy", "pip": "happy"},
    {"type": "grownup", "who": "pip", "text": "Count 5 things in your room with your grown-up!", "bobo": "happy", "pip": "excited"},
    {"type": "recap", "items": ["apple", "apple", "apple", "apple", "apple"], "chorus": "One, two, three, four, five... sharing is fun!"},
    {"type": "recap", "items": ["heart", "heart", "heart"], "chorus": "Share with a friend, and your friend smiles too!"},
    {"type": "bye", "next": "See you tomorrow for a new adventure!"},
]

SHORTS = [
    [
        {"type": "ask", "q": "Can you count Bobo's apples?", "a": "5 apples!", "show": ("apple", 5), "scene": "orchard"},
        {"type": "ask", "q": "Bobo shares 2. How many are left?", "a": "3 apples!", "show": ("apple", 3), "scene": "orchard"},
        {"type": "bye", "next": "Full video on Tiny Explorer!", "scene": "orchard"},
    ],
    [
        {"type": "say", "who": "pip", "text": "I'm hungry, and I have no apples...", "pip": "sad", "bobo": "surprised", "scene": "orchard"},
        {"type": "ask", "q": "Should Bobo share with Pip?", "a": "Yes, share!", "show": ("heart", 3), "scene": "orchard"},
        {"type": "lesson", "item": "apple", "lesson": LESSON, "scene": "orchard"},
        {"type": "bye", "next": "Full video on Tiny Explorer!", "scene": "orchard"},
    ],
]

THUMB = {"big": "SHARE & COUNT", "small": "1 to 5!", "px": 150,
         "objects": [("apple", 960, 760, 80), ("apple", 1080, 840, 70), ("heart", 1220, 640, 55)]}
