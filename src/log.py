"""
DietSense Daily Log
儲存每日飲食記錄（in-memory + SQLite 持久化）
"""

import sqlite3
import json
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "diet_log.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS food_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            date      TEXT,
            meal      TEXT,
            name      TEXT,
            portion_g REAL,
            kcal_low  INTEGER,
            kcal_pt   INTEGER,
            kcal_high INTEGER,
            protein_g REAL,
            carb_g    REAL,
            fat_g     REAL,
            source    TEXT,
            created   TEXT
        )
    """)
    conn.commit()
    return conn


def add_entry(meal: str, name: str, portion_g: float,
              kcal_low: int, kcal_pt: int, kcal_high: int,
              protein_g: float = 0, carb_g: float = 0, fat_g: float = 0,
              source: str = "unknown"):
    today = datetime.date.today().isoformat()
    now   = datetime.datetime.now().isoformat()
    with _get_conn() as conn:
        conn.execute("""
            INSERT INTO food_log
            (date,meal,name,portion_g,kcal_low,kcal_pt,kcal_high,
             protein_g,carb_g,fat_g,source,created)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (today, meal, name, portion_g,
              kcal_low, kcal_pt, kcal_high,
              protein_g, carb_g, fat_g, source, now))
        conn.commit()


def get_today() -> list[dict]:
    today = datetime.date.today().isoformat()
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM food_log WHERE date=? ORDER BY id", (today,)
        ).fetchall()
    cols = ["id","date","meal","name","portion_g",
            "kcal_low","kcal_pt","kcal_high",
            "protein_g","carb_g","fat_g","source","created"]
    return [dict(zip(cols, r)) for r in rows]


def clear_today():
    today = datetime.date.today().isoformat()
    with _get_conn() as conn:
        conn.execute("DELETE FROM food_log WHERE date=?", (today,))
        conn.commit()


def today_summary() -> dict:
    entries = get_today()
    total_kcal_pt  = sum(e["kcal_pt"]  for e in entries)
    total_kcal_low = sum(e["kcal_low"] for e in entries)
    total_kcal_hi  = sum(e["kcal_high"] for e in entries)
    return {
        "entries":        entries,
        "total_kcal_low": total_kcal_low,
        "total_kcal_pt":  total_kcal_pt,
        "total_kcal_high":total_kcal_hi,
        "protein_g":      round(sum(e["protein_g"] for e in entries), 1),
        "carb_g":         round(sum(e["carb_g"]    for e in entries), 1),
        "fat_g":          round(sum(e["fat_g"]      for e in entries), 1),
        "meal_count":     len(entries),
    }

