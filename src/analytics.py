"""
DietSense Analytics Engine
計算 BMR、TDEE、熱量估算範圍
"""

class UserProfile:
    def __init__(self, age, gender, weight_kg, height_cm, activity_level, goal):
        self.age = age
        self.gender = gender
        self.weight_kg = weight_kg
        self.height_cm = height_cm
        self.activity_level = activity_level  # sedentary/light/moderate/active/very_active
        self.goal = goal  # lose/maintain/gain

ACTIVITY_FACTORS = {
    "sedentary":   1.2,
    "light":       1.375,
    "moderate":    1.55,
    "active":      1.725,
    "very_active": 1.9,
}

def calculate_bmr(profile: UserProfile) -> float:
    """Mifflin-St Jeor 公式"""
    base = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age
    if profile.gender.lower() == "male":
        return base + 5
    else:
        return base - 161

def calculate_tdee(profile: UserProfile) -> float:
    """TDEE = BMR × 活動係數"""
    bmr = calculate_bmr(profile)
    factor = ACTIVITY_FACTORS.get(profile.activity_level, 1.55)
    return round(bmr * factor, 1)

def estimate_calories(kcal_per_100g: float, portion_g: float,
                      confidence: float) -> tuple:
    """
    計算熱量估算範圍
    回傳 (low, point, high)
    """
    point = kcal_per_100g * portion_g / 100
    uncertainty = (1 - confidence) * 0.5 + 0.1   # 最少 ±10%
    margin = point * uncertainty
    return round(point - margin), round(point), round(point + margin)

def compute_macro_ratios(entries: list) -> dict:
    """計算巨量營養素佔比"""
    total_protein = sum(e.get("protein_g", 0) for e in entries)
    total_carb    = sum(e.get("carb_g",    0) for e in entries)
    total_fat     = sum(e.get("fat_g",     0) for e in entries)

    protein_kcal = total_protein * 4
    carb_kcal    = total_carb    * 4
    fat_kcal     = total_fat     * 9
    total_kcal   = protein_kcal + carb_kcal + fat_kcal or 1

    return {
        "protein_pct": round(protein_kcal / total_kcal * 100, 1),
        "carb_pct":    round(carb_kcal    / total_kcal * 100, 1),
        "fat_pct":     round(fat_kcal     / total_kcal * 100, 1),
    }

def safety_check(daily_kcal: float, profile: UserProfile) -> str:
    """
    回傳安全狀態：OK / WARNING / DANGER
    """
    min_safe = 1200 if profile.gender.lower() == "female" else 1500
    if daily_kcal < min_safe:
        return "DANGER"
    tdee = calculate_tdee(profile)
    if daily_kcal < tdee * 0.5:
        return "WARNING"
    return "OK"

