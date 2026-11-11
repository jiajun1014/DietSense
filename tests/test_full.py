import sys; sys.path.insert(0,'src')
from retrieval import search_taiwan, search_all
from analytics import UserProfile, calculate_tdee, estimate_calories, safety_check
from log import add_entry, today_summary, clear_today

# Test 1: Taiwan food search
r = search_taiwan('珍珠奶茶')
assert r, 'Taiwan DB miss'
name = r[0]['name']
kcal = r[0]['kcal_per_100g']
print(f'[OK] Taiwan DB: {name} | {kcal} kcal/100g')

r2 = search_all('台式牛肉麵')
assert r2
print(f'[OK] search_all: {r2[0]["name"]}')

# Test 2: Analytics
p = UserProfile(22,'female',55,162,'moderate','maintain')
tdee = calculate_tdee(p)
assert 1900 < tdee < 2200, f'TDEE={tdee}'
print(f'[OK] TDEE: {tdee} kcal')

lo, pt, hi = estimate_calories(180, 200, 0.85)
assert lo < pt < hi
print(f'[OK] Calorie range: {lo}~{hi} (mid={pt})')

assert safety_check(800, p) == 'DANGER'
assert safety_check(2000, p) == 'OK'
print('[OK] Safety check')

# Test 3: Log (SQLite)
clear_today()
add_entry('午餐','滷肉飯',300, 350,420,490, 15,60,14,'taiwan_db')
s = today_summary()
assert s['meal_count'] == 1
assert s['total_kcal_pt'] == 420
print(f'[OK] Log: {s["meal_count"]} entry, {s["total_kcal_pt"]} kcal')
clear_today()

print('')
print('All systems OK! DietSense is ready.')
print('  Web UI -> python src/app.py')
print('  CLI    -> python src/agent.py')

