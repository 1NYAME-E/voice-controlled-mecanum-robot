# Making the necessary imports
import random
import re

import joblib
from sklearn import metrics
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC
from sklearn.utils import shuffle

# Ensuring we always get the same results
random.seed(42)

# The dataset used
data = {
    # For Basic Movement
    "FORWARD": [
        "move forward", "go forward", "drive forward", "advance", "keep going",
        "forward", "onward", "in front", "move ahead", "go ahead", "push forward",
        "continue forward", "proceed forward", "head forward", "go straight",
        "move straight", "drive straight", "go straight ahead", "keep moving",
        "keep moving forward", "straight ahead", "go on", "continue", "proceed",
        "go this way", "this way", "come forward", "roll forward", "inch forward",
        "press on", "march forward", "charge ahead", "move up", "go up",
        "shift forward", "push ahead", "go front", "move front",
        # Accounting for Ghanaian phrases
        "move small forward", "go forward small", "take it forward",
        "go forward small small", "let it move forward", "bring it forward",
        "shift small forward", "move am forward", "go forward make we see",
        # Accounting for wrong pronunciations
        "move foreword",
        "go foreword",
        "drive foreword",
        "move for word",
        "go for word",
        "head for it",
        "ford ward",
        "move for ward",
        "go for ward",
        "moo forward",
        "moo foreword",
        "groove forward",
        "strayed ahead",
        "straight a head",
        "go strait ahead",
        "strait ahead",
        "keep go in",
        "keep moving for",
        "ad vance",
        "on ward",
    ],

    "BACKWARD": [
        "move backward", "go backward", "reverse", "back up", "retreat",
        "go back", "move back", "drive backward", "pull back", "step back",
        "roll back", "come back", "go in reverse", "head backward",
        "reverse a little", "back off", "move in reverse", "go backwards",
        "reverse slowly", "drift back", "recede", "fall back",
        # Accounting for Ghanaian phrases
        "come back small", "reverse small", "go back small small",
        "move back small", "take am back", "shift back", "go back make we see",
        "small reverse", "reverse small small", "back small",
        # Accounting for wrong pronunciations
        "move backboard",
        "go backboard",
        "drive backboard",
        "move back were",
        "go back were",
        "move back word",
        "back words",
        "go back words",
        "move back words",
        "re verse",
        "re-verse",
        "reverse lee",
        "back cop",
        "backup",
        "move beck",
        "go beck",
        "pull beck",
        "re treat",
        "re-treat",
        "re cede",
        "moo back",
        "groove back",
    ],

    "STRAFE_LEFT": [
        "move left", "go left", "slide left", "strafe left", "scoot left",
        "shift left", "drift left", "step left", "move to the left",
        "go to the left", "head left", "veer left", "lean left",
        "sidestep left", "move sideways left", "go sideways left",
        "slide to the left", "shift to the left", "inch left",
        "move a little to the left", "go a bit left",
        # Accounting for Ghanaian phrases
        "move left small", "go left small small", "shift small to left",
        "left small", "take am left", "enter left", "move go left",
        # Accounting for wrong pronunciations
        "move lift",
        "go lift",
        "slide lift",
        "step lift",
        "head lift",
        "veer lift",
        "shift lift",
        "move to the lift",
        "go to the lift",
        "move laughed",
        "go laughed",
        "slide laughed",
        "move lest",
        "go lest",
        "move led",
        "go led",
        "move let",
        "go let",
        "move loft",
        "go loft",
        "slide to the lift",
        "shift to the lift",
        "scoot lift",
        "inch lift",
        "drift lift",
        "lean lift",
        "side step left",
        "side step lift",
        "move left word",
        "go leftward",
        "move leftward",
    ],

    "STRAFE_RIGHT": [
        "move right", "go right", "slide right", "strafe right", "scoot right",
        "shift right", "drift right", "step right", "move to the right",
        "go to the right", "head right", "veer right", "lean right",
        "sidestep right", "move sideways right", "go sideways right",
        "slide to the right", "shift to the right", "inch right",
        "move a little to the right", "go a bit right",
        # Accounting for Ghanaian phrases
        "move right small", "go right small small", "shift small to right",
        "right small", "take am right", "enter right", "move go right",
        # Accounting for wrong pronunciations
        "move write",
        "go write",
        "slide write",
        "step write",
        "head write",
        "veer write",
        "shift write",
        "move to the write",
        "go to the write",
        "move ride",
        "go ride",
        "slide ride",
        "move wright",
        "go wright",
        "move rite",
        "go rite",
        "slide to the write",
        "shift to the write",
        "scoot write",
        "inch write",
        "drift write",
        "lean write",
        "move side ways right",
        "go side ways right",
        "side step right",
        "side step write",
        "move right word",
        "go rightward",
        "move rightward",
    ],

    "ROTATE_LEFT": [
        "turn left", "rotate left", "spin left", "pivot left", "look left",
        "face left", "swing left", "turn to the left", "rotate to the left",
        "spin to the left", "bear left", "yaw left", "wheel left",
        "turn anticlockwise", "rotate anticlockwise", "spin anticlockwise",
        "turn counterclockwise", "rotate counterclockwise",
        "do a left turn", "make a left turn", "face the other way left",
        # Accounting for Ghanaian phrases
        "turn left small", "rotate small to left", "face left small",
        "small turn left", "turn go left",
        # Accounting for wrong pronunciations
        "ten left",
        "tern left",
        "torn left",
        "tan left",
        "ton left",
        "ten to the left",
        "tern to the left",
        "torn to the left",
        "ten lift",
        "tern lift",
        "torn lift",
        "turn lift",
        "turn laughed",
        "turn lest",
        "ten lift",
        "road eight left",
        "row tate left",
        "ro tate left",
        "road eight to the left",
        "anti clock wise",
        "anti clockwise",
        "counter clock wise",
        "counter clock",
        "counter clockwise",
        "anti-clockwise",
        "counter-clockwise",
        "anti clock",
        "turn anti",
        "rotate anti",
        "pit it left",
        "piv it left",
    ],

    "ROTATE_RIGHT": [
        "turn right", "rotate right", "spin right", "pivot right", "look right",
        "face right", "swing right", "turn to the right", "rotate to the right",
        "spin to the right", "bear right", "yaw right", "wheel right",
        "turn clockwise", "rotate clockwise", "spin clockwise",
        "do a right turn", "make a right turn", "face the other way right",
        "twirl", "360", "do a spin", "do a full spin", "spin around",
        "do a full rotation", "turn around", "face the other way",
        "flip around",
        # Accounting for Ghanaian phrases
        "turn right small", "rotate small to right", "face right small",
        "small turn right", "turn go right",
        # Accounting for wrong pronunciations
        "ten right",
        "tern right",
        "torn right",
        "tan right",
        "ton right",
        "ten to the right",
        "tern to the right",
        "torn to the right",
        "ten write",
        "tern write",
        "torn write",
        "turn write",
        "turn ride",
        "turn wright",
        "ten write",
        "road eight right",
        "row tate right",
        "ro tate right",
        "road eight to the right",
        "clock wise",
        "clock ways",
        "clock wised",
        "turn clock",
        "rotate clock",
        "pit it right",
        "piv it right",
        "three sixty",
        "do three sixty",
        "do a three sixty",
        "three hundred sixty",
        "full spin",
        "full rotation",
        "yaw right",
        "yore right",
        "your right",
        "face the other way write",
        "flip a round",
    ],

    "STOP": [
        "stop", "halt", "freeze", "kill the motors", "brake", "wait",
        "stay", "pause", "hold on", "stop moving", "cease", "don't move",
        "stand still", "stay still", "hold your position", "quit moving",
        "hold it", "hold there", "hold", "stop right there",
        "stop where you are", "don't go anywhere", "stay put",
        "cut it out", "enough", "that's enough", "stop now",
        "kill it", "shut down", "power off", "turn off", "end",
        "abort", "cancel", "stop everything", "emergency stop",
        "stop immediately", "stop at once", "whoa", "wait there",
        # Accounting for Ghanaian phrases
        "stop there", "park there", "wait small", "hold on small",
        "make it stop", "let it stop", "stop am", "don't move at all",
        "stop the thing", "ei stop", "chale stop", "stay there", "wait dey",
        # Accounting for wrong pronunciations
        "shop",
        "stomp",
        "strop",
        "stock",
        "stop it",
        "stop now please",
        "full stop",
        "dead stop",
        "complete stop",
        "halt there",
        "halt now",
        "free's",
        "frees",
        "freese",
        "break",
        "breaks",
        "apply the break",
        "apply the brake",
        "don't move please",
        "hold up",
        "hold up there",
        "wait up",
        "hold still",
        "stand by",
        "stay in place",
        "don't budge",
        "no more moving",
        "kill motors",
        "kill the engine",
        "power down",
        "shut it down",
        "turn it off",
        "emergency brake",
        "e stop",
        "e-stop",
        "cease and desist",
        "abort mission",
        "chale stop am",
        "stop am there",
    ],

    "SPEED_UP": [
        "speed up", "go faster", "move faster", "accelerate", "faster",
        "increase speed", "pick up speed", "pick up the pace", "go quicker",
        "move quicker", "quicker", "go swift", "be swift", "rush",
        "hurry", "hurry up", "go at full speed", "full speed", "full speed ahead",
        "maximum speed", "max speed", "push it", "push harder",
        "throttle up", "throttle it up", "open it up", "open up the throttle",
        "go at top speed", "top speed", "boost", "boost speed",
        "increase pace", "move with urgency", "pick it up",
        "step it up", "kick it up", "kick it into gear",
        "move faster please", "go a bit faster", "go a lot faster",
        "rev it up", "rev up", "crank it up",
        # Accounting for Ghanaian phrases
        "move faster small", "go fast small", "pick up small",
        "speed up small", "add speed", "add more speed", "go fast make we see",
        "chale go faster", "zoom zoom", "shift small faster",
        "make it go faster", "let it go faster", "push am faster",
        "fast small", "add am speed",
        # Accounting for wrong pronunciations
        "speed cup",
        "speeding up",
        "speed it up",
        "speeds up",
        "speak up",
        "speed op",
        "ac celerate",
        "ac-celerate",
        "a celerate",
        "a-celerate",
        "excel arate",
        "excel rate",
        "axle rate",
        "throttle cup",
        "throttle op",
        "go fester",
        "move fester",
        "go foster",
        "move foster",
        "go pastor",
        "go farther",
        "move farther",
        "full speed a head",
        "full speed a-head",
        "hurry cop",
        "hurry op",
        "pick cop",
        "pick op",
        "step it cop",
        "kick it cop",
        "push it cop",
        "crank it cop",
        "rev it cop",
        "boost it cop",
    ],

    "SLOW_DOWN": [
        "slow down", "slow up", "decelerate", "reduce speed", "decrease speed",
        "slower", "go slower", "move slower", "take it slow", "easy",
        "take it easy", "ease up", "ease off", "ease off the throttle",
        "throttle down", "throttle back", "back off the throttle",
        "reduce pace", "lower speed", "calm down", "chill",
        "chill out", "cool it", "cool down", "dial it back",
        "tone it down", "bring it down", "bring it back",
        "not so fast", "too fast", "you are going too fast",
        "going too fast", "slow it down", "slow it up",
        "drop your speed", "cut your speed", "cut speed",
        "more slowly", "go gently", "gentle", "be gentle",
        "take it easy please", "slow down please",
        "reduce your speed", "reduce your pace",
        "go at a slower pace", "move at a slower pace",
        "cruise", "cruise along", "cruise control",
        "maintain a slow pace", "hold back a little",
        "hold back", "hold back the speed",
        # Accounting for Ghanaian phrases
        "slow down small", "reduce speed small", "easy easy",
        "go slow small small", "take am slow", "make it slow",
        "let it slow down", "chill small", "ease small",
        "don't go too fast", "small small", "go small small",
        "drive small small", "move small small",
        "chale slow down", "ei slow down",
        # Accounting for wrong pronunciations
        "slow town",
        "slow drown",
        "slow gown",
        "slow crown",
        "slow brown",
        "slow down a bit",
        "slow down a little",
        "sloe down",
        "sloe town",
        "sloe drown",
        "de celerate",
        "de-celerate",
        "de-cell-erate",
        "de cell rate",
        "d-celerate",
        "ease cop",
        "ease op",
        "throttle town",
        "throttle drown",
        "throttle gown",
        "back off the throttle please",
        "dial it beck",
        "dial it bag",
        "bring it beck",
        "tone it town",
        "tone it drown",
        "not so fester",
        "not so foster",
        "too fester",
        "cool town",
        "cool drown",
        "calm town",
        "calm drown",
        "chill town",
        "chill drown",
        "go gently please",
        "be gen tle",
        "cruise along please",
        "hold beck",
        "hold bag",
        "cut your speed please",
    ],

    # For Navigation
    "NAV_DOOR": [
        "go to the door", "drive to the door", "navigate to the door",
        "head to the door", "move to the door", "take me to the door",
        "find the door", "locate the door", "go towards the door",
        "go to the first door", "drive to the first door", "navigate to the first door",
        "head to the first door", "move to the first door", "take me to the first door",
        "find the first door", "locate the first door", "go towards the first door",
        "approach the door", "make your way to the door", "go near the door",
        "get to the door", "reach the door", "go by the door",
        "head over to the door", "move towards the door", "go through the door",
        "exit through the door", "go to the entrance", "go to the exit",
        "find the exit", "go to the doorway", "move to the doorway",
        # Ghanaian natural phrasing
        "go to door", "move to door", "take it to the door",
        "chale go to the door", "go enter the door", "go reach the door",
        "go check the door",
        # accounting for wrong pronunciations
        "go to the draw",
        "go to the daw",
        "go to the doe",
        "go to the dour",
        "head to the draw",
        "move to the draw",
        "find the draw",
        "go to the door way",
        "go to the entrance way",
        "go to the door please",
        "navigate to the draw",
    ],

    "NAV_SECOND_DOOR": [
        "go to the second door", "drive to the second door", "navigate to the second door",
        "head to the second door", "move to the second door", "take me to the second door",
        "find the second door", "locate the second door", "go towards the second door",
        "approach the second door", "make your way to the second door", "go near the second door",
        "get to the second door", "reach the second door", "go by the second door",
        "head over to the second door", "move towards the second door", "go through the second door",
        "exit through the second door", "go to the entrance", "go to the exit",
        "find the exit", "go to the second doorway", "move to the second doorway",
        # Ghanaian natural phrasing
        "go to second door", "move to second door", "take it to the second door",
        "chale go to the second door", "go enter the second door", "go reach the second door",
        "go check the second door",
        # accounting for wrong pronunciations
        "go to the second draw",
        "go to the second daw",
        "go to the second doe",
        "head to the second draw",
        "move to the second draw",
        "find the second draw",
        "go to the sekond door",
        "go to the sec door",
        "navigate to the second draw",
    ],

    "NAV_TABLE": [
        "go to the table", "drive to the table", "navigate to the table",
        "head to the table", "move to the table", "find the table",
        "locate the table", "go towards the table", "approach the table",
        "make your way to the table", "go near the table",
        "get to the table", "reach the table", "go by the table",
        "head over to the table", "move towards the table",
        "go to the nearest table", "find a table",
        # Ghanaian natural phrasing
        "go to table", "go check the table", "go reach the table",
        "take it to the table", "chale go to the table",
        "go to that table", "go near that table",
        # accounting for wrong pronunciations
        "go to the tabel",
        "go to the tayble",
        "go to the cable",
        "go to the stable",
        "head to the cable",
        "move to the cable",
        "find the cable",
        "go to the table",
        "navigate to the tabel",
    ],

    "NAV_DESK": [
        "go to the desk", "drive to the desk", "navigate to the desk",
        "head to the desk", "move to the desk", "find the desk",
        "locate the desk", "go towards the desk", "approach the desk",
        "make your way to the desk", "go near the desk",
        "get to the desk", "reach the desk", "go by the desk",
        "go to the lectern", "drive to the lectern", "navigate to the lectern",
        "head to the lectern", "move to the lectern", "find the lectern",
        "locate the lectern", "go towards the lectern", "approach the lectern",
        "go to the teacher's table", "drive to the teacher's table", "navigate to the teacher's table",
        "head to the teacher's table", "move to the teacher's table", "find the teacher's table",
        "locate the teacher's table", "go towards the teacher's table", "approach the teacher's table",
        "head over to the desk", "move towards the desk",
        "go to the teacher's desk", "go to the workstation",
        "move to the workstation", "navigate to the workstation",
        # Ghanaian natural phrasing
        "go to desk", "go check the desk", "go reach the desk",
        "take it to the desk", "chale go to the desk",
        "go to that desk", "move to that desk",
        # accounting for wrong pronunciations
        "go to the disk",
        "go to the disc",
        "go to the dusk",
        "go to the des",
        "head to the disk",
        "move to the disk",
        "find the disk",
        "navigate to the disk",
        "go to the lec turn",
        "go to the lec tern",
        "go to the lecture",
        "go to the lectern please",
        "go to the teachers table",
        "go to the teachers desk",
        "go to the work station",
    ],

    "NAV_BASE": [
        "go to the base", "drive to the base", "return to base",
        "head back to base", "go home", "return home", "go back to base",
        "navigate to base", "head to home position", "go to start",
        "return to start", "go back to start", "return to starting position",
        "go back to the beginning", "reset position", "go to origin",
        "return to origin", "drive home", "navigate home",
        "come back to base", "head home", "get back to base",
        "return to your spot", "go back to where you started",
        # Ghanaian natural phrasing
        "go home now", "return go base", "chale go back to base",
        "go back to your place", "go to your position",
        "go back home", "go back small", "return small",
        # accounting for wrong pronunciations
        "go to the bass",
        "go to the base",
        "return to bass",
        "go back to bass",
        "head back to bass",
        "go to the based",
        "go to home",
        "go to the home",
        "go to home base",
        "go to home position",
        "return to home",
        "return to home position",
        "go to the origin",
        "go to or again",
        "go to or i gin",
        "reset the position",
    ],

    # Irrelevant language (no actions)
    "UNKNOWN": [
        "what is your name",
        "how are you",
        "tell me a joke",
        "what time is it",
        "i like pizza",
        "who created you",
        "do you sleep",
        "what is your favorite color",
        "sing a song",
        "open youtube",
        "what can you do",
        "how do you work",
        "are you smart",
        "do you know me",
        "what is the weather",
        "who is your owner",
        "can you talk",
        "are you alive",
        "do you have feelings",
        "what is your purpose",
        "can you cook",
        "where are you from",
        "how old are you",
        "do you have a brain",
        "can you fly",
        "tell me something interesting",
        "what is two plus two",
        "who won the match",
        "play some music",
        "call my friend",
        "i am tired",
        "this is boring",
        "you are funny",
        "can you dance",
        "do a backflip",
        "what is happening",
        "nothing is happening",
        "i don't know what to do",
        "are you ready",
        "how far",
        "chale what is up",
        "ei you dey here",
        "make you talk",
        "what you fit do",
        "you sabi",
        "abeg explain yourself",
        "who be you sef",
        "tell me something",
        "you dey craze",
        "mehn this thing is cool",
        "herh nice robot",
    ],
}

prefixes = [
    "please", "robot", "can you", "hey robot", "kindly", "uhm", "uh", "just",
    "hey", "yo", "ok robot", "alright", "could you", "would you", "i need you to",
    "i want you to", "go ahead and", "try to", "make sure you", "quickly",
    "slowly", "carefully", "now", "immediately",
    # Ghanaian prefixes
    "chale", "ei robot", "herh", "abeg", "my guy", "oya", "oya robot",
    "mehn", "guy", "bros", "boss", "make you",
]

suffixes = [
    "now", "a bit", "please", "quickly", "slowly", "actually",
    "right now", "immediately", "at once", "for me", "a little",
    "a little bit", "gently", "carefully", "fast", "asap",
    # Ghanaian suffixes
    "small", "small small", "dey there", "make we go", "abeg",
    "chale", "sharp sharp", "like that", "sef",
]

fillers = [
    "like", "maybe", "sort of", "well", "basically",
    "you know", "i mean", "kind of", "actually", "literally",
    "just", "simply", "really", "honestly",
    # Ghanaian fillers
    "chale", "erm", "ei", "herh", "so", "then", "abi",
]

# Data preprocessing


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

# Injecting noise to make the model more realistic


def inject_noise(phrase):
    words = phrase.split()
    if random.random() < 0.6:
        words.insert(random.randint(0, len(words)), random.choice(fillers))
    if random.random() < 0.3 and len(words) > 1:
        words.pop(random.randint(0, len(words)-1))
    return " ".join(words)


# Data Augmentation
expanded_data = {}
for intent, phrases in data.items():
    expanded = set()

    for p in phrases:
        p = clean_text(p)
        expanded.add(p)

        for pre in prefixes:
            expanded.add(clean_text(f"{pre} {p}"))

        for suf in suffixes:
            expanded.add(clean_text(f"{p} {suf}"))

        for _ in range(6):
            noisy = clean_text(inject_noise(p))
            expanded.add(noisy)
            expanded.add(clean_text(f"{random.choice(prefixes)} {noisy}"))

    expanded_data[intent] = list(expanded)

# Flattening the dataset into x and y
X = []
y = []

for intent, phrases in expanded_data.items():
    for phrase in phrases:
        X.append(phrase)
        y.append(intent)

X, y = shuffle(X, y, random_state=42)
print(f"Dataset size: {len(X)} samples")

# Splitting into the test set and the training set
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# The model pipeline
model = make_pipeline(
    TfidfVectorizer(
        ngram_range=(1, 2),
        lowercase=True,
        min_df=1,
        max_df=0.9,
    ),
    CalibratedClassifierCV(LinearSVC(C=0.8, dual="auto"))
)

# Performing Cross Validation
print("\nRunning Cross Validation...")
scores = cross_val_score(model, X, y, cv=5)
print("Average CV accuracy:", scores.mean())

# Training the model
print("\nTraining Intent Classifier...")
model.fit(X_train, y_train)

# Evaluating the model
y_pred = model.predict(X_test)
accuracy = metrics.accuracy_score(y_test, y_pred)

print(f"\nTest Accuracy: {accuracy * 100:.2f}%\n")
print("Classification Report:")
print(metrics.classification_report(y_test, y_pred))

# Performing stress tests with some phrases
test_phrases = [
    "uhm robot please navigate to the cupboard",
    "hey robot maybe go home",
    "what is your favorite color",
    "just stop please",
    "robot head to the door quickly",
    "can you dance for me",
    "tell me something funny",
    # Ghanaian natural phrasing stress tests
    "chale move forward small",
    "oya go to the table",
    "abeg stop the thing",
    "herh go back to base",
    "ei robot go left small small",
    "my guy reverse small",
    "boss go to the door make we see",
    "chale what is up",
    "how far robot",
    "make you go right sharp sharp",
    "go forward small small for me",
    "oya turn left small",
]

print("\nStress Test Results:")
CONFIDENCE_THRESHOLD = 0.80

for phrase in test_phrases:
    cleaned = clean_text(phrase)

    probabilities = model.predict_proba([cleaned])
    confidence = probabilities.max()
    pred = model.predict([cleaned])[0]

    # Decision logic by comparing to a set confidence threshold
    if pred == "UNKNOWN" or confidence < CONFIDENCE_THRESHOLD:
        print(f"'{phrase}' -> IGNORE (intent=UNKNOWN, confidence={confidence:.2f})")
    else:
        print(f"'{phrase}' -> {pred} (confidence={confidence:.2f})")

# Saving the model as a.pkl file
joblib.dump(model, "intent_model.pkl")
print("\nModel exported as 'intent_model.pkl'")
