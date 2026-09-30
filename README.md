# Personalized Gym Planner

A command-line Python program that creates a weekly gym timetable and workout plan from a user's profile, fitness goal, available days, preferred time, workout duration, and equipment. The plan is rule-based and uses an exercise list included in the program.

## Features

- Collects a name, age (14-80), and experience level (Beginner, Intermediate, or Advanced).
- Offers five goals: Muscle Gain, Fat Loss, Strength, Endurance, and General Fitness.
- Accepts two or more available weekdays, then limits training days by experience (up to 4 for Beginner, 5 for Intermediate, and 6 for Advanced).
- Accepts a preferred workout time, a duration of 30, 45, 60, or 90 minutes, and one of four equipment levels.
- Selects a workout split from fixed templates, and filters exercises by experience and available equipment.
- Sets repetitions, sets, rest periods, and cardio time using rules based on the selected goal and experience.
- Prints a weekly timetable, detailed workouts, progression tips, and a general safety note.
- Lets the user replace an exercise with another suitable exercise for the same muscle group.

## Requirements

- Python 3 (the program uses only the Python standard library; no extra packages are required).
- Visual Studio Code.

## Run in Visual Studio Code

1. Install Python 3 and Visual Studio Code if they are not already installed.
2. Open the folder containing the Gym Planner source in VS Code.
3. Open the source file named `gym_planner.py` 
4. Open **Terminal > New Terminal** in VS Code.
5. In the terminal, run `python  gym_planner.py`. On some systems, use `python3 gym_planner.py` or `py gym_planner.py`.
6. Follow the numbered menus and prompts. For available days, enter at least two day numbers separated by spaces, for example `1 3 5`.
7. Review the timetable and workouts. At the replacement prompt, choose **Yes** to change an exercise or **No** to finish.



## Input checks

The program asks again when a menu choice is not a valid number, when the name is empty or longer than 30 characters, or when the age is not a whole number from 14 through 80. At least two different weekdays are required. Repeated day numbers are ignored.

## Scope

The planner is a text-based, rule-driven program. It does not save plans to a file, use an online service, or collect body measurements. Its output is general planning information and should be adjusted to the user's situation.
