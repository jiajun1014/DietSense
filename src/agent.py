"""
DietSense Agent — 核心對話邏輯
使用 OpenAI Function Calling 架構

執行方式：
  python src/agent.py          # CLI 模式
  python src/app.py            # Gradio Web UI
"""

import os
import json
import sys

# 讓 src/ 內互相 import
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from analytics import UserProfile, calculate_tdee, calorie_goal, \
                      compute_macro_ratios, safety_check, estimate_calories
from retrieval import search_all
import log as diet_log

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── 預設用戶（可由對話動態更新）────────────────────────────
_user = UserProfile()


# ════════════════════════════════════════════════════════
# Tools（Function Calling 定義）
# ════════════════════════════════════════════════════════
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_food_nutrition",
            "description": "搜尋食物的熱量與營養素資訊。優先查詢台灣食物資料庫，再查 USDA。",
            "parameters": {
                "type": "object",
                "properties": {
                    "food_name": {
                        "type": "string",
                        "description": "食物名稱（中文或英文），例如：牛肉麵、雞胸肉、apple"
                    }
                },
                "required": ["food_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_food_entry",
            "description": "將一筆食物記錄新增至今日飲食日誌。",
            "parameters": {
                "type": "object",
                "properties": {
                    "meal_type": {
                        "type": "string",
                        "enum": ["早餐", "午餐", "晚餐", "點心", "宵夜"],
                        "description": "餐別"
                    },
                    "food_name": {"type": "string", "description": "食物名稱"},
                    "portion_g": {
                        "type": "number",
                        "description": "份量（公克）。若用戶說「一碗」約 200-300g，「一份」約 150g，請合理估算。"
                    },
                    "kcal_per_100g": {"type": "number", "description": "每 100g 熱量（kcal）"},
                    "protein_per_100g": {"type": "number", "description": "每 100g 蛋白質（g）"},
                    "carb_per_100g":    {"type": "number", "description": "每 100g 碳水化合物（g）"},
                    "fat_per_100g":     {"type": "number", "description": "每 100g 脂肪（g）"},
                    "confidence": {
                        "type": "number",
                        "description": "估算信心分數 0.0~1.0，份量描述越精確則越高"
                    },
                    "source": {"type": "string", "description": "資料來源（taiwan_db / usda / llm_estimate）"}
                },
                "required": ["meal_type","food_name","portion_g",
                             "kcal_per_100g","confidence"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_summary",
            "description": "取得今日所有飲食記錄的總熱量、巨量營養素摘要與目標進度。",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_user_profile",
            "description": "更新用戶的基本資料，以便計算個人化 TDEE。",
            "parameters": {
                "type": "object",
                "properties": {
                    "age":            {"type": "integer"},
                    "gender":         {"type": "string", "enum": ["male","female"]},
                    "weight_kg":      {"type": "number"},
                    "height_cm":      {"type": "number"},
                    "activity_level": {
                        "type": "string",
                        "enum": ["sedentary","light","moderate","active","very_active"]
                    },
                    "goal":           {"type": "string", "enum": ["lose","maintain","gain"]}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clear_today_log",
            "description": "清除今日所有飲食記錄（重新開始）。",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]


# ════════════════════════════════════════════════════════
# Tool 執行邏輯
# ════════════════════════════════════════════════════════
def _run_tool(name: str, args: dict) -> str:
    """執行 tool 並回傳 JSON 字串結果"""

    if name == "search_food_nutrition":
        results = search_all(args["food_name"])
        if not results:
            return json.dumps({"found": False,
                               "message": f"找不到「{args['food_name']}」的資料，請嘗試更精確的名稱或告知原料"})
        return json.dumps({"found": True, "results": results[:3]}, ensure_ascii=False)

    elif name == "log_food_entry":
        low, pt, high = estimate_calories(
            args["kcal_per_100g"], args["portion_g"],
            args.get("confidence", 0.80)
        )
        # 計算巨量營養素絕對值
        ratio = args["portion_g"] / 100
        protein_g = round(args.get("protein_per_100g", 0) * ratio, 1)
        carb_g    = round(args.get("carb_per_100g",    0) * ratio, 1)
        fat_g     = round(args.get("fat_per_100g",     0) * ratio, 1)

        diet_log.add_entry(
            meal=args["meal_type"],
            name=args["food_name"],
            portion_g=args["portion_g"],
            kcal_low=low, kcal_pt=pt, kcal_high=high,
            protein_g=protein_g, carb_g=carb_g, fat_g=fat_g,
            source=args.get("source", "unknown")
        )
        return json.dumps({
            "logged": True,
            "food":   args["food_name"],
            "meal":   args["meal_type"],
            "kcal":   f"{low}~{high} kcal（中位估計 {pt} kcal）",
            "macros": f"蛋白質 {protein_g}g｜碳水 {carb_g}g｜脂肪 {fat_g}g"
        }, ensure_ascii=False)

    elif name == "get_daily_summary":
        s    = diet_log.today_summary()
        tdee = calculate_tdee(_user)
        goal = calorie_goal(_user)
        diff = s["total_kcal_pt"] - goal
        safety = safety_check(s["total_kcal_pt"], _user)
        return json.dumps({
            "entries": [
                f"{e['meal']} | {e['name']} | {e['kcal_low']}~{e['kcal_high']} kcal"
                for e in s["entries"]
            ],
            "total_kcal": f"{s['total_kcal_low']}~{s['total_kcal_high']} kcal（中位 {s['total_kcal_pt']}）",
            "macros":     f"蛋白質 {s['protein_g']}g｜碳水 {s['carb_g']}g｜脂肪 {s['fat_g']}g",
            "tdee":       tdee,
            "goal_kcal":  goal,
            "diff":       diff,
            "diff_label": "超出" if diff > 0 else "距目標還差",
            "safety":     safety,
            "meal_count": s["meal_count"]
        }, ensure_ascii=False)

    elif name == "update_user_profile":
        for k, v in args.items():
            if hasattr(_user, k):
                setattr(_user, k, v)
        return json.dumps({"updated": True, "profile": _user.to_dict(),
                           "tdee": calculate_tdee(_user)}, ensure_ascii=False)

    elif name == "clear_today_log":
        diet_log.clear_today()
        return json.dumps({"cleared": True})

    return json.dumps({"error": f"Unknown tool: {name}"})


# ════════════════════════════════════════════════════════
# 主對話函式
# ════════════════════════════════════════════════════════
SYSTEM_PROMPT = """你是 DietSense，一個專業的繁體中文飲食熱量追蹤 AI Agent。

## 你的能力
1. 從用戶的自然語言中解析食物名稱、份量、餐別
2. 搜尋食物營養資訊（工具：search_food_nutrition）
3. 記錄飲食至日誌（工具：log_food_entry）
4. 查詢今日攝取摘要（工具：get_daily_summary）
5. 更新個人資料以計算個人化 TDEE（工具：update_user_profile）

## 重要規則
- **永遠**使用工具查詢食物資訊後再記錄，不要憑空捏造數字
- 提供熱量估算時必須給**範圍**（低~高），不能只給單一數字
- 若份量描述模糊（如「一點點」「一些」），直接用合理預設值並告知用戶
- 如果用戶一次描述多種食物，逐一搜尋並記錄每種食物
- 回應使用**繁體中文**，語氣親切自然
- 記錄後主動告知今日累計熱量

## 安全機制
- 若今日攝取 < 1200 kcal（女）/ 1500 kcal（男），需主動提醒健康風險
- 不提供減重速度超過每週 1kg 的建議
- 明確告知本系統不能取代專業營養師

## 份量估算參考
- 一碗白飯 ≈ 200g；一碗麵 ≈ 200g（麵）+ 湯
- 一份菜 ≈ 100g；一塊肉 ≈ 80~120g
- 台式雞排 ≈ 180g；珍珠奶茶大杯 ≈ 700ml
"""

def chat(user_message: str, history: list[dict]) -> tuple[str, list[dict]]:
    """
    單輪對話
    history: [{"role":"user/assistant", "content":"..."}]
    回傳 (assistant_reply, updated_history)
    """
    history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    # ── Agentic Loop（最多 6 輪 tool call）──────────────
    for _ in range(6):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.3,
        )
        msg = response.choices[0].message

        # 沒有 tool call → 最終回覆
        if not msg.tool_calls:
            reply = msg.content or ""
            history.append({"role": "assistant", "content": reply})
            return reply, history

        # 有 tool call → 執行並繼續
        messages.append(msg)
        for tc in msg.tool_calls:
            args   = json.loads(tc.function.arguments)
            result = _run_tool(tc.function.name, args)
            messages.append({
                "role":         "tool",
                "tool_call_id": tc.id,
                "content":      result,
            })

    # 超過輪次上限
    reply = "⚠️ 處理時間過長，請換個方式描述你的飲食。"
    history.append({"role": "assistant", "content": reply})
    return reply, history


# ════════════════════════════════════════════════════════
# CLI 模式
# ════════════════════════════════════════════════════════
def run_cli():
    print("=" * 55)
    print("  DietSense — Daily Calorie Intake AI Agent")
    print("  輸入 'quit' 結束 | 'clear' 清除今日記錄")
    print("=" * 55)
    history = []
    while True:
        try:
            user_input = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if user_input.lower() == "clear":
            diet_log.clear_today()
            print("DietSense：今日記錄已清除 ✓")
            continue
        reply, history = chat(user_input, history)
        print(f"\nDietSense：{reply}")


if __name__ == "__main__":
    run_cli()
