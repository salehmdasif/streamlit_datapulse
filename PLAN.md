# DataPulse — Universal Data Analytics Dashboard

### Portfolio Project | Author: Abu Salah Mohammad Asif

---

## Project Purpose

A portfolio-grade, interactive data analytics web application built with Python and Streamlit.

**Goal:** Demonstrate end-to-end data analytics capability — from raw/dirty data ingestion, through automated cleaning, to deep statistical analysis and visual insights — for any structured tabular dataset.

**Not for production. Built to show clients what I can do with data.**

---

## What Makes This Different from the Old Version

| Old Version                | New Version (DataPulse)                       |
| -------------------------- | --------------------------------------------- |
| Assumed clean data         | Handles raw, dirty, unprocessed data          |
| Only Meta Ads data         | Any structured tabular dataset                |
| Basic charts               | Rich EDA + statistical analysis               |
| No cleaning step           | Auto Data Cleaning Engine with full report    |
| No domain detection        | Smart domain detection with tailored insights |
| Plain Streamlit default UI | Custom dark-sidebar branded UI                |

---

## Tech Stack

- **Python 3.x**
- **Streamlit** — UI framework
- **Pandas** — data manipulation & cleaning
- **NumPy** — numerical operations
- **Scikit-learn** — linear regression, scaling
- **Statsmodels** — hypothesis testing, OLS
- **Matplotlib / Seaborn** — charts & heatmaps
- **Plotly** — interactive charts (new addition)

---

## App Architecture (Modules)

```
DataPulse/
├── main.py                  # App entry point, page routing
├── requirements.txt
├── data/
│   └── samples/             # Pre-loaded sample datasets (4 domains)
│       ├── sample_meta_ads.csv
│       ├── sample_sales.csv
│       ├── sample_finance.csv
│       └── sample_hr.csv
├── modules/
│   ├── cleaner.py           # Auto Data Cleaning Engine
│   ├── profiler.py          # Data Profiling & Domain Detection
│   ├── eda.py               # Exploratory Data Analysis
│   ├── analyzer.py          # Statistical Analysis (correlation, regression)
│   ├── visualizer.py        # All chart/plot functions
│   └── domain_insights.py   # Domain-specific logic (Meta Ads, Sales, etc.)
└── assets/
    └── style.css            # Custom CSS for branding
```

---

## App Flow (Step by Step)

```
[Step 1] Data Ingestion
    → Upload CSV/Excel  OR  paste URL  OR  load sample dataset

[Step 2] Auto Cleaning Engine (NEW)
    → Detect & report issues
    → Apply cleaning with user choices
    → Show Cleaning Report (before vs after)

[Step 3] Data Profile (NEW)
    → Column types (numeric, categorical, datetime)
    → Data quality score
    → Auto domain detection

[Step 4] EDA — Exploratory Data Analysis
    → Data preview, shape, dtypes
    → Missing value report
    → Summary statistics
    → Distribution plots
    → Correlation heatmap

[Step 5] Analysis (user selects columns & method)
    → Correlation analysis
    → Trend analysis (if datetime column exists)
    → Group/Category comparison
    → Linear Regression + Feature Importance
    → Hypothesis Testing (p-value, t-stat, CI)

[Step 6] Domain Intelligence (auto-activated based on domain)
    → If Marketing/Ads: Winning Ad Selector, ROAS/CTR/CPC analysis
    → If Sales: Top products, revenue trends
    → If Finance: Profit/loss, budget vs actual
    → If HR: Attrition risk, salary bands
    → If Unknown: Generic insights only
```

---

## Module Details

### Module 1 — Auto Data Cleaning Engine (`cleaner.py`)

Detects and fixes the following automatically:

| Issue                      | Detection                      | Fix Options                                                         |
| -------------------------- | ------------------------------ | ------------------------------------------------------------------- |
| Missing values             | Count & % per column           | Drop rows / Fill mean / Fill median / Fill mode / Fill custom value |
| Duplicate rows             | Exact duplicate detection      | Auto-remove                                                         |
| Wrong data types           | e.g. numbers stored as strings | Auto-convert                                                        |
| Whitespace in column names | Strip & lowercase              | Auto-fix                                                            |
| Outliers (numeric)         | IQR method                     | Flag only / Cap / Remove                                            |
| All-null columns           | 100% missing                   | Drop column                                                         |

**Output:** A "Cleaning Report" showing exactly what was changed (rows removed, columns fixed, nulls filled, etc.)  
**User control:** User can accept defaults or choose options before applying.

---

### Module 2 — Data Profiler (`profiler.py`)

After cleaning, auto-profile the dataset:

- **Column classification:**
  
  - Numeric (continuous)
  - Categorical (low cardinality)
  - Datetime
  - Boolean / Binary
  - High-cardinality text (name/ID columns — excluded from analysis)

- **Data Quality Score:** 0–100 based on completeness, uniqueness, type consistency

- **Domain Detection (keyword-based heuristic):**

| Detected Domain | Trigger Keywords in Column Names                                                     |
| --------------- | ------------------------------------------------------------------------------------ |
| Marketing / Ads | `roas`, `ctr`, `cpc`, `cpm`, `impressions`, `clicks`, `spend`, `ad_name`, `campaign` |
| Sales           | `revenue`, `sales`, `order`, `product`, `quantity`, `price`, `discount`              |
| Finance         | `profit`, `loss`, `expense`, `budget`, `balance`, `income`, `cost`                   |
| HR / People     | `employee`, `salary`, `attrition`, `department`, `tenure`, `age`, `gender`           |
| E-commerce      | `sku`, `cart`, `checkout`, `conversion`, `return_rate`, `aov`                        |
| Unknown         | No strong keyword matches → Generic mode                                             |

---

### Module 3 — EDA (`eda.py`)

Standard EDA panels:

1. **Data Preview** — head(), shape, dtypes
2. **Missing Value Report** — table + bar chart (% missing per column)
3. **Summary Statistics** — describe() with formatting
4. **Distribution Plots** — histogram + box plot per numeric column (user selects)
5. **Correlation Heatmap** — full numeric correlation matrix as heatmap (Seaborn/Plotly)

---

### Module 4 — Statistical Analysis (`analyzer.py`)

User selects columns and analysis type:

1. **Correlation Analysis**
   
   - Select X and Y (numeric)
   - Pearson correlation coefficient
   - Scatter plot with trend line
   - Interpretation text (positive/negative/none + strength)

2. **Group Comparison**
   
   - Select 1 categorical + 1 numeric column
   - Bar chart: mean of numeric by category
   - Useful for: campaign type vs ROAS, product category vs revenue, etc.

3. **Trend Analysis** *(only if datetime column detected)*
   
   - Select date column + metric column
   - Line chart over time
   - Optional: 7-day rolling average overlay

4. **Linear Regression**
   
   - Select target variable + feature columns
   - StandardScaler applied automatically
   - Output: Coefficients, R², Feature Importance chart

5. **Hypothesis Testing**
   
   - OLS via statsmodels on selected regression
   - Output: p-value, t-statistic, std error, confidence interval per feature
   - Plain-English interpretation per feature

---

### Module 5 — Domain Intelligence (`domain_insights.py`)

Auto-activates if domain is detected. User can also manually select domain.

#### Marketing / Meta Ads Mode

- **Winning Ad Selector** (existing logic, kept & improved)
  - Filters: amount_spent > 100, ROAS ≥ 2, result_rate > 20%, etc.
  - User can adjust thresholds via sliders
- **Key Metrics Summary:** ROAS, CTR, CPC, CPR cards
- **Best & Worst performing ads** side by side

#### Sales Mode

- **Top 10 Products by Revenue**
- **Revenue by Category** (bar chart)
- **Discount vs Revenue correlation**

#### Finance Mode

- **Income vs Expense comparison**
- **Profit margin calculation**
- **Budget vs Actual variance**

#### HR Mode

- **Attrition rate**
- **Salary distribution by department**
- **Tenure vs Attrition scatter**

---

## What Data This Works Best For

### ✅ Best Performance

- **Marketing Analytics** — Meta Ads, Google Ads, email campaign exports
- **Sales & E-commerce** — order data, product performance, revenue reports
- **Financial Reports** — monthly P&L, budget sheets, expense logs
- **HR & People Data** — employee records, survey results, payroll data
- **Survey / Research Data** — any structured tabular output

### ⚠️ Works But Limited

- Mixed text + numeric data (text columns are excluded from analysis)
- Time-series data with irregular intervals

### ❌ Not Designed For

- Raw text / NLP datasets
- Image, audio, video data
- Datasets with more than 100,000 rows (Streamlit performance limit)
- Nested JSON or hierarchical data
- Real-time streaming data

---

## UI Design

- **Layout:** Dark sidebar (gray-900) + white content area
- **Font:** Inter
- **Colors:** Monochromatic (black/white/gray) with subtle blue accent for charts
- **No border-radius** anywhere
- **Sidebar contains:** App branding, step indicator, domain badge, file info
- **Main area:** Step-by-step sections, collapsible panels per module

---

## Sample Datasets (Bundled)

4 sample datasets will be included so anyone viewing the portfolio can try the app without their own data:

| Sample                | Rows | Domain    | Description                                             |
| --------------------- | ---- | --------- | ------------------------------------------------------- |
| `sample_meta_ads.csv` | ~200 | Marketing | Facebook ad campaign data with intentional dirty values |
| `sample_sales.csv`    | ~300 | Sales     | E-commerce order data with missing values & duplicates  |
| `sample_finance.csv`  | ~150 | Finance   | Monthly budget vs actual with outliers                  |
| `sample_hr.csv`       | ~250 | HR        | Employee records with mixed types & nulls               |

Each sample has **intentional data quality issues** to showcase the cleaning engine.

---

## Build Phases

### Phase 1 — Foundation & Cleaning Engine

- [ ] New folder structure
- [ ] `cleaner.py` — full cleaning engine
- [ ] Basic `main.py` with file upload + cleaning UI
- [ ] Cleaning report display

### Phase 2 — Profiler & EDA

- [ ] `profiler.py` — column classification + domain detection
- [ ] `eda.py` — all EDA panels
- [ ] Correlation heatmap (Plotly)

### Phase 3 — Analysis Engine

- [ ] `analyzer.py` — correlation, group comparison, trend, regression, hypothesis testing
- [ ] All charts via `visualizer.py`

### Phase 4 — Domain Intelligence

- [ ] `domain_insights.py` — Marketing, Sales, Finance, HR modes
- [ ] Winning Ad Selector with adjustable sliders

### Phase 5 — UI Polish & Sample Data

- [ ] Custom CSS styling
- [ ] 4 sample datasets with dirty data
- [ ] Final README with screenshots for portfolio

---

## Portfolio Value

When a client sees this app they will understand:

- Asif can ingest raw, messy data and clean it systematically
- Asif knows statistical analysis (correlation, regression, hypothesis testing)
- Asif can build interactive tools, not just static reports
- Asif understands multiple business domains (marketing, sales, finance, HR)
- Asif can communicate insights clearly through UI/UX choices

---

*Plan created: 2026-06-02*
*Author: Abu Salah Mohammad Asif | Ravelweb Ltd*
