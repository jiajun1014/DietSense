"""
DietSense Main Agent
主要對話迴圈與任務協調
"""

import os
import json
import datetime
from dotenv import load_dotenv
from openai import OpenAI

from analytics import UserProfile, calculate_tdee, estimate_calories, \
                      compute_macro_ratios, safety_check
from retrieval import search_all

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── 簡易 In-memory 每日日誌 ──────────────────────────────
daily_log: list[dict] = []

# ── 預設示範用戶 ─────────────────────────────────────────
demo_user = UserProfile(
    age=22, gender="female",
    weight_kg=55, height_cm=162,
    activity_level="moderate", goal="maintain"
)

SYSTEM_PROMPT = """你是 DietSense，一個專業的飲食熱量追蹤 AI Agent。
你的能力：
1. 從用戶的自然語言描述中解析食物名稱、份量、餐別
2. 查詢熱量資料庫並估算熱量（含信賴區間）
3. 分析每日攝取與 TDEE 的差距
4. 提供個人化飲食建議
5. 偵測異常飲食模式並給予安全提示

回應規則：
- 永遠提供熱量範圍（低估-高估），不要只給單一數字
- 若資訊不足（份量不明確），主動詢問
- 繁體中文回應
- 不提供超出 AI 能力的醫療診斷
"""

conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]


def chat(user_input: str) -> str:
    """單輪對話"""
    conversation_history.append({"role": "user", "content": user_input})

    # ── 簡易意圖判斷 ────────────────────────────────────
    intent = detect_intent(user_input)

    if intent == "analyze":
        # 注入當日日誌給 LLM
        log_summary = format_log_for_llm()
        tdee = calculate_tdee(demo_user)
        context = f"\n[當日飲食記錄]\n{log_summary}\n[用戶 TDEE: {tdee} kcal]"
        conversation_history[-1]["content"] += context

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation_history,
        temperature=0.3,
    )
    reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": reply})

    # ── 安全檢查 ────────────────────────────────────────
    total_kcal = sum(e.get("kcal_point", 0) for e in daily_log)
    status = safety_check(total_kcal, demo_user)
    if status == "DANGER":
        reply += "\n\n⚠️ 警示：今日攝取熱量低於安全下限，請確保充足飲食。建議諮詢專業營養師。"

    return reply


def detect_intent(text: str) -> str:
    """簡易意圖分類"""
    analyze_kw = ["分析", "今天", "今日", "總共", "吃了多少", "統計", "summary"]
    if any(kw in text for kw in analyze_kw):
        return "analyze"
    return "general"


def format_log_for_llm() -> str:
    if not daily_log:
        return "（尚無記錄）"
    lines = []
    for e in daily_log:
        lines.append(
            f"  {e.get('meal','?')} | {e.get('name','?')} | "
            f"{e.get('kcal_low',0)}-{e.get('kcal_high',0)} kcal"
        )
    total = sum(e.get("kcal_point", 0) for e in daily_log)
    lines.append(f"  ── 預估總計：{total} kcal")
    return "\n".join(lines)


def main():
    print("=" * 50)
    print("  DietSense — Daily Calorie Intake AI Agent")
    print("  輸入 'quit' 結束對話")
    print("=" * 50)
    while True:
        user_input = input("\n你：").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue
        reply = chat(user_input)
        print(f"\nDietSense：{reply}")


if __name__ == "__main__":
    main()

