"""
DietSense Analytics Engine
計算 BMR、TDEE、熱量估算範圍、巨量營養素
"""

ACTIVITY_FACTORS = {
    "sedentary":   1.2,
    "light":       1.375,
    "moderate":    1.55,
    "active":      1.725,
    "very_active": 1.9,
}

class UserProfile:
    def __init__(self, age=22, gender="female", weight_kg=60,
                 height_cm=165, activity_level="moderate", goal="maintain"):
        self.age            = age
        self.gender         = gender
        self.weight_kg      = weight_kg
        self.height_cm      = height_cm
        self.activity_level = activity_level
        self.goal           = goal  # lose / maintain / gain

    def to_dict(self):
        return self.__dict__


def calculate_bmr(p: UserProfile) -> float:
    base = 10 * p.weight_kg + 6.25 * p.height_cm - 5 * p.age
    return base + 5 if p.gender.lower() == "male" else base - 161


def calculate_tdee(p: UserProfile) -> float:
    factor = ACTIVITY_FACTORS.get(p.activity_level, 1.55)
    return round(calculate_bmr(p) * factor, 0)


def calorie_goal(p: UserProfile) -> float:
    tdee = calculate_tdee(p)
    if p.goal == "lose":    return tdee - 500
    if p.goal == "gain":    return tdee + 300
    return tdee


def estimate_calories(kcal_per_100g: float, portion_g: float,
                      confidence: float = 0.85) -> tuple[int, int, int]:
    """回傳 (low, point, high) kcal"""
    point   = kcal_per_100g * portion_g / 100
    margin  = point * (0.10 + (1 - confidence) * 0.40)
    return int(point - margin), int(point), int(point + margin)


def compute_macro_ratios(entries: list[dict]) -> dict:
    p = sum(e.get("protein_g", 0) for e in entries)
    c = sum(e.get("carb_g",    0) for e in entries)
    f = sum(e.get("fat_g",     0) for e in entries)
    total_kcal = p * 4 + c * 4 + f * 9 or 1
    return {
        "protein_pct": round(p * 4 / total_kcal * 100, 1),
        "carb_pct":    round(c * 4 / total_kcal * 100, 1),
        "fat_pct":     round(f * 9 / total_kcal * 100, 1),
        "protein_g":   round(p, 1),
        "carb_g":      round(c, 1),
        "fat_g":       round(f, 1),
    }


def safety_check(daily_kcal: float, p: UserProfile) -> str:
    min_safe = 1200 if p.gender.lower() == "female" else 1500
    if daily_kcal > 0 and daily_kcal < min_safe:
        return "DANGER"
    if daily_kcal > 0 and daily_kcal < calculate_tdee(p) * 0.5:
        return "WARNING"
    return "OK"
