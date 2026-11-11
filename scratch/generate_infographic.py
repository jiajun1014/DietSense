"""
生成 DietSense A4 橫式 高密度 NUMBERING 資訊圖表
規格：A4 橫式 (297mm x 210mm -> 11.69 x 8.27 inches), 300 DPI
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Arrow
import os

# 設定字型為微軟正黑體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Microsoft YaHei', 'SimHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# A4 橫式比例: 11.69 x 8.27 inches
fig = plt.figure(figsize=(11.69, 8.27), dpi=300)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# 顏色定義
DARK_NAVY = "#0F2537"
PRIMARY_BLUE = "#1B4965"
CYAN_ACCENT = "#62B6CB"
LIGHT_BG = "#F4F7F6"
CARD_BG = "#FFFFFF"
BORDER_COLOR = "#D0DBE5"
TEXT_MAIN = "#1A1A1A"
TEXT_MUTED = "#555555"
GREEN_BADGE = "#2D6A4F"
TAG_BG = "#E8F1F5"
ACCENT_ORANGE = "#E07A5F"

# 背景底色
ax.add_patch(Rectangle((0, 0), 100, 100, color=LIGHT_BG, zorder=0))

# 頂部 Header Banner (Y: 92 ~ 100)
ax.add_patch(Rectangle((0, 92), 100, 8, color=DARK_NAVY, zorder=1))
ax.text(2.0, 95.8, "DietSense 專題提案系統性解析資訊圖表", fontsize=15, fontweight='bold', color="#FFFFFF", va='center')
ax.text(2.0, 93.6, "依據《期末專題提案作業規範》與《2020 A-Z SOP Outline》 · 分析對象：《期中Proposal_熱量AI_Agent.docx》與 GitHub 原始碼", fontsize=8.5, color="#D0DBE5", va='center')
ax.text(98.0, 95.0, "DIC3: A4 橫式 高密度 NUMBERING", fontsize=9.5, fontweight='bold', color="#62B6CB", ha='right', va='center')

def draw_card(x, y, w, h, title, num, bg_color=CARD_BG, border_color=BORDER_COLOR):
    """繪製模組卡片與編號標籤"""
    # 陰影與主卡片
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.0",
                                facecolor=bg_color, edgecolor=border_color, linewidth=1.2, zorder=2))
    # 標題欄
    ax.add_patch(FancyBboxPatch((x, y + h - 3.8), w, 3.8, boxstyle="round,pad=0,rounding_size=0.8",
                                facecolor=PRIMARY_BLUE, edgecolor=PRIMARY_BLUE, linewidth=0.5, zorder=3))
    # 補底防圓角穿透
    ax.add_patch(Rectangle((x, y + h - 3.8), w, 1.8, facecolor=PRIMARY_BLUE, edgecolor='none', zorder=3))
    
    # 卡片編號球
    ax.add_patch(patches.Circle((x + 2.5, y + h - 1.9), 1.3, facecolor="#FFFFFF", edgecolor='none', zorder=4))
    ax.text(x + 2.5, y + h - 1.9, str(num), fontsize=9, fontweight='bold', color=PRIMARY_BLUE, ha='center', va='center', zorder=5)
    
    # 卡片標題
    ax.text(x + 4.8, y + h - 1.9, title, fontsize=9.5, fontweight='bold', color="#FFFFFF", va='center', zorder=4)

# -------------------------------------------------------------
# 模組 1: 核心維度檢核 (左上, X: 2, Y: 57, W: 31, H: 33)
# -------------------------------------------------------------
draw_card(2, 57, 31, 33, "符合度總覽：核心維度檢視 (1.1-1.4)", 1)
dim_items = [
    ("1.1 AI Agent 智慧代理", "GPT-4o Planner 協調意圖識別、Clarification Loop 與 5 大 Tool Calling。超越純問答 Chatbot。"),
    ("1.2 領域知識整合 (Domain)", "整合代謝平衡模型、Mifflin-St Jeor 公式、AMDR 巨量比例、衛福部指南與 <1200 kcal 安全防護。"),
    ("1.3 數據分析與不確定性", "串接台灣衛福部資料庫 + USDA API + 向量庫；計算置信區間 (low, point, high)，拒絕偽精確。"),
    ("1.4 真實世界情境落地", "專注台灣外食與夜市小吃痛點，解決傳統手動輸入 85% 於 30 天內放棄之認知負擔。")
]
cur_y = 85.5
for idx, (title, desc) in enumerate(dim_items):
    # 標題標籤
    ax.text(3.5, cur_y, f"[ {title} ]", fontsize=7.5, fontweight='bold', color=PRIMARY_BLUE, zorder=4)
    # 勾選標籤
    ax.add_patch(FancyBboxPatch((28.5, cur_y - 0.4), 3.5, 1.5, boxstyle="round,pad=0.2", facecolor="#E8F5E9", edgecolor="#4CAF50", linewidth=0.6, zorder=4))
    ax.text(30.25, cur_y + 0.35, "達標", fontsize=6.8, fontweight='bold', color="#2E7D32", ha='center', va='center', zorder=5)
    
    # 描述 (手動分行提高緊密排版)
    words = desc
    line1 = words[:32]
    line2 = words[32:64]
    ax.text(3.5, cur_y - 1.5, line1, fontsize=6.8, color=TEXT_MAIN, zorder=4)
    if line2:
        ax.text(3.5, cur_y - 2.8, line2, fontsize=6.8, color=TEXT_MUTED, zorder=4)
    cur_y -= 6.8

# -------------------------------------------------------------
# 模組 2: A–F 摘要六段式結構 (左下, X: 2, Y: 2, W: 31, H: 53)
# -------------------------------------------------------------
draw_card(2, 2, 31, 53, "Abstract & Introduction 結構對照 (2.1-2.2)", 2)
af_items = [
    ("A", "Attention Getter 引題", "引用 WHO 2025 全球 10 億肥胖人口、台灣成人過重率 47.9% 及年逾 500 億醫療支出。"),
    ("B", "But 核心挑戰與痛點", "現有手動工具負擔繁瑣、缺乏台灣在地小吃、自報誤差達 18-54%、85% 於一個月內放棄。"),
    ("C", "Cure 提出創新解藥", "DietSense：對話式每日熱量分析 Domain AI Agent，兼顧便利性與在地化營養支持。"),
    ("D", "Development 技術架構", "整合 LLM 意圖推理、RAG 多來源檢索、Mifflin-St Jeor 引擎與區間不確定性量化。"),
    ("E", "Experiments 評估規劃", "500 筆台式料理標註集、USDA 與台灣成分庫，對照 MyFitnessPal 展開 20 人 7 天實測。"),
    ("F", "Findings 預期產出", "遵循學術誠實原則不捏造數據；預期達成 ±20% 誤差內準確率 >85%、記錄耗時縮短 60%。")
]
cur_y = 50.5
for code, name, text in af_items:
    # 圓形徽章
    ax.add_patch(patches.Circle((4.2, cur_y - 0.4), 1.1, facecolor=CYAN_ACCENT, edgecolor=PRIMARY_BLUE, linewidth=0.8, zorder=4))
    ax.text(4.2, cur_y - 0.4, code, fontsize=7.5, fontweight='bold', color="#FFFFFF", ha='center', va='center', zorder=5)
    ax.text(6.0, cur_y - 0.1, name, fontsize=7.5, fontweight='bold', color=PRIMARY_BLUE, zorder=4)
    
    # 內文兩行
    l1 = text[:30]
    l2 = text[30:60]
    ax.text(6.0, cur_y - 1.6, l1, fontsize=6.6, color=TEXT_MAIN, zorder=4)
    if l2:
        ax.text(6.0, cur_y - 2.8, l2, fontsize=6.6, color=TEXT_MUTED, zorder=4)
    cur_y -= 5.0

# 2.2 緒論論證精神區塊 (底部框)
ax.add_patch(FancyBboxPatch((3.2, 3.5), 28.6, 15.0, boxstyle="round,pad=0,rounding_size=0.6", facecolor="#F0F4F8", edgecolor="#CBD5E1", linewidth=0.8, zorder=3))
ax.text(4.2, 16.5, "2.2 Introduction 論證精神 (回答 Why worth doing?)", fontsize=7.2, fontweight='bold', color=PRIMARY_BLUE, zorder=4)
intro_pts = [
    "• 四大核心障礙：查詢負擔、份量模糊、複合料理拆解困難、台灣食物缺乏。",
    "• 競品清晰界定：手動輸入 (繁瑣)、拍照辨識 (無隱藏油脂)、通用LLM (易幻覺)。",
    "• 核心創新貢獻：多源資料錨定 + 置信區間量化 + 飲食失調安全攔截。"
]
for i, pt in enumerate(intro_pts):
    ax.text(4.2, 14.2 - i * 2.8, pt, fontsize=6.4, color=TEXT_MAIN, zorder=4)

# -------------------------------------------------------------
# 模組 3: Deep Research 三大核心問題 (中上, X: 34.5, Y: 57, W: 32, H: 33)
# -------------------------------------------------------------
draw_card(34.5, 57, 32, 33, "Deep Research：三大核心問題 (3.1-3.3)", 3)
# 3.1 五個核心思維
ax.text(36.0, 85.5, "3.1 領域五大核心思維模式 (Mental Models)", fontsize=7.5, fontweight='bold', color=PRIMARY_BLUE, zorder=4)
q1_text = (
    "① 能量平衡為基 (攝取-消耗=體重)  ② 巨量營養素比例 (AMDR 碳水/蛋白質/脂肪)\n"
    "③ 份量不確定性 (自報誤差18-54%)   ④ 個體代謝差異 (代謝率與活動係數)\n"
    "⑤ 行為情境意識 (用餐情境與暴食誘發因子)"
)
ax.text(36.0, 81.8, q1_text, fontsize=6.6, color=TEXT_MAIN, linespacing=1.3, zorder=4)

# 3.2 三大專業爭論
ax.text(36.0, 75.0, "3.2 三大核心專業爭論 (Debates & Evidence)", fontsize=7.5, fontweight='bold', color=PRIMARY_BLUE, zorder=4)
q2_items = [
    ("爭論1: 熱量數量 vs. 食物品質", "熱力學赤字必然有效 vs. 荷爾蒙與加工等級影響長期留存。"),
    ("爭論2: AI 純文字估算 vs. 硬體輔助", "對話極低阻力 (+-20%) vs. 臨床需3D掃描/食物秤。採區間輸出妥協。"),
    ("爭論3: 通用指引 vs. 高度個人化", "DRI/指南為安全基線 vs. 體質差異精準指導。採分層機制確保合規。")
]
for i, (title, exp) in enumerate(q2_items):
    ax.text(36.0, 72.8 - i * 3.3, f"• {title}:", fontsize=6.8, fontweight='bold', color=PRIMARY_BLUE, zorder=4)
    ax.text(37.5, 71.3 - i * 3.3, exp, fontsize=6.4, color=TEXT_MUTED, zorder=4)

# 3.3 十個深度問題
ax.text(36.0, 61.8, "3.3 十個深度理解問題維度 (Q3 覆蓋率)", fontsize=7.5, fontweight='bold', color=PRIMARY_BLUE, zorder=4)
ax.text(36.0, 59.2, "涵蓋 Why / What-if / Trade-off / Failure Case / Evidence / Comparison / Design\nDecision / Real-world 等維度，建立完整未知食物降級與飲食失調攔截邏輯。", fontsize=6.3, color=TEXT_MAIN, linespacing=1.2, zorder=4)

# -------------------------------------------------------------
# 模組 4: Proposed Scheme 系統架構與流程 (中下, X: 34.5, Y: 2, W: 32, H: 53)
# -------------------------------------------------------------
draw_card(34.5, 2, 32, 53, "Proposed Scheme：系統架構與演算法 (4.1-4.4)", 4)

# 4.1 八大模組串接流水線
ax.text(36.0, 50.5, "4.1 八大模組端到端處理管線 (① ~ ⑧)", fontsize=7.5, fontweight='bold', color=PRIMARY_BLUE, zorder=4)

modules_8 = [
    ("① 用戶情境", "文字/語音日常對話"),
    ("② 輸入處理", "繁簡正規化 + 4大意圖分類"),
    ("③ 規劃推理 Agent", "LLM 任務拆解 + 記憶管理"),
    ("④ 資料檢索層", "台灣DB (優先) + USDA API + 向量庫"),
    ("⑤ 分析引擎", "Mifflin-St Jeor TDEE + 區間熱量估算"),
    ("⑥ 領域知識庫", "飲食指南標準 + 份量參照 + 安全規則"),
    ("⑦ 決策建議", "熱量缺口分析 + 替代品建議 + 警示"),
    ("⑧ 輸出互動", "結構化 Markdown + 區間展示 + 追問")
]

for idx, (m_title, m_desc) in enumerate(modules_8):
    y_pos = 46.8 - idx * 2.8
    # 小編號框
    ax.add_patch(Rectangle((36.0, y_pos - 0.2), 9.5, 2.2, facecolor="#EBF3F8", edgecolor="#B0C8D8", linewidth=0.6, zorder=3))
    ax.text(36.5, y_pos + 0.9, m_title, fontsize=6.5, fontweight='bold', color=PRIMARY_BLUE, zorder=4)
    ax.text(46.2, y_pos + 0.9, f"→  {m_desc}", fontsize=6.2, color=TEXT_MAIN, zorder=4)

# 4.2 核心演算法 (Pseudocode 精要)
ax.add_patch(FancyBboxPatch((35.8, 4.0), 29.4, 18.5, boxstyle="round,pad=0,rounding_size=0.6", facecolor="#1E293B", edgecolor="#0F172A", linewidth=0.8, zorder=3))
ax.text(37.0, 20.5, "4.2 Algorithm 1: DietSense 核心控制邏輯 (Pseudocode)", fontsize=7.0, fontweight='bold', color="#38BDF8", zorder=4)

pseudo_lines = [
    "01: Receive user_query Q, user_profile P, daily_log D",
    "02: intent, foods ← parse_input(Q)  # intent in {log, query, analyze, rec}",
    "03: IF intent == 'log_food':",
    "04:   FOR each food in foods:",
    "05:     candidates ← search_MultiDB(food.name)  # TaiwanDB -> USDA",
    "06:     match, conf ← rank_candidates(candidates)",
    "07:     IF conf < 0.80: food ← trigger_clarification(food)",
    "08:     kcal_range ← estimate_uncertainty(match, food.portion, conf)",
    "09:     D.append(food, kcal_range, macros)",
    "10: IF safety_check(D.total_kcal, P) == 'DANGER':",
    "11:   RETURN fallback_safety_guidance(D, P)",
    "12: RETURN format_structured_response(D, P)"
]
for i, l in enumerate(pseudo_lines):
    ax.text(37.0, 18.8 - i * 1.25, l, fontsize=5.6, fontfamily='Consolas', color="#F1F5F9", zorder=4)

# -------------------------------------------------------------
# 模組 5: A–Z SOP 全流程映射矩陣 (右上, X: 68, Y: 43, W: 30, H: 47)
# -------------------------------------------------------------
draw_card(68, 43, 30, 47, "A–Z SOP 26 字母結構深度解析 (5.1-5.3)", 5)

az_rows = [
    ("A-B", "動機/痛點", "WHO 10億肥胖、自報誤差54%、85%放棄率"),
    ("C-D", "解法/方法", "DietSense 對話式 Agent + RAG + TDEE引擎"),
    ("E-F", "評估/成果", "500筆標註集、±20%準確>85%、省時60% (預期)"),
    ("G-H", "現況/瓶頸", "68億健康App市場但高認知負擔、LLM易幻覺"),
    ("I-J", "文獻/評析", "三世代演進梳理 (手動->視覺->LLM+Tool)"),
    ("K-L", "核心/架構", "從逐項填寫轉向AI主動驗證 (典範轉移)"),
    ("M-O", "方法/Gap", "Summary Table收斂出無本土化對話Agent之Gap"),
    ("PA-PD", "目標/設計", "以熱力學平衡為基，建立八大模組架構"),
    ("PE-PF", "模組/公式", "Mifflin-St Jeor TDEE、Atwater換算、區間推導"),
    ("PG-PI", "圖表/實作", "流程圖分流判定、帶行號演算法、安全閥門"),
    ("PJ-PK", "案例/貢獻", "「牛肉麵加蛋喝半碗湯」端到端案例、四大產出"),
    ("PL-PM", "模擬/檢驗", "20人7天實測、誤差率分析、熱量守恆檢驗"),
    ("Q-T", "指標/調優", "SUS>70、門檻0.80、不確定性區間擴展係數"),
    ("U-V", "產出/驗證", "全天多維報告生成、驗證降低60%記錄耗時"),
    ("W-Z", "回顧/展望", "專精台灣外食模糊輸入，未來邁向多模態")
]

cur_y = 85.5
for code, title, content in az_rows:
    ax.add_patch(Rectangle((69.2, cur_y - 0.2), 3.8, 1.8, facecolor="#F1F5F9", edgecolor="#CBD5E1", linewidth=0.5, zorder=3))
    ax.text(71.1, cur_y + 0.7, code, fontsize=5.8, fontweight='bold', color=PRIMARY_BLUE, ha='center', va='center', zorder=4)
    ax.text(73.5, cur_y + 0.7, f"{title}:", fontsize=6.2, fontweight='bold', color=PRIMARY_BLUE, zorder=4)
    ax.text(79.5, cur_y + 0.7, content[:22] + "...", fontsize=5.8, color=TEXT_MAIN, zorder=4)
    cur_y -= 2.65

# -------------------------------------------------------------
# 模組 6: 實驗評估規劃與最終交付 (右下, X: 68, Y: 2, W: 30, H: 39)
# -------------------------------------------------------------
draw_card(68, 2, 30, 39, "評估規劃與 Final Handover (6.1-6.3)", 6)

# 6.1 評估指標 Target 儀表盤
ax.text(69.5, 36.5, "6.1 提案預期指標 (Expected Targets)", fontsize=7.5, fontweight='bold', color=PRIMARY_BLUE, zorder=4)

targets = [
    ("±20% 準確率", "> 85%", "#E8F5E9", "#2E7D32"),
    ("耗時縮減", "60%", "#E0F2FE", "#0284C7"),
    ("SUS 滿意度", "> 70", "#FEF3C7", "#D97706"),
    ("在地覆蓋率", "> 90%", "#F3E8FF", "#7E22CE")
]

for idx, (lbl, val, bg_c, tx_c) in enumerate(targets):
    col = idx % 2
    row = idx // 2
    bx = 69.5 + col * 14.0
    by = 31.0 - row * 4.6
    ax.add_patch(FancyBboxPatch((bx, by), 13.0, 3.8, boxstyle="round,pad=0.2", facecolor=bg_c, edgecolor="none", zorder=3))
    ax.text(bx + 1.2, by + 1.9, lbl, fontsize=6.5, color=TEXT_MAIN, va='center', zorder=4)
    ax.text(bx + 11.8, by + 1.9, val, fontsize=8.5, fontweight='bold', color=tx_c, ha='right', va='center', zorder=4)

# 6.2 評估方法與 Baseline
ax.text(69.5, 20.5, "6.2 實驗評估方法 (Methodology)", fontsize=7.5, fontweight='bold', color=PRIMARY_BLUE, zorder=4)
eval_points = [
    "• 基準對照 (Baseline)：MyFitnessPal 繁體中文手動輸入紀錄。",
    "• 測試資料集：500 筆台式料理自報語料標註 (含地瓜球、珍奶、牛肉麵)。",
    "• 用戶研究：招募 20 位使用者連續 7 天雙盲測試紀錄耗時與滿意度。"
]
for i, p in enumerate(eval_points):
    ax.text(69.5, 18.2 - i * 2.2, p, fontsize=6.2, color=TEXT_MAIN, zorder=4)

# 6.3 最終交付物 (Final Handover Package)
ax.add_patch(Rectangle((69.2, 3.5), 27.6, 7.5, facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=0.8, zorder=3))
ax.text(70.2, 9.2, "6.3 Final Handover 交接保證 (GitHub 已推上)", fontsize=6.8, fontweight='bold', color=PRIMARY_BLUE, zorder=4)
handover_txt = (
    "• GitHub: https://github.com/yenyen0921/DietSense\n"
    "• 完整代碼庫：src/ (Agent, Retrieval, Analytics, Log, Gradio Web UI)\n"
    "• 完整交接規格文件：README.md, DESIGN.md, openspec.yaml"
)
ax.text(70.2, 5.0, handover_txt, fontsize=5.8, color=TEXT_MUTED, linespacing=1.3, zorder=4)

# 儲存資訊圖表
OUT_PNG = r"C:\Users\lab52\.antigravity-ide\DietSense\docs\DietSense_Infographic_A4_Landscape.png"
OUT_PDF = r"C:\Users\lab52\.antigravity-ide\DietSense\docs\DietSense_Infographic_A4_Landscape.pdf"

plt.savefig(OUT_PNG, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
plt.savefig(OUT_PDF, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()

print(f"✅ Infographic PNG saved to: {OUT_PNG}")
print(f"✅ Infographic PDF saved to: {OUT_PDF}")
