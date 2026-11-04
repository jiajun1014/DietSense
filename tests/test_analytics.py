"""
基本測試：Analytics Engine
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analytics import UserProfile, calculate_bmr, calculate_tdee, \
                      estimate_calories, safety_check

def test_bmr_female():
    p = UserProfile(22, "female", 55, 162, "moderate", "maintain")
    bmr = calculate_bmr(p)
    assert 1200 < bmr < 1500, f"BMR out of range: {bmr}"
    print(f"[PASS] BMR female: {bmr:.1f}")

def test_bmr_male():
    p = UserProfile(25, "male", 70, 175, "active", "maintain")
    bmr = calculate_bmr(p)
    assert 1600 < bmr < 1900, f"BMR out of range: {bmr}"
    print(f"[PASS] BMR male: {bmr:.1f}")

def test_tdee():
    p = UserProfile(22, "female", 55, 162, "moderate", "maintain")
    tdee = calculate_tdee(p)
    assert 1800 < tdee < 2400, f"TDEE out of range: {tdee}"
    print(f"[PASS] TDEE: {tdee:.1f}")

def test_calorie_estimate():
    low, point, high = estimate_calories(100, 200, 0.9)
    assert low < point < high
    print(f"[PASS] Calorie range: {low}-{point}-{high}")

def test_safety_check():
    p = UserProfile(22, "female", 55, 162, "moderate", "maintain")
    assert safety_check(800,  p) == "DANGER"
    assert safety_check(1500, p) == "OK"
    print("[PASS] Safety check")

if __name__ == "__main__":
    test_bmr_female()
    test_bmr_male()
    test_tdee()
    test_calorie_estimate()
    test_safety_check()
    print("\nAll tests passed.")
