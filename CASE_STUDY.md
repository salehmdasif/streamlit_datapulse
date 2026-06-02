# Case Study: DataPulse - Universal Data Analytics Dashboard

> A self-service analytics platform that transforms raw, messy business data into clean insights - without writing a single line of code.

---

## Client / Context

The target user is any business professional who regularly works with data exports - a marketing manager downloading Meta Ads reports, an operations lead tracking monthly budgets, an HR coordinator managing employee records, or a sales analyst reviewing order history. These people have the data. They don't have the tools, the time, or the technical depth to clean and analyze it themselves.

The broader context: data literacy is rising, but the gap between "having data" and "understanding data" remains wide. Most business professionals can export a CSV. Very few know what to do with it once it's open in Excel and half the columns are empty, some numbers have dollar signs, and three rows appear to be duplicates.

This project was designed to close that gap - an intelligent, self-service analytics layer for non-technical data owners.

---

## The Challenge

Business data is almost never analysis-ready when it leaves its source system. Ad platform exports embed currency symbols in numeric fields. CRM downloads have blank rows where a customer didn't fill in a field. HR systems encode the same "yes/no" value three different ways across different records. Finance spreadsheets have column names with spaces and mixed capitalisation that break any standard parser.

Before any insight can be generated, this data must be cleaned - and cleaning it manually is slow, error-prone, and requires technical knowledge that most business users don't have.

The secondary challenge: even after cleaning, users rarely know which analysis to run. A marketing professional needs ROAS and CTR comparisons. A finance manager needs budget-versus-actual variance. An HR leader needs attrition rates by department. A generic analytics tool gives them charts. What they need is context.

### Key Pain Points

- **Data quality friction:** Every analysis project begins with 30–60 minutes of manual cleaning before any real work can start
- **Domain blindness:** Generic tools don't know whether you're looking at ad data or HR data - so they give you the same generic charts regardless
- **Statistical inaccessibility:** Correlation analysis, regression, and hypothesis testing are powerful tools that most business professionals never use because they require statistical knowledge to interpret
- **Tool complexity:** Enterprise BI tools (Tableau, Power BI) require significant setup, licensing costs, and training before delivering value

---

## The Approach

The core design question was: what does the pipeline look like when you assume the user has zero technical knowledge and potentially messy data?

The answer was a **linear, step-by-step pipeline** - not a blank canvas that overwhelms, but a guided flow that takes the user from raw data to actionable insight one step at a time. Each step builds on the previous one. Nothing in step 4 runs until step 2 is complete.

### Discovery Phase

The first design constraint identified was: **the cleaning must be transparent**. Users need to see exactly what changed and why. A black-box cleaner that silently modifies their data would destroy trust. Every action needed to be logged and displayed.

The second constraint: **user control within sensibility**. The engine auto-detects issues and proposes reasonable defaults, but the user chooses how to handle each problem. They can fill missing values with the mean, or drop the rows, or use the median. The engine never acts unilaterally without showing the user what it found.

### Architecture Decision

**Option 1:** Single-file Streamlit app with inline functions.
*Rejected:* Unmaintainable. Analysis logic mixed with UI code is impossible to test and extend.

**Option 2:** Modular architecture with one Python module per responsibility.
*Chosen:* Each module (`cleaner.py`, `profiler.py`, `eda.py`, `analyzer.py`, `domain_insights.py`) contains zero Streamlit imports. They are pure computation - testable, reusable, and independently deployable. `main.py` acts as the controller, calling modules and rendering results.

This decision also made domain intelligence cleanly extensible: adding an E-commerce domain requires adding one class to `domain_insights.py` and one conditional block in `main.py`. Nothing else changes.

### Engineering Priorities

1. **Transparency over automation:** Every cleaning action is logged. Every statistical result is explained in plain English alongside the number.
2. **Modularity over brevity:** Slightly more files, but each has a single, clear responsibility.
3. **Correctness over speed:** Regression uses StandardScaler before fitting (coefficients are comparable across features). Hypothesis testing uses `statsmodels` OLS (full statistical output, not just scikit-learn's limited regression object).

---

## What Was Built

DataPulse is a five-step interactive web application that handles the complete data analytics lifecycle:

1. Accept data from any source (file upload, URL, or bundled samples)
2. Automatically clean it and explain every change made
3. Profile the dataset - classify columns, detect the business domain, score data quality
4. Run any combination of: correlation analysis, group comparison, trend analysis, linear regression, and OLS hypothesis testing
5. Activate domain-specific insights - Winning Ad Selector for marketing data, revenue analysis for sales data, budget variance for finance, attrition analysis for HR

### Core Capabilities

- **Auto Cleaning Engine:** 6 categories of data quality issues detected and resolved with full reporting
- **Domain Intelligence:** 4 business domains with tailored KPIs and analysis views that activate automatically
- **Statistical Analysis:** 5 analysis types including hypothesis testing with per-feature p-values, confidence intervals, and t-statistics
- **Flexible Architecture:** Adding a new domain, chart type, or analysis method requires changes to exactly one module

### Technical Highlights

- **IQR-based outlier detection** with three resolution strategies (cap, remove, flag) implemented without any ML library dependency
- **Keyword-based domain heuristic** that maps column name vocabulary to business context - flexible enough to handle column name variations across different data exports
- **StandardScaler regression pipeline** ensuring all regression coefficients are interpretable on the same scale regardless of the original unit differences between features
- **Deep copy pattern** throughout the cleaning pipeline ensures the original uploaded data is never mutated - users can reset and re-clean at any point

---

## Results & Impact

| Capability | Without DataPulse | With DataPulse |
|---|---|---|
| Time to clean a typical 30-row dataset | 20–40 minutes manual | Under 60 seconds |
| Data quality visibility | None - issues found during analysis | Full report before analysis begins |
| Domain-specific insights | Requires custom analyst work | Auto-activated from column names |
| Statistical analysis accessibility | Requires R or Python knowledge | One click with plain-English output |
| Reproducibility | Manual steps, hard to repeat | Deterministic pipeline, same input = same output |

DataPulse demonstrates that a well-architected analytics pipeline does not need to be complex to be powerful. The value is in the design decisions - transparent cleaning, domain awareness, and statistical rigour - not in the volume of features.

---

## Lessons Learned

### What Went Well

- The modular architecture paid dividends immediately - testing each module independently was clean and fast, and adding Phase 4 domain intelligence required no changes to Phases 1–3
- The decision to make the Cleaning Report explicit and transparent proved to be the most impactful UX choice - it turns a black-box process into something the user can trust and verify
- Plotly's flexibility for custom styling made it possible to match the dark sidebar / Inter font design language without fighting the charting library

### What I Would Do Differently

- **Smarter column mapping:** The current domain detection uses exact keyword matching. A production version would use fuzzy matching or a small embedding model to handle column names like `"Monthly Expenditure"` mapping to the finance domain even without an exact keyword match
- **Async cleaning for large files:** The current pipeline is synchronous - for files above 10,000 rows, the cleaning step has noticeable latency. A background task queue (e.g., Celery or async Streamlit) would handle this more gracefully
- **Export report as PDF:** The cleaning report and analysis results should be downloadable as a formatted PDF for sharing with stakeholders who won't visit the app directly

---

## Technologies Used

Python 3.11, Streamlit, Plotly, Pandas, NumPy, Scikit-learn, Statsmodels, SciPy, Git, GitHub, Streamlit Community Cloud

---

## Want to Discuss This Project?

> I'm available for a private walkthrough, technical deep-dive, or to discuss how this architecture can be adapted for a specific client use case.

**LinkedIn:** [linkedin.com/in/salehmdasif](https://linkedin.com/in/salehmdasif)
**Email:** salehmdasif@gmail.com
**Portfolio:** [asif.ravelweb.com](https://asif.ravelweb.com)
