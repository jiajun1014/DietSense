"""
DietSense Data Retrieval Layer
查詢 USDA API 與台灣食品成分資料庫
"""

import os
import requests
import pandas as pd

USDA_API_KEY = os.getenv("USDA_API_KEY", "DEMO_KEY")
USDA_BASE    = "https://api.nal.usda.gov/fdc/v1"

TAIWAN_DB_PATH = os.path.join(os.path.dirname(__file__),
                              "..", "data", "taiwan_food_db.csv")

def search_usda(food_name: str, top_k: int = 5) -> list:
    """
    從 USDA FoodData Central 搜尋食物
    回傳 [{ name, kcal_per_100g, protein_g, carb_g, fat_g, source }]
    """
    url    = f"{USDA_BASE}/foods/search"
    params = {"query": food_name, "pageSize": top_k, "api_key": USDA_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[USDA] Error: {e}")
        return []

    results = []
    for item in data.get("foods", []):
        nutrients = {n["nutrientName"]: n["value"]
                     for n in item.get("foodNutrients", [])}
        results.append({
            "name":          item.get("description", food_name),
            "kcal_per_100g": nutrients.get("Energy", 0),
            "protein_g":     nutrients.get("Protein", 0),
            "carb_g":        nutrients.get("Carbohydrate, by difference", 0),
            "fat_g":         nutrients.get("Total lipid (fat)", 0),
            "source":        "usda",
        })
    return results


def search_taiwan_db(food_name: str, top_k: int = 5) -> list:
    """
    從台灣食品成分資料庫（本地 CSV）搜尋食物
    """
    try:
        df = pd.read_csv(TAIWAN_DB_PATH, encoding="utf-8-sig")
    except FileNotFoundError:
        return []

    mask = df["食品名稱"].str.contains(food_name, na=False, case=False)
    hits = df[mask].head(top_k)

    results = []
    for _, row in hits.iterrows():
        results.append({
            "name":          row.get("食品名稱", food_name),
            "kcal_per_100g": row.get("熱量(kcal)", 0),
            "protein_g":     row.get("蛋白質(g)",  0),
            "carb_g":        row.get("碳水化合物(g)", 0),
            "fat_g":         row.get("脂肪(g)",    0),
            "source":        "taiwan_db",
        })
    return results


def search_all(food_name: str) -> list:
    """合併 USDA + 台灣 DB 搜尋結果"""
    results  = search_usda(food_name)
    results += search_taiwan_db(food_name)
    return results

