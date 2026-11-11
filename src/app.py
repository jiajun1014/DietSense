"""
DietSense Web UI — Gradio
執行：python src/app.py
開啟：http://localhost:7860
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import gradio as gr
from agent import chat, _user, calculate_tdee, calorie_goal
import log as diet_log

# ── 對話歷史（Gradio session 內共享）──────────────────────
_history: list[dict] = []


def respond(user_message: str, chatbot_ui: list):
    global _history
    if not user_message.strip():
        return "", chatbot_ui

    reply, _history = chat(user_message, _history)

    chatbot_ui.append((user_message, reply))
    return "", chatbot_ui


def get_summary_md() -> str:
    s     = diet_log.today_summary()
    tdee  = calculate_tdee(_user)
    goal  = calorie_goal(_user)
    eaten = s["total_kcal_pt"]
    left  = goal - eaten

    bars  = "█" * min(int(eaten / goal * 20), 20) if goal else ""
    empty = "░" * (20 - len(bars))

    lines = [
        f"## 📊 今日攝取摘要",
        f"",
        f"**熱量進度**",
        f"`{bars}{empty}` {eaten} / {int(goal)} kcal",
        f"",
        f"{'✅ 距目標還差' if left > 0 else '⚠️ 已超出目標'} **{abs(int(left))} kcal**",
        f"",
        f"**巨量營養素**",
        f"- 🥩 蛋白質：{s['protein_g']} g",
        f"- 🍚 碳水：{s['carb_g']} g",
        f"- 🧈 脂肪：{s['fat_g']} g",
        f"",
        f"**今日記錄（{s['meal_count']} 筆）**",
    ]
    for e in s["entries"]:
        lines.append(f"- {e['meal']}｜{e['name']}｜{e['kcal_low']}~{e['kcal_high']} kcal")
    if not s["entries"]:
        lines.append("_尚無記錄_")
    return "\n".join(lines)


def clear_log():
    global _history
    diet_log.clear_today()
    _history = []
    return [], "今日記錄已清除，對話重置 ✓"


def refresh_summary():
    return get_summary_md()


# ════════════════════════════════════════════════════════
# Gradio UI
# ════════════════════════════════════════════════════════
with gr.Blocks(title="DietSense", theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # 🍱 DietSense
    ### Daily Calorie Intake AI Agent
    用自然語言告訴我你吃了什麼，我來幫你計算熱量、追蹤每日攝取。
    """)

    with gr.Row():
        # 左側：對話
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="對話記錄",
                height=480,
                bubble_full_width=False,
            )
            with gr.Row():
                txt = gr.Textbox(
                    placeholder="例：我中午吃了一碗滷肉飯跟一個茶葉蛋",
                    label="你的飲食描述",
                    scale=5,
                    autofocus=True,
                )
                send_btn = gr.Button("送出", variant="primary", scale=1)

            gr.Examples(
                examples=[
                    "我早餐吃了一個蛋餅和一杯豆漿",
                    "午餐吃了台式牛肉麵加一顆滷蛋",
                    "晚餐吃了雞腿便當，菜吃了一半",
                    "幫我分析今天吃了多少",
                    "點心喝了一杯珍珠奶茶大杯",
                    "我是女生，22歲，55公斤，165公分，運動量普通，目標維持體重",
                ],
                inputs=txt,
                label="快速範例（點擊後按送出）",
            )

        # 右側：摘要
        with gr.Column(scale=2):
            summary_md = gr.Markdown(get_summary_md())
            refresh_btn = gr.Button("🔄 更新摘要", variant="secondary")
            clear_btn   = gr.Button("🗑️ 清除今日記錄", variant="stop")
            clear_msg   = gr.Textbox(label="", interactive=False, lines=1)

    # ── 事件綁定 ──────────────────────────────────────
    send_btn.click(
        respond,
        inputs=[txt, chatbot],
        outputs=[txt, chatbot],
    ).then(refresh_summary, outputs=summary_md)

    txt.submit(
        respond,
        inputs=[txt, chatbot],
        outputs=[txt, chatbot],
    ).then(refresh_summary, outputs=summary_md)

    refresh_btn.click(refresh_summary, outputs=summary_md)

    clear_btn.click(clear_log, outputs=[chatbot, clear_msg])\
             .then(refresh_summary, outputs=summary_md)

    gr.Markdown("""
    ---
    > ⚠️ DietSense 為學術研究專題，熱量估算僅供參考，不能取代專業營養師建議。
    """)

if __name__ == "__main__":
    print("啟動 DietSense Web UI...")
    print("請開啟瀏覽器：http://localhost:7860")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)

