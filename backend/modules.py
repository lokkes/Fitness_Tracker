import json
from pathlib import Path
from typing import Dict, List

from .schemas import TrainingGoal, TrainingRequest


EXERCISE_FILE = Path(__file__).resolve().parent / "data" / "exercise.json"
WEEK_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

FOCUS_TO_CATEGORY = {
    "Technique": "technique",
    "Speed": "speed",
    "Power": "power",
    "Endurance": "cardio",
    "Sparring": "sparring",
    "Strength": "strength",
    "Recovery": "recovery",
    "Fight Simulation": "sparring",
}

GOAL_TO_FOCUS = {
    TrainingGoal.technique: ["Technique", "Speed", "Defense"],
    TrainingGoal.stamina: ["Endurance", "Recovery", "Strength"],
    TrainingGoal.power: ["Power", "Strength", "Endurance"],
    TrainingGoal.weight_loss: ["Endurance", "Strength", "Technique"],
    TrainingGoal.fight_prep: ["Technique", "Sparring", "Power", "Endurance"],
}

WEAKNESS_TO_FOCUS = {
    "cardio": ["Endurance", "Recovery"],
    "defense": ["Technique", "Sparring"],
    "power": ["Power", "Strength"],
    "speed": ["Speed", "Technique"],
    "technique": ["Technique", "Speed"],
}


def load_exercises() -> Dict[str, List[str]]:
    with EXERCISE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def _unique(values: List[str]) -> List[str]:
    seen = set()
    ordered = []

    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)

    return ordered


def _normalize_focus(focus: str) -> str:
    if focus == "Defense":
        return "Technique"
    return focus


def _build_focus_cycle(plan: TrainingRequest) -> List[str]:
    focus_cycle: List[str] = []

    for goal in plan.goal.primary_goals:
        focus_cycle.extend(GOAL_TO_FOCUS.get(goal, []))

    if plan.weakness:
        for weakness in plan.weakness:
            focus_cycle.extend(WEAKNESS_TO_FOCUS.get(weakness.value, []))

    experience = plan.experience.value
    if experience == "beginner":
        focus_cycle.extend(["Technique", "Endurance", "Recovery"])
    elif experience == "intermediate":
        focus_cycle.extend(["Technique", "Power", "Endurance", "Recovery"])
    else:
        focus_cycle.extend(["Technique", "Power", "Speed", "Sparring", "Recovery"])

    fatigue_level = plan.context.fatigue_level if plan.context else 5
    if fatigue_level >= 8:
        focus_cycle.extend(["Recovery", "Technique"])

    normalized_cycle = [_normalize_focus(focus) for focus in focus_cycle]
    normalized_cycle.append("Recovery")
    return _unique(normalized_cycle)


def _exercise_allowed(exercise: str, plan: TrainingRequest) -> bool:
    equipment = plan.equipment
    text = exercise.lower()

    if equipment is None:
        return True

    if equipment.has_heavy_bag is False and "heavy bag" in text:
        return False

    if equipment.has_speed_bag is False and "speed bag" in text:
        return False

    if equipment.has_sparring_partner is False and ("partner" in text or "sparring" in text):
        return False

    gym_keywords = ["assault bike", "rowing machine", "medicine ball", "deadlift", "bench press", "dumbbell", "kettlebell"]
    if equipment.has_gym is False and any(keyword in text for keyword in gym_keywords):
        return False

    weight_keywords = ["weighted", "deadlift", "bench press", "dumbbell", "kettlebell", "medicine ball", "farmer", "squat"]
    if equipment.has_weights is False and any(keyword in text for keyword in weight_keywords):
        return False

    return True


def _session_size(plan: TrainingRequest) -> int:
    duration = plan.availability.session_duration or 60
    if duration <= 30:
        return 2
    if duration <= 60:
        return 3
    if duration <= 90:
        return 4
    return 5


def _pick_exercises(category: str, exercises: Dict[str, List[str]], plan: TrainingRequest, day_index: int) -> List[str]:
    available = exercises.get(category, [])
    allowed = [exercise for exercise in available if _exercise_allowed(exercise, plan)]

    if not allowed:
        allowed = available

    if not allowed:
        return []

    session_size = min(_session_size(plan), len(allowed))
    start = day_index % len(allowed)
    rotated = allowed[start:] + allowed[:start]
    return rotated[:session_size]


def _build_day_notes(plan: TrainingRequest, focus: str) -> List[str]:
    notes = [f"Experience level: {plan.experience.value.capitalize()}"]

    if plan.availability.preferred_time:
        notes.append(f"Preferred time: {plan.availability.preferred_time.value.capitalize()}")

    if plan.weakness:
        notes.append(
            "Weakness emphasis: " + ", ".join(weakness.value.replace("_", " ").capitalize() for weakness in plan.weakness)
        )

    if focus == "Recovery":
        notes.append("Keep the intensity low and prioritize clean technique, mobility, and rest.")
    elif focus == "Sparring":
        notes.append("Use controlled intensity and focus on decision-making, not just volume.")
    else:
        notes.append("Warm up for 10 minutes before the main work and finish with light cooldown work.")

    return notes


def create_plan(plan: TrainingRequest) -> Dict[str, object]:
    exercises = load_exercises()
    days = plan.availability.days_per_week
    focus_cycle = _build_focus_cycle(plan)
    week_plan = []

    for i in range(days):
        focus = focus_cycle[i % len(focus_cycle)]
        category = FOCUS_TO_CATEGORY[focus]
        workout = _pick_exercises(category, exercises, plan, i)

        week_plan.append(
            {
                "day": WEEK_DAYS[i],
                "focus": focus,
                "duration_minutes": plan.availability.session_duration or 60,
                "workout": workout,
                "notes": _build_day_notes(plan, focus),
            }
        )

    return {
        "plan_overview": {
            "days_per_week": days,
            "primary_goals": [goal.value for goal in plan.goal.primary_goals],
            "experience": plan.experience.value,
        },
        "week_plan": week_plan,
    }
