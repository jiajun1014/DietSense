"""
DietSense Data Retrieval
搜尋台灣本地食物 JSON 資料庫 + USDA FoodData Central API
"""

import os
import json
import difflib
import requests

USDA_KEY = os.getenv("USDA_API_KEY", "DEMO_KEY")
USDA_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "taiwan_food_db.json")

def _load_taiwan_db() -> dict:
    try:
        with open(_DB_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

TAIWAN_DB = _load_taiwan_db()


def search_taiwan(food_name: str, top_k: int = 3) -> list[dict]:
    """模糊匹配台灣食品資料庫"""
    keys   = list(TAIWAN_DB.keys())
    # 先找包含子字串的
    exact  = [k for k in keys if food_name in k or k in food_name]
    # 再用 difflib 模糊匹配
    fuzzy  = difflib.get_close_matches(food_name, keys, n=top_k, cutoff=0.4)
    merged = list(dict.fromkeys(exact + fuzzy))[:top_k]

    results = []
    for k in merged:
        d = TAIWAN_DB[k]
        results.append({
            "name":          k,
            "kcal_per_100g": d["kcal"],
            "protein_g":     d.get("protein", 0),
            "carb_g":        d.get("carb",    0),
            "fat_g":         d.get("fat",     0),
            "unit":          d.get("unit", "100g"),
            "source":        "taiwan_db",
            "confidence":    0.90 if k == food_name else 0.75,
        })
    return results


def search_usda(food_name: str, top_k: int = 3) -> list[dict]:
    """查詢 USDA FoodData Central"""
    try:
        resp = requests.get(USDA_URL,
            params={"query": food_name, "pageSize": top_k, "api_key": USDA_KEY},
            timeout=5)
        resp.raise_for_status()
        foods = resp.json().get("foods", [])
    except Exception:
        return []

    results = []
    for item in foods:
        nmap = {n["nutrientName"]: n.get("value", 0)
                for n in item.get("foodNutrients", [])}
        results.append({
            "name":          item.get("description", food_name),
            "kcal_per_100g": nmap.get("Energy", 0),
            "protein_g":     nmap.get("Protein", 0),
            "carb_g":        nmap.get("Carbohydrate, by difference", 0),
            "fat_g":         nmap.get("Total lipid (fat)", 0),
            "unit":          "100g",
            "source":        "usda",
            "confidence":    0.70,
        })
    return results


def search_all(food_name: str) -> list[dict]:
    """合併台灣DB（優先）+ USDA"""
    tw = search_taiwan(food_name)
    if tw:
        return tw          # 台灣食物找到就直接用
    return search_usda(food_name)
