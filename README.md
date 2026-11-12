# DietSense — Daily Calorie Intake AI Agent

> A conversational Domain AI Agent for daily calorie tracking, built with LLM + RAG + Taiwan Food Database.

## 專題簡介

DietSense 是一個以自然語言對話方式追蹤每日飲食熱量的 Domain AI Agent。  
只需告訴它「我剛剛吃了一碗牛肉麵加蛋」，它就能自動估算熱量、分析巨量營養素、並根據你的目標提供個人化建議。

**核心理念：AI Agent + Nutrition Domain Knowledge + Data Analytics + Real-World Application**

---

## Features

- **自然語言記錄**：直接用中文描述飲食，無需手動搜尋資料庫
- **多源資料庫查詢**：整合 USDA FoodData Central + 台灣食品成分資料庫
- **不確定性量化**：提供熱量範圍（如 320–420 kcal），而非單一數字
- **個人化 TDEE 計算**：根據年齡、體重、活動量計算每日能量需求
- **安全機制**：偵測過度限制飲食，提供警示
- **台灣在地化**：覆蓋夜市、小吃、傳統料理

---

## System Architecture

```
User Input (自然語言)
      ↓
Intent Classifier → [log_food / query / analyze / recommend]
      ↓
Planner & Reasoning Agent (LLM)
      ↓
Data Retrieval ──→ USDA API / Taiwan Food DB / RAG Vector Store
      ↓
Analytics Engine ──→ Calorie Calc / Macro Analysis / TDEE
      ↓
Domain Knowledge ──→ Dietary Guidelines / Safety Rules
      ↓
Response Generator
      ↓
Output (文字 + 圖表 + 建議)
```

---

## Installation

```bash
# 1. Clone
git clone https://github.com/yenyen0921/DietSense.git
cd DietSense

# 2. 安裝套件
pip install -r requirements.txt

# 3. 設定 API Key
cp .env.example .env
# 在 .env 填入：
# OPENAI_API_KEY=sk-...
# USDA_API_KEY=...

# 4. 執行
python src/agent.py
```

---

## How to Run

### CLI 模式

```bash
python src/agent.py
```

```
DietSense > 我中午吃了一碗滷肉飯和一個茶葉蛋
→ 記錄成功！
  滷肉飯（200g）：約 380–450 kcal
  茶葉蛋（55g）：約 70 kcal
  本餐小計：450–520 kcal
  今日累計：650–720 kcal / 目標 2100 kcal
```

### Web UI 模式

```bash
python src/app.py
# 開啟瀏覽器：http://localhost:7860
```

---

## Project Structure

```
DietSense/
├── README.md
├── DESIGN.md              # 系統設計文件
├── openspec.yaml          # OpenAPI 3.1 規格（DIC3 新增）
├── requirements.txt
├── .env.example
├── src/
│   ├── agent.py           # 主 Agent（含意圖分類、NER、安全機制）
│   ├── retrieval.py       # 資料庫查詢（USDA + 台灣食品 DB）
│   ├── analytics.py       # 熱量計算 & TDEE & 安全檢查
│   ├── log.py             # 飲食日誌持久化（SQLite）
│   └── app.py             # Web UI（Gradio）
├── data/
│   ├── taiwan_food_db.json       # 台灣食品成分資料庫
│   └── portion_reference.json    # 份量對照表
├── docs/
│   ├── Introduction_refactor.md  # 緒論重構（A2Z G–L）
│   ├── RelatedWork_refactor.md   # 相關研究重構（A2Z M–O）
│   ├── Abstract_A_to_F.md        # A–F 六段式摘要完整版
│   ├── Abstract_500.md           # 500 字專業摘要
│   ├── Abstract_300.md           # 300 字精簡摘要
│   ├── Abstract_IEEE_EN.md       # IEEE 英文 Abstract
│   ├── DietSense_Infographic_A4_Landscape.png  # 資訊圖表
│   └── DietSense_Infographic_A4_Landscape.pdf
├── scratch/
│   └── generate_infographic.py   # 圖表產生腳本
└── tests/
    ├── test_analytics.py
    └── test_full.py
```

---

---

## References

- WHO (2025). Obesity and overweight fact sheet.
- USDA FoodData Central: https://fdc.nal.usda.gov/
- 衛生福利部食品藥物管理署台灣食品成分資料庫
- Mifflin, M. D., et al. (1990). A new predictive equation for resting energy expenditure in healthy individuals. *AJCN*.

---

*課程：AIoT 應用專題 | 學期：2026 秋季*

