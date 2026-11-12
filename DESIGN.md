# DESIGN.md — DietSense: Daily Calorie Intake AI Agent

> 本文件從 Proposal 階段開始建立，並在開發過程中持續更新。  
> 目標：使任何人能透過本文件理解、執行、驗證並繼續開發此系統。

**DIC3 更新（2026-11-11）：Openspec Refactor**
- 新增 [`openspec.yaml`](./openspec.yaml)：完整 OpenAPI 3.1 規格，含 5 cores / 3 trade-offs / 10 details / 八大模組 workflow
- 新增 [`docs/Introduction_refactor.md`](./docs/Introduction_refactor.md)：依 A2Z G–L 重構緒論
- 新增 [`docs/RelatedWork_refactor.md`](./docs/RelatedWork_refactor.md)：依 A2Z M–O 重構相關研究

---

## Problem

**核心問題：傳統熱量追蹤的認知負擔過高，導致 85% 使用者在 30 天內放棄。**

具體痛點：
- 使用者需手動搜尋龐大資料庫中的精確食物名稱
- 需估算精確份量（通常需磅秤，日常不可行）
- 需手動拆解複合料理（如牛肉麵、滷肉飯）為各食材
- 現有系統對台灣在地食物（夜市、小吃）資料嚴重缺乏

---

## Requirements

### Functional Requirements

| ID | 需求描述 | 優先級 |
|----|---------|-------|
| F1 | 以自然語言描述飲食，系統自動解析食物名稱與份量 | 高 |
| F2 | 查詢 USDA 及台灣食品成分資料庫，回傳熱量與巨量營養素 | 高 |
| F3 | 根據個人資料（年齡/性別/體重/身高/活動量）計算 TDEE | 高 |
| F4 | 追蹤每日各餐攝取，提供每日熱量總結 | 高 |
| F5 | 當資訊不足時，主動提問澄清（如份量不明確） | 中 |
| F6 | 提供熱量估算範圍（信賴區間），而非單一數字 | 中 |
| F7 | 偵測潛在飲食失調模式並提供警示 | 中 |
| F8 | 提供食物替換建議（低卡替代品） | 低 |

### Non-Functional Requirements

- **準確度**：標準食物熱量估算在 ±20% 誤差內達 85%+
- **回應時間**：一般查詢 < 3 秒
- **可用性**：SUS Score > 70
- **安全性**：不儲存用戶個人健康資料至外部伺服器（本地 DB）

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   DietSense System                      │
│                                                         │
│  ① User Interface (CLI / Web Chat)                      │
│        │                                                │
│  ② Input Processor                                      │
│     ├─ Language Normalizer                              │
│     └─ Intent Classifier                               │
│        │                                                │
│  ③ Planner & Reasoning Agent (LLM Core)                 │
│     ├─ Conversation Memory                              │
│     ├─ Tool Selector                                    │
│     └─ Clarification Generator                         │
│        │                                                │
│  ④ Data Retrieval Layer                                 │
│     ├─ USDA FoodData Central API                        │
│     ├─ Taiwan Food Composition DB                       │
│     └─ RAG Vector Store (local)                        │
│        │                                                │
│  ⑤ Analytics Engine                                     │
│     ├─ Calorie Calculator                               │
│     ├─ Macronutrient Analyzer                           │
│     ├─ TDEE/BMR Calculator                              │
│     └─ Uncertainty Quantifier                          │
│        │                                                │
│  ⑥ Domain Knowledge Base                                │
│     ├─ Dietary Guidelines (DRI / Taiwan)                │
│     ├─ Portion Reference Table                          │
│     └─ Safety Rules Engine                             │
│        │                                                │
│  ⑦ Response Generator                                   │
│     ├─ Natural Language Output                          │
│     └─ Visualization Builder                           │
└─────────────────────────────────────────────────────────┘
```

---

## Components

### ① User Interface
- **技術**：Python CLI（MVP）/ Gradio Web UI（後續）
- **輸入**：文字描述（支援中英混合）
- **輸出**：文字回應 + ASCII 圖表（CLI）/ HTML 圖表（Web）

### ② Input Processor
- **Language Normalizer**：處理繁簡中文、英文食物名稱
- **Intent Classifier**：分類用戶意圖
  - `log_food`：記錄飲食
  - `query_nutrition`：查詢食物營養
  - `analyze`：分析今日攝取
  - `recommend`：獲取建議

### ③ Planner & Reasoning Agent
- **LLM Backend**：GPT-4o（主）/ Gemini 1.5 Pro（備）
- **Conversation Memory**：儲存當日對話歷史與食物記錄
- **Tool Selector**：決定呼叫哪個資料庫/工具
- **Function Calling**：使用 OpenAI function calling 架構呼叫外部 API

### ④ Data Retrieval Layer
- **USDA FoodData Central API**：免費，900,000+ 食物項目
  - Endpoint: `https://api.nal.usda.gov/fdc/v1/foods/search`
- **台灣食品成分資料庫**：衛生福利部，6,000+ 台灣食物
  - 格式：CSV 下載，本地查詢
- **RAG Vector Store**：FAISS + sentence-transformers
  - 用於台式料理、夜市食物等特殊查詢

### ⑤ Analytics Engine
- **Calorie Calculator**：`kcal = portion_g × kcal_per_100g / 100`
- **Macronutrient Analyzer**：計算蛋白質/碳水/脂肪佔比
- **TDEE Calculator**：Mifflin-St Jeor BMR × 活動係數
- **Uncertainty Quantifier**：基於信心分數計算 ±margin

### ⑥ Domain Knowledge Base
- **Dietary Guidelines**：台灣每日飲食指南、DRI 標準
- **Portion Reference**：一碗/一份/一個的標準重量對照表
- **Safety Rules**：
  - `daily_kcal < 1200` → 危險警示
  - 連續 3 天攝取 < 70% TDEE → 飲食失調警示

### ⑦ Response Generator
- 結構化 Markdown 輸出
- 熱量範圍顯示（如：`預估 320–420 kcal`）
- 每日摘要表格

---

## Data

### Data Sources

| 資料來源 | 類型 | 項目數 | 取得方式 |
|---------|------|-------|---------|
| USDA FoodData Central | API | 900,000+ | 免費 API Key 申請 |
| 台灣食品成分資料庫 | CSV | 6,000+ | 衛福部官網下載 |
| 自建台式料理資料集 | JSON | 500+（預計） | 人工標註 |
| 用戶飲食記錄 | SQLite | 動態成長 | 本地生成 |

### Data Schema

```json
// 食物記錄項目 (FoodEntry)
{
  "id": "uuid",
  "timestamp": "2026-11-03T12:30:00",
  "meal_type": "lunch",
  "food_name": "台式牛肉麵",
  "portion_desc": "一碗",
  "portion_g": 500,
  "kcal_low": 420,
  "kcal_point": 520,
  "kcal_high": 620,
  "protein_g": 28,
  "carb_g": 65,
  "fat_g": 12,
  "source": "taiwan_food_db",
  "confidence": 0.75
}

// 用戶檔案 (UserProfile)
{
  "user_id": "uuid",
  "age": 22,
  "gender": "female",
  "weight_kg": 55,
  "height_cm": 162,
  "activity_level": "moderate",
  "goal": "maintain",
  "bmr": 1390,
  "tdee": 2154
}
```

---

## AI/Analytics

### LLM 使用策略

| 任務 | 方法 | 備註 |
|------|------|------|
| 意圖分類 | LLM zero-shot | 4 類別，準確率預期 >95% |
| 食物 NER | LLM few-shot + prompt | 抽取食物名、份量、餐別 |
| 資料庫排名 | Cosine similarity + LLM re-rank | 混合語意與規則 |
| 澄清問題生成 | LLM with template | 當 confidence < 0.8 |
| 回應生成 | LLM with structured output | JSON → 自然語言 |

### BMR/TDEE 計算

```python
# Mifflin-St Jeor 公式
BMR_male   = 10 * weight + 6.25 * height - 5 * age + 5
BMR_female = 10 * weight + 6.25 * height - 5 * age - 161

# 活動係數
activity_factors = {
    "sedentary":   1.2,   # 久坐，幾乎不運動
    "light":       1.375, # 輕度運動，每週 1-3 天
    "moderate":    1.55,  # 中度運動，每週 3-5 天
    "active":      1.725, # 高度運動，每週 6-7 天
    "very_active": 1.9    # 非常高強度運動或體力勞動
}
TDEE = BMR × activity_factors[activity_level]
```

---

## Domain Knowledge

### 關鍵營養學知識

1. **熱量換算**：碳水 4 kcal/g、蛋白質 4 kcal/g、脂肪 9 kcal/g、酒精 7 kcal/g
2. **AMDR 建議**：碳水 45-65%、蛋白質 10-35%、脂肪 20-35%
3. **安全下限**：女性 1200 kcal/天、男性 1500 kcal/天
4. **台灣飲食特色**：高碳水（米飯、麵食為主）、烹調方式影響熱量（炸 vs 蒸）

### 份量標準參照表

| 描述 | 標準重量 | 備註 |
|------|---------|------|
| 一碗白飯 | 200g | 約 280 kcal |
| 一碗麵（熟） | 200g | 依麵種類而異 |
| 一塊雞排（大） | 180g | 約 450-550 kcal（炸） |
| 一杯珍珠奶茶（大） | 700ml | 約 400-600 kcal |
| 一個茶葉蛋 | 55g | 約 70 kcal |

---

## Algorithm

```python
def diet_agent(query: str, user: UserProfile, log: DailyLog):
    intent = classify_intent(query)

    if intent == "log_food":
        entities = extract_food_entities(query)
        for food in entities:
            candidates = search_all_databases(food.name)
            match, confidence = rank_best_match(candidates, food)
            if confidence < 0.80:
                return ask_clarification(food)
            kcal_range = estimate_calories(match, food.portion, confidence)
            log.add(food, kcal_range)

    elif intent == "analyze":
        total = log.sum_calories()
        tdee = calculate_tdee(user)
        macros = log.macro_ratios()
        safety = check_safety(total, user)
        return generate_analysis(total, tdee, macros, safety)

    elif intent == "recommend":
        gap = log.sum_calories() - calculate_tdee(user)
        return generate_recommendation(gap, log, user)
```

---

## Implementation

### 技術選型

| 層級 | 技術 | 版本 |
|------|------|------|
| LLM Backend | OpenAI GPT-4o | API |
| 向量搜尋 | FAISS | 1.7.4 |
| 語意嵌入 | sentence-transformers | 2.7.0 |
| 資料庫 | SQLite | 內建 |
| Web UI | Gradio | 4.x |
| 資料處理 | pandas | 2.x |

### 專案結構

```
DietSense/
├── README.md
├── DESIGN.md
├── openspec.yaml          # OpenAPI 3.1 規格（DIC3 新增）
├── requirements.txt
├── .env.example
│
├── src/
│   ├── agent.py          # 主 Agent（含意圖分類、NER、安全機制）
│   ├── retrieval.py      # 資料庫查詢（USDA + 台灣食品 DB）
│   ├── analytics.py      # 熱量計算 & TDEE & 安全檢查
│   ├── log.py            # 飲食日誌持久化（SQLite）
│   └── app.py            # Web UI（Gradio）
│
├── data/
│   ├── taiwan_food_db.json       # 台灣食品成分資料庫
│   └── portion_reference.json    # 份量對照表
│
├── docs/
│   ├── Introduction_refactor.md  # 緒論重構（A2Z G–L）
│   ├── RelatedWork_refactor.md   # 相關研究重構（A2Z M–O）
│   ├── Abstract_A_to_F.md        # A–F 六段式摘要完整版
│   ├── Abstract_500.md           # 500 字專業摘要
│   ├── Abstract_300.md           # 300 字精簡摘要
│   ├── Abstract_IEEE_EN.md       # IEEE 英文 Abstract
│   ├── DietSense_Infographic_A4_Landscape.png
│   └── DietSense_Infographic_A4_Landscape.pdf
│
├── scratch/
│   └── generate_infographic.py   # 圖表產生腳本
│
└── tests/
    ├── test_analytics.py
    └── test_full.py
```

### How to Run

```bash
# 1. Clone repository
git clone https://github.com/yenyen0921/DietSense.git
cd DietSense

# 2. 安裝相依套件
pip install -r requirements.txt

# 3. 設定環境變數
cp .env.example .env
# 填入 OPENAI_API_KEY 和 USDA_API_KEY

# 4. 執行 CLI 版本
python src/agent.py

# 5. 執行 Web UI
python src/app.py  # 開啟 http://localhost:7860
```

---

## Results

> 本節將在實驗完成後填入，Proposal 階段為預期結果。

### Expected Results

| 指標 | 預期目標 | 測量方式 |
|------|---------|---------|
| 熱量估算準確率（±20%）| > 85% | 對照 USDA 標準值 |
| 食物記錄時間 | < 30 秒/餐 | 用戶計時測試 |
| SUS 可用性評分 | > 70 | 20 位用戶問卷 |
| 台式食物辨識覆蓋率 | > 90% | 自建測試集 |

---

## Limitations

1. **份量估算不確定性高**：純文字描述的份量估算誤差可達 ±30%，需用戶確認
2. **LLM 幻覺風險**：LLM 可能對不熟悉食物產生錯誤熱量，需資料庫驗證
3. **台式資料庫覆蓋不完整**：自建資料集初期僅 500 筆，仍有缺漏
4. **非醫療建議**：本系統不能替代專業營養師的臨床評估
5. **個人化限制**：TDEE 公式對運動員、孕婦、老年人可能失準

---

*最後更新：2026-11-12 | 版本：v0.2 (DIC3 Refactor)*

