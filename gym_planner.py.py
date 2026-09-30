"""
PERSONALIZED GYM PLANNER
A rule-based program that builds a weekly gym timetable and workout plan
from the user's goal, experience, schedule, time, and equipment.
Uses only the Python standard library.
"""

# CONSTANTS (fixed data used by many functions)


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

EXPERIENCE_OPTIONS = ["Beginner", "Intermediate", "Advanced"]
LEVELS = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}

GOAL_OPTIONS = ["Muscle Gain", "Fat Loss", "Strength", "Endurance", "General Fitness"]

TIME_OPTIONS = ["Early Morning", "Morning", "Afternoon", "Evening", "Night", "No Preference"]
TIME_VALUES = ["6:30 AM", "9:00 AM", "2:00 PM", "6:00 PM", "8:30 PM", "6:00 PM"]

DURATION_OPTIONS = ["30 minutes", "45 minutes", "60 minutes", "90 minutes"]
DURATION_VALUES =  [30, 45, 60, 90]

# Menu text (with a short description) and the short names used in the plan
EQUIPMENT_MENU = [
                   "Full Gym (machines, cables, free weights)",
                   "Dumbbells + Bench",
                   "Basic Gym Equipment (barbell, dumbbells, bench, pull-up bar, treadmill/bike)",
                   "Bodyweight Only (no equipment)",
                  ]
EQUIPMENT_NAMES = ["Full Gym", "Dumbbells + Bench", "Basic Gym Equipment", "Bodyweight Only"]
EQUIPMENT_KEYS = ["full", "dumbbells", "basic", "bodyweight"]

# Each equipment level includes everything from the levels below it.
# An exercise is allowed if its required level <= the user's level.
EQUIPMENT_RANK = {"bodyweight": 1, "dumbbells": 2, "basic": 3, "full": 4}

# Sets depend on experience
COMPOUND_SETS = {"Beginner": 3, "Intermediate": 3, "Advanced": 4}
ISOLATION_SETS = {"Beginner": 2, "Intermediate": 3, "Advanced": 3}

# Reps and rest depend on the goal
GOAL_SETTINGS = {
    "Muscle Gain": {
        "compound_reps": "8-10", "compound_rest": "90 seconds",
        "isolation_reps": "10-15", "isolation_rest": "60 seconds",
    },
    "Strength": {
        "compound_reps": "4-6", "compound_rest": "2-3 minutes",
        "isolation_reps": "8-10", "isolation_rest": "90 seconds",
    },
    "Fat Loss": {
        "compound_reps": "10-12", "compound_rest": "45-60 seconds",
        "isolation_reps": "12-15", "isolation_rest": "45 seconds",
    },
    "Endurance": {
        "compound_reps": "12-15", "compound_rest": "30-45 seconds",
        "isolation_reps": "15-20", "isolation_rest": "30 seconds",
    },
    "General Fitness": {
        "compound_reps": "8-12", "compound_rest": "60 seconds",
        "isolation_reps": "10-15", "isolation_rest": "45-60 seconds",
    },
}

CARDIO_PACE = {
    "Muscle Gain": "easy pace",
    "Strength": "easy pace",
    "Fat Loss": "moderate pace",
    "Endurance": "steady pace",
    "General Fitness": "comfortable pace",
}

# Maximum training days per week (more days than this = less recovery)
MAX_TRAINING_DAYS = {"Beginner": 4, "Intermediate": 5, "Advanced": 6}

# Each workout is a list of muscle "slots". The generator goes through the
# slots in order until it has enough exercises for the chosen duration.
# (quads + hamstrings + calves together make up the legs)
TEMPLATES = {
    "Full Body A": ["quads", "chest", "back", "shoulders", "hamstrings", "core", "triceps", "biceps", "calves", "core"],
    "Full Body B": ["hamstrings", "back", "chest", "quads", "shoulders", "core", "biceps", "triceps", "calves", "core"],
    "Full Body C": ["quads", "back", "chest", "hamstrings", "shoulders", "core", "biceps", "calves", "triceps", "core"],
    "Upper Body A": ["chest", "back", "shoulders", "triceps", "biceps", "chest", "back", "shoulders", "triceps", "biceps"],
    "Upper Body B": ["back", "chest", "shoulders", "biceps", "triceps", "back", "chest", "core", "shoulders", "biceps"],
    "Lower Body A": ["quads", "hamstrings", "quads", "calves", "hamstrings", "core", "calves", "core", "quads", "hamstrings"],
    "Lower Body B": ["hamstrings", "quads", "hamstrings", "calves", "quads", "core", "calves", "core", "hamstrings", "quads"],
    "Push": ["chest", "shoulders", "chest", "triceps", "shoulders", "triceps", "chest", "core", "shoulders", "triceps"],
    "Pull": ["back", "back", "biceps", "back", "biceps", "core", "back", "core", "biceps", "back"],
    "Legs": ["quads", "hamstrings", "quads", "calves", "hamstrings", "core", "calves", "quads", "hamstrings", "core"],
}


# ------------------------------------------------------------------
# INPUT HELPERS
# ------------------------------------------------------------------

def ask(prompt):
    """Read one answer from the user."""
    return input(prompt).strip()


def get_choice(title, options):
    """Show a numbered menu and return the chosen index (starting at 0)."""
    print("\n" + title)
    number = 1
    for option in options:
        print("  " + str(number) + ". " + option)
        number += 1

    while True:
        text = ask("Enter your choice (1-" + str(len(options)) + "): ")
        if not text.isdigit():
            print("Please enter a number, not text.")
            continue
        number = int(text)
        if 1 <= number <= len(options):
            return number - 1
        print("That number is not in the menu. Try again.")


# ------------------------------------------------------------------
# BLOCK 1 - USER PROFILE
# ------------------------------------------------------------------

def get_user_profile():
    while True:
        name = ask("Enter your name: ")
        if name == "":
            print("Name cannot be empty.")
        elif len(name) > 30:
            print("Please use a shorter name (30 characters or less).")
        else:
            break

    while True:
        text = ask("Enter your age: ")
        if not text.isdigit():
            print("Please enter your age as a whole number, like 18.")
            continue
        age = int(text)
        if age < 14 or age > 80:
            print("This planner is meant for ages 14 to 80. Please enter a valid age.")
        else:
            break

    index = get_choice("What is your experience level?", EXPERIENCE_OPTIONS)
    experience = EXPERIENCE_OPTIONS[index]
    return name, age, experience


# ------------------------------------------------------------------
# BLOCKS 2-6 - GOAL, TIME, DAYS, DURATION, EQUIPMENT
# ------------------------------------------------------------------

def get_goal():
    index = get_choice("What is your main fitness goal?", GOAL_OPTIONS)
    return GOAL_OPTIONS[index]


def get_time_preference():
    index = get_choice("When do you prefer to work out?", TIME_OPTIONS)
    return TIME_OPTIONS[index], TIME_VALUES[index]


def get_available_days():
    print("\nWhich days can you work out?")
    number = 1
    for day in DAYS:
        print("  " + str(number) + ". " + day)
        number += 1
    print("Type the day numbers separated by spaces, for example: 1 3 5")

    while True:
        text = ask("Your days (choose at least 2): ")
        text = text.replace(",", " ")
        parts = text.split()

        chosen = []
        all_valid = True
        for part in parts:
            if not part.isdigit():
                all_valid = False
                continue
            number = int(part)
            if number < 1 or number > 7:
                all_valid = False
            elif number not in chosen:
                chosen.append(number)  # repeated numbers are ignored

        if not all_valid or len(parts) == 0:
            print("Invalid entry. Use only the numbers 1 to 7, like: 1 3 5")
        elif len(chosen) < 2:
            print("Please choose at least 2 different days.")
        else:
            chosen.sort()
            days = []
            for number in chosen:
                days.append(DAYS[number - 1])
            return days


def get_duration():
    index = get_choice("How much time do you have per workout?", DURATION_OPTIONS)
    return DURATION_VALUES[index]


def get_equipment():
    index = get_choice("What equipment do you have access to?", EQUIPMENT_MENU)
    return EQUIPMENT_KEYS[index], EQUIPMENT_NAMES[index]


# ------------------------------------------------------------------
# BLOCK 7 - EXERCISE DATABASE
# ------------------------------------------------------------------

def add_exercise(database, name, muscle, equipment, difficulty, kind, timed=False):
    """equipment = minimum setup needed, difficulty 1/2/3 = beginner/intermediate/advanced,
    kind = compound or isolation (or cardio), timed = measured in seconds instead of reps."""
    exercise = {
        "name": name,
        "muscle": muscle,
        "equipment": equipment,
        "difficulty": difficulty,
        "kind": kind,
        "timed": timed,
    }
    database.append(exercise)


def create_exercise_database():
    db = []

    # CHEST
    add_exercise(db, "Push-Up", "chest", "bodyweight", 1, "compound")
    add_exercise(db, "Incline Push-Up (hands on bench or table)", "chest", "bodyweight", 1, "compound")
    add_exercise(db, "Decline Push-Up (feet raised)", "chest", "bodyweight", 2, "compound")
    add_exercise(db, "Archer Push-Up", "chest", "bodyweight", 3, "compound")
    add_exercise(db, "Dumbbell Bench Press", "chest", "dumbbells", 1, "compound")
    add_exercise(db, "Incline Dumbbell Press", "chest", "dumbbells", 2, "compound")
    add_exercise(db, "Dumbbell Fly", "chest", "dumbbells", 2, "isolation")
    add_exercise(db, "Barbell Bench Press", "chest", "basic", 2, "compound")
    add_exercise(db, "Incline Barbell Bench Press", "chest", "basic", 2, "compound")
    add_exercise(db, "Machine Chest Press", "chest", "full", 1, "compound")
    add_exercise(db, "Cable Fly", "chest", "full", 2, "isolation")

    # BACK
    add_exercise(db, "Superman Hold", "back", "bodyweight", 1, "isolation")
    add_exercise(db, "Reverse Snow Angel", "back", "bodyweight", 1, "isolation")
    add_exercise(db, "Inverted Row (under a sturdy table)", "back", "bodyweight", 2, "compound")
    add_exercise(db, "Feet-Elevated Inverted Row", "back", "bodyweight", 3, "compound")
    add_exercise(db, "One-Arm Dumbbell Row", "back", "dumbbells", 1, "compound")
    add_exercise(db, "Chest-Supported Dumbbell Row", "back", "dumbbells", 2, "compound")
    add_exercise(db, "Barbell Row", "back", "basic", 2, "compound")
    add_exercise(db, "Pull-Up", "back", "basic", 3, "compound")
    add_exercise(db, "Chin-Up", "back", "basic", 3, "compound")
    add_exercise(db, "Deadlift", "back", "basic", 3, "compound")
    add_exercise(db, "Lat Pulldown", "back", "full", 1, "compound")
    add_exercise(db, "Seated Cable Row", "back", "full", 1, "compound")
    add_exercise(db, "Machine Row", "back", "full", 1, "compound")

    # SHOULDERS
    add_exercise(db, "Plank Shoulder Taps", "shoulders", "bodyweight", 1, "isolation")
    add_exercise(db, "Wall Angels", "shoulders", "bodyweight", 1, "isolation")
    add_exercise(db, "Pike Push-Up", "shoulders", "bodyweight", 2, "compound")
    add_exercise(db, "Elevated Pike Push-Up", "shoulders", "bodyweight", 3, "compound")
    add_exercise(db, "Dumbbell Shoulder Press", "shoulders", "dumbbells", 1, "compound")
    add_exercise(db, "Dumbbell Lateral Raise", "shoulders", "dumbbells", 1, "isolation")
    add_exercise(db, "Arnold Press", "shoulders", "dumbbells", 2, "compound")
    add_exercise(db, "Bent-Over Dumbbell Rear Raise", "shoulders", "dumbbells", 2, "isolation")
    add_exercise(db, "Barbell Overhead Press", "shoulders", "basic", 2, "compound")
    add_exercise(db, "Machine Shoulder Press", "shoulders", "full", 1, "compound")
    add_exercise(db, "Cable Lateral Raise", "shoulders", "full", 2, "isolation")
    add_exercise(db, "Face Pull", "shoulders", "full", 2, "isolation")

    # BICEPS
    add_exercise(db, "Backpack Curl (loaded backpack)", "biceps", "bodyweight", 1, "isolation")
    add_exercise(db, "Towel Isometric Curl", "biceps", "bodyweight", 1, "isolation")
    add_exercise(db, "Underhand Inverted Row", "biceps", "bodyweight", 2, "compound")
    add_exercise(db, "Dumbbell Bicep Curl", "biceps", "dumbbells", 1, "isolation")
    add_exercise(db, "Hammer Curl", "biceps", "dumbbells", 1, "isolation")
    add_exercise(db, "Incline Dumbbell Curl", "biceps", "dumbbells", 2, "isolation")
    add_exercise(db, "Concentration Curl", "biceps", "dumbbells", 2, "isolation")
    add_exercise(db, "Barbell Curl", "biceps", "basic", 1, "isolation")
    add_exercise(db, "Cable Curl", "biceps", "full", 1, "isolation")
    add_exercise(db, "Preacher Curl Machine", "biceps", "full", 2, "isolation")

    # TRICEPS
    add_exercise(db, "Bench Dip (chair or bench)", "triceps", "bodyweight", 1, "isolation")
    add_exercise(db, "Diamond Push-Up", "triceps", "bodyweight", 2, "compound")
    add_exercise(db, "Bodyweight Triceps Extension", "triceps", "bodyweight", 3, "isolation")
    add_exercise(db, "Overhead Dumbbell Triceps Extension", "triceps", "dumbbells", 1, "isolation")
    add_exercise(db, "Dumbbell Kickback", "triceps", "dumbbells", 1, "isolation")
    add_exercise(db, "Dumbbell Skull Crusher", "triceps", "dumbbells", 2, "isolation")
    add_exercise(db, "Close-Grip Bench Press", "triceps", "basic", 2, "compound")
    add_exercise(db, "Cable Triceps Pushdown", "triceps", "full", 1, "isolation")
    add_exercise(db, "Overhead Cable Triceps Extension", "triceps", "full", 2, "isolation")

    # LEGS - quads
    add_exercise(db, "Bodyweight Squat", "quads", "bodyweight", 1, "compound")
    add_exercise(db, "Reverse Lunge", "quads", "bodyweight", 1, "compound")
    add_exercise(db, "Step-Up (sturdy step or bench)", "quads", "bodyweight", 1, "compound")
    add_exercise(db, "Bulgarian Split Squat", "quads", "bodyweight", 2, "compound")
    add_exercise(db, "Jump Squat", "quads", "bodyweight", 2, "compound")
    add_exercise(db, "Pistol Squat (to a bench)", "quads", "bodyweight", 3, "compound")
    add_exercise(db, "Goblet Squat", "quads", "dumbbells", 1, "compound")
    add_exercise(db, "Dumbbell Lunge", "quads", "dumbbells", 1, "compound")
    add_exercise(db, "Dumbbell Bulgarian Split Squat", "quads", "dumbbells", 2, "compound")
    add_exercise(db, "Barbell Back Squat", "quads", "basic", 2, "compound")
    add_exercise(db, "Front Squat", "quads", "basic", 3, "compound")
    add_exercise(db, "Leg Press", "quads", "full", 1, "compound")
    add_exercise(db, "Leg Extension", "quads", "full", 1, "isolation")

    # LEGS - hamstrings and glutes
    add_exercise(db, "Glute Bridge", "hamstrings", "bodyweight", 1, "isolation")
    add_exercise(db, "Good Morning (bodyweight hip hinge)", "hamstrings", "bodyweight", 1, "isolation")
    add_exercise(db, "Single-Leg Glute Bridge", "hamstrings", "bodyweight", 2, "isolation")
    add_exercise(db, "Single-Leg Romanian Deadlift (bodyweight)", "hamstrings", "bodyweight", 3, "compound")
    add_exercise(db, "Dumbbell Romanian Deadlift", "hamstrings", "dumbbells", 1, "compound")
    add_exercise(db, "Weighted Glute Bridge (dumbbell)", "hamstrings", "dumbbells", 1, "isolation")
    add_exercise(db, "Dumbbell Single-Leg Romanian Deadlift", "hamstrings", "dumbbells", 2, "compound")
    add_exercise(db, "Barbell Romanian Deadlift", "hamstrings", "basic", 2, "compound")
    add_exercise(db, "Barbell Hip Thrust", "hamstrings", "basic", 2, "compound")
    add_exercise(db, "Lying Leg Curl", "hamstrings", "full", 1, "isolation")
    add_exercise(db, "Seated Leg Curl", "hamstrings", "full", 1, "isolation")
    add_exercise(db, "Cable Pull-Through", "hamstrings", "full", 2, "compound")

    # LEGS - calves
    add_exercise(db, "Standing Calf Raise (bodyweight)", "calves", "bodyweight", 1, "isolation")
    add_exercise(db, "Single-Leg Calf Raise", "calves", "bodyweight", 2, "isolation")
    add_exercise(db, "Dumbbell Calf Raise", "calves", "dumbbells", 1, "isolation")
    add_exercise(db, "Machine Calf Raise", "calves", "full", 1, "isolation")

    # CORE
    add_exercise(db, "Plank", "core", "bodyweight", 1, "isolation", True)
    add_exercise(db, "Dead Bug", "core", "bodyweight", 1, "isolation")
    add_exercise(db, "Crunch", "core", "bodyweight", 1, "isolation")
    add_exercise(db, "Bicycle Crunch", "core", "bodyweight", 1, "isolation")
    add_exercise(db, "Side Plank", "core", "bodyweight", 2, "isolation", True)
    add_exercise(db, "Lying Leg Raise", "core", "bodyweight", 2, "isolation")
    add_exercise(db, "Mountain Climbers", "core", "bodyweight", 2, "isolation")
    add_exercise(db, "Weighted Russian Twist (dumbbell)", "core", "dumbbells", 2, "isolation")
    add_exercise(db, "Hanging Leg Raise", "core", "basic", 3, "isolation")
    add_exercise(db, "Cable Crunch", "core", "full", 2, "isolation")

    # CARDIO
    add_exercise(db, "Brisk Walk", "cardio", "bodyweight", 1, "cardio")
    add_exercise(db, "Jumping Jacks", "cardio", "bodyweight", 1, "cardio")
    add_exercise(db, "Shadow Boxing", "cardio", "bodyweight", 1, "cardio")
    add_exercise(db, "Easy Jog", "cardio", "bodyweight", 2, "cardio")
    add_exercise(db, "High Knees", "cardio", "bodyweight", 2, "cardio")
    add_exercise(db, "Burpees", "cardio", "bodyweight", 3, "cardio")
    add_exercise(db, "Treadmill Walk or Jog", "cardio", "basic", 1, "cardio")
    add_exercise(db, "Stationary Bike", "cardio", "basic", 1, "cardio")
    add_exercise(db, "Elliptical", "cardio", "full", 1, "cardio")
    add_exercise(db, "Rowing Machine", "cardio", "full", 2, "cardio")
    add_exercise(db, "Stair Climber", "cardio", "full", 2, "cardio")

    return db


# ------------------------------------------------------------------
# BLOCK 8 - WORKOUT SPLIT GENERATOR
# ------------------------------------------------------------------

def limit_training_days(days, experience):
    """Too many training days = not enough recovery. If the user picked more days
    than is sensible for their level, keep evenly spread days from their choice."""
    limit = MAX_TRAINING_DAYS[experience]
    if len(days) <= limit:
        return days

    # Spread the kept days across the user's full selection, including its ends.
    kept_days = []
    last_index = len(days) - 1
    for i in range(limit):
        # Integer division keeps the selection evenly spaced.
        index = (i * last_index + (limit - 1) // 2) // (limit - 1)
        kept_days.append(days[index])
    return kept_days


def generate_split(num_days, goal):
    if num_days == 2:
        return ["Full Body A", "Full Body B"]
    elif num_days == 3:
        return ["Full Body A", "Full Body B", "Full Body C"]
    elif num_days == 4:
        return ["Upper Body A", "Lower Body A", "Upper Body B", "Lower Body B"]
    elif num_days == 5:
        if goal == "Endurance":
            return ["Full Body A", "Cardio + Core", "Full Body B", "Cardio + Core", "Full Body C"]
        return ["Push", "Pull", "Legs", "Upper Body A", "Lower Body A"]
    else:
        # 6 days
        if goal == "Endurance":
            return ["Full Body A", "Cardio + Core", "Full Body B", "Cardio + Core", "Full Body C", "Cardio + Core"]
        return ["Push", "Pull", "Legs", "Push", "Pull", "Legs"]


# ------------------------------------------------------------------
# BLOCK 9 - PERSONALIZED WORKOUT GENERATOR
# ------------------------------------------------------------------

def get_allowed_exercises(database, muscle, user):
    """All exercises for a muscle that match the user's equipment and experience.
    Harder exercises (that the user is allowed to do) come first."""
    my_level = LEVELS[user["experience"]]
    my_rank = EQUIPMENT_RANK[user["equipment"]]

    allowed = [exercise for exercise in database
               if exercise["muscle"] == muscle
               and exercise["difficulty"] <= my_level
               and EQUIPMENT_RANK[exercise["equipment"]] <= my_rank]
    # Show the most challenging suitable options first.
    return sorted(allowed, key=lambda exercise: exercise["difficulty"], reverse=True)


def pick_exercise(database, muscle, user, used_in_workout, times_used):
    """Choose an exercise for a muscle. Exercises used less often this week are
    preferred, so different days get different exercises."""
    choices = [exercise for exercise in get_allowed_exercises(database, muscle, user)
               if exercise["name"] not in used_in_workout]
    best = min(choices, key=lambda exercise: times_used.get(exercise["name"], 0), default=None)

    if best is not None:
        used_in_workout.append(best["name"])
        times_used[best["name"]] = times_used.get(best["name"], 0) + 1
    return best


def get_exercise_count(duration, experience):
    counts = {30: 4, 45: 5, 60: 6, 90: 8}
    count = counts[duration]
    if experience == "Beginner":
        return min(count, 7)
    return count


def get_cardio_minutes(goal, duration):
    base = {"Muscle Gain": 0, "Strength": 0, "Fat Loss": 15, "Endurance": 20, "General Fitness": 10}
    minutes = base[goal]
    if minutes == 0:
        return 0
    if duration == 30:
        return 10
    if duration == 90:
        return minutes + 10
    return minutes


def make_item(exercise, user):
    """Turn an exercise into a workout entry with sets, reps and rest."""
    goal = user["goal"]
    level = user["experience"]
    settings = GOAL_SETTINGS[goal]

    if exercise["kind"] == "compound":
        sets = COMPOUND_SETS[level]
        reps = settings["compound_reps"]
        rest = settings["compound_rest"]
        if goal == "Strength" and level == "Beginner":
            reps = "6-8"
        if goal == "Strength" and user["equipment"] == "bodyweight":
            reps = "6-10"  # bodyweight moves are hard to load heavily
    else:
        sets = ISOLATION_SETS[level]
        reps = settings["isolation_reps"]
        rest = settings["isolation_rest"]

    if exercise["muscle"] == "core":
        reps = "12-15"
        if goal == "Endurance":
            reps = "15-20"
        rest = "45 seconds"

    if exercise["timed"]:
        if level == "Beginner":
            reps = "20-30 seconds"
        elif level == "Intermediate":
            reps = "30-45 seconds"
        else:
            reps = "45-60 seconds"

    item = {
        "name": exercise["name"],
        "muscle": exercise["muscle"],
        "sets": sets,
        "reps": reps,
        "rest": rest,
    }
    return item


def make_cardio_item(exercise, user, minutes):
    if user["experience"] == "Beginner":
        pace = "easy pace"
    else:
        pace = CARDIO_PACE[user["goal"]]
    item = {
        "name": exercise["name"],
        "muscle": "cardio",
        "sets": 1,
        "reps": str(minutes) + " minutes, " + pace,
        "rest": "",
    }
    return item


def generate_cardio_day(user, database, times_used):
    """Cardio + Core day (used in the Endurance plan for 5+ days)."""
    duration = user["duration"]
    core_count = {30: 2, 45: 3, 60: 3, 90: 4}[duration]
    blocks = {30: 1, 45: 2, 60: 2, 90: 3}[duration]
    block_minutes = (duration - 5 - 3 * core_count) // blocks // 5 * 5

    workout = []
    used_in_workout = []

    for i in range(blocks):
        exercise = pick_exercise(database, "cardio", user, used_in_workout, times_used)
        if exercise is not None:
            workout.append(make_cardio_item(exercise, user, block_minutes))

    for i in range(core_count):
        exercise = pick_exercise(database, "core", user, used_in_workout, times_used)
        if exercise is not None:
            workout.append(make_item(exercise, user))

    return workout


def generate_workout(session_name, user, database, times_used):
    if session_name == "Cardio + Core":
        return generate_cardio_day(user, database, times_used)

    template = TEMPLATES[session_name]
    count = get_exercise_count(user["duration"], user["experience"])

    workout = []
    used_in_workout = []

    for muscle in template:
        if len(workout) >= count:
            break
        exercise = pick_exercise(database, muscle, user, used_in_workout, times_used)
        if exercise is not None:
            workout.append(make_item(exercise, user))

    # Cardio at the end depends on the goal
    minutes = get_cardio_minutes(user["goal"], user["duration"])
    if minutes > 0:
        exercise = pick_exercise(database, "cardio", user, used_in_workout, times_used)
        if exercise is not None:
            workout.append(make_cardio_item(exercise, user, minutes))

    return workout


def build_timetable(user, database):
    """Returns a dictionary: day -> None (rest day) or {"session": ..., "workout": [...]}"""
    split = generate_split(len(user["days"]), user["goal"])

    timetable = {}
    for day in DAYS:
        timetable[day] = None

    times_used = {}
    for i in range(len(split)):
        workout = generate_workout(split[i], user, database, times_used)
        timetable[user["days"][i]] = {"session": split[i], "workout": workout}
    return timetable


# ------------------------------------------------------------------
# BLOCK 10 - MODIFICATION + PROGRESSION
# ------------------------------------------------------------------

def find_alternatives(database, old_item, workout, user):
    names_in_workout = []
    for item in workout:
        names_in_workout.append(item["name"])

    alternatives = []
    for exercise in get_allowed_exercises(database, old_item["muscle"], user):
        if exercise["name"] not in names_in_workout:
            alternatives.append(exercise)
    return alternatives


def modify_workout(timetable, user, database):
    """Lets the user replace exercises. Returns True if anything was changed."""
    changed = False
    question = "Would you like to replace any exercise?"

    while True:
        answer = get_choice(question, ["Yes", "No"])
        if answer == 1:
            return changed
        question = "Would you like to replace another exercise?"

        # Step 1: choose the workout day
        training_days = []
        labels = []
        for day in DAYS:
            if timetable[day] is not None:
                training_days.append(day)
                labels.append(day + " - " + timetable[day]["session"])
        day_index = get_choice("Which workout?", labels)
        workout = timetable[training_days[day_index]]["workout"]

        # Step 2: choose the exercise
        names = []
        for item in workout:
            names.append(item["name"])
        exercise_index = get_choice("Which exercise do you want to replace?", names)
        old_item = workout[exercise_index]

        # Step 3: choose the replacement
        alternatives = find_alternatives(database, old_item, workout, user)
        if len(alternatives) == 0:
            print("\nSorry, there is no other suitable " + old_item["muscle"] + " exercise for your level and equipment.")
            continue

        alt_names = []
        for exercise in alternatives:
            alt_names.append(exercise["name"])
        alt_names.append("Cancel (keep the current exercise)")
        alt_index = get_choice("Replace " + old_item["name"] + " with:", alt_names)
        if alt_index == len(alternatives):
            print("Okay, nothing changed.")
            continue

        new_exercise = alternatives[alt_index]
        if old_item["muscle"] == "cardio":
            old_item["name"] = new_exercise["name"]  # keep the same duration
        else:
            workout[exercise_index] = make_item(new_exercise, user)
        print("Replaced " + names[exercise_index] + " with " + new_exercise["name"] + ".")
        changed = True


def get_progression_tips(user):
    tips = []

    if user["equipment"] == "bodyweight":
        tips.append("When you can complete the top of the rep range on every set with good form, "
                    "make the exercise harder: slow down the lowering part, add a pause, "
                    "or move to a harder variation.")
    else:
        tips.append("When you can comfortably complete the top of the rep range on every set "
                    "with good form, consider slightly increasing the weight next session "
                    "(a small jump of about 2-5%).")

    if user["goal"] == "Muscle Gain":
        tips.append("Aim to add one rep or a little weight over time. Muscle growth also needs "
                    "enough rest and sleep between workouts.")
    elif user["goal"] == "Strength":
        tips.append("Keep the reps low, rest fully between heavy sets, and add weight steadily "
                    "only when your form stays solid.")
    elif user["goal"] == "Fat Loss":
        tips.append("Every 1-2 weeks, add 2-5 minutes to your cardio or shorten your rest "
                    "periods by 5-10 seconds.")
    elif user["goal"] == "Endurance":
        tips.append("Every 1-2 weeks, add about 5 minutes to your cardio or raise the pace "
                    "slightly.")
    else:
        tips.append("Progress gradually. One small improvement per week (a rep, a little "
                    "weight, or a few minutes of cardio) is enough.")

    if user["experience"] == "Beginner":
        tips.append("For the first 2 weeks, use light weights and focus on learning good form.")
    else:
        tips.append("Every 6-8 weeks, take an easier week with lighter weights so your body "
                    "can recover.")

    return tips


# ------------------------------------------------------------------
# BLOCK 11 - FINAL PERSONALIZED TIMETABLE
# ------------------------------------------------------------------

def print_wrapped(text, indent=""):
    words = text.split()
    line = indent
    for word in words:
        if len(line) + len(word) + 1 > 60 and line != indent:
            print(line)
            line = indent + word
        elif line == indent:
            line += word
        else:
            line += " " + word
    print(line)


def display_final_plan(timetable, user):
    double_line = "=" * 50
    single_line = "-" * 50

    print("\n" + double_line)
    print("PERSONALIZED GYM PLAN".center(50))
    print(double_line)
    print("")
    print("Name: " + user["name"])
    print("Age: " + str(user["age"]))
    print("Experience: " + user["experience"])
    print("Goal: " + user["goal"])
    print("Workout Days: " + str(len(user["days"])) + " (" + ", ".join(user["days"]) + ")")
    print("Duration: " + str(user["duration"]) + " minutes")
    print("The selected duration guides exercise and cardio volume; it is not a timer.")
    print("Actual time varies with warm-up, pace, rest, and transitions.")
    if user["time_label"] == "No Preference":
        print("Preferred Time: No preference (" + user["time_text"] + " used)")
    else:
        print("Preferred Time: " + user["time_label"] + " (" + user["time_text"] + ")")
    print("Equipment: " + user["equipment_name"])

    print("\n" + single_line)
    print("WEEKLY TIMETABLE")
    print(single_line)
    for day in DAYS:
        print("\n" + day.upper())
        if timetable[day] is None:
            print("Rest")
        else:
            print(user["time_text"])
            print(timetable[day]["session"])

    print("\n" + single_line)
    print("DETAILED WORKOUTS")
    print(single_line)
    if user["duration"] == 90:
        warmup = "Warm-up: 10 minutes of light cardio and dynamic stretching"
    else:
        warmup = "Warm-up: 5 minutes of light cardio and dynamic stretching"

    for day in DAYS:
        if timetable[day] is None:
            continue
        print("\n" + day.upper() + " - " + timetable[day]["session"].upper())
        print(warmup)
        number = 1
        for item in timetable[day]["workout"]:
            print("\n" + str(number) + ". " + item["name"] + " (" + item["muscle"].title() + ")")
            if item["muscle"] == "cardio":
                print("   " + item["reps"])
            else:
                print("   " + str(item["sets"]) + " sets x " + item["reps"])
                print("   Rest: " + item["rest"])
            number = number + 1

    print("\n" + single_line)
    print("PROGRESSION")
    print(single_line)
    for tip in get_progression_tips(user):
        print_wrapped(tip, "- ")
        print("")

    print(single_line)
    print("NOTE")
    print(single_line)
    note = ("This program provides a general workout plan for educational and planning "
            "purposes. Adjust exercises according to your fitness level and stop if an "
            "exercise causes pain. If you are unsure whether exercise is right for you, "
            "check with a doctor first.")
    print_wrapped(note)
    if user["age"] < 18:
        print("")
        print_wrapped("Since you are under 18, please ask a parent, teacher, or coach to "
                      "supervise you when lifting weights.")
    print(double_line)


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------

def has_back_to_back_days(days):
    if len(days) < 2:
        return False

    # Check each selected day and the next one in the weekly cycle, including Sunday -> Monday.
    selected_days = set(days)
    for day in days:
        day_index = DAYS.index(day)
        next_day = DAYS[(day_index + 1) % len(DAYS)]
        if next_day in selected_days:
            return True
    return False


def main():
    print("=" * 50)
    print("PERSONALIZED GYM PLANNER".center(50))
    print("=" * 50)
    print("Answer a few questions and get a weekly workout plan.")

    database = create_exercise_database()

    name, age, experience = get_user_profile()
    goal = get_goal()
    time_label, time_text = get_time_preference()
    chosen_days = get_available_days()
    duration = get_duration()
    equipment, equipment_name = get_equipment()

    training_days = limit_training_days(chosen_days, experience)
    if len(training_days) < len(chosen_days):
        print("\nYou selected " + str(len(chosen_days)) + " days, but " + str(len(training_days)) +
              " training days is the most we recommend for a " + experience.lower() +
              ", so your body gets enough recovery.")
        print("The other days are kept as rest days.")
    if len(training_days) <= 3 and has_back_to_back_days(training_days):
        print("\nTip: with 2-3 full-body days, try to leave a rest day between workouts.")

    user = {
        "name": name,
        "age": age,
        "experience": experience,
        "goal": goal,
        "time_label": time_label,
        "time_text": time_text,
        "days": training_days,
        "duration": duration,
        "equipment": equipment,
        "equipment_name": equipment_name,
    }

    timetable = build_timetable(user, database)
    display_final_plan(timetable, user)

    changed = modify_workout(timetable, user, database)
    if changed:
        print("\nHere is your updated plan:")
        display_final_plan(timetable, user)

    print("\nGood luck with your training, " + name + "!")


if __name__ == "__main__":
    main()
