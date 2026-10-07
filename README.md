# E-commerce Customer & Product Analysis

SQL, Python, and Power BI analysis of ~96K delivered orders from the
Olist Brazilian e-commerce marketplace (Sep 2016 - Oct 2018 dataset,
analyzed for Jan 2017 - Aug 2018).

## Overview

This project analyzes customer behavior, product performance, and revenue
trends for a Brazilian e-commerce marketplace, using PostgreSQL for data
modeling, Python for customer segmentation and cohort analysis, and Power
BI for an executive dashboard. All numbers are cross-validated across
SQL, Python, and the dashboard.

**Dataset:** [Olist Brazilian E-commerce (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
— 9 relational tables, ~100K orders.

## Dashboard

![Dashboard](dashboard/dashboard_screenshot.png)

[Download the PDF](dashboard/ecommerce_dashboard.pdf) | [Power BI file](dashboard/ecommerce_dashboard.pbix)

## Key Findings

1. **Revenue grew 143% year-over-year but growth has stalled.** Revenue
   rose from R$3.47M (Jan-Aug 2017) to R$8.45M (Jan-Aug 2018), but the
   3-month rolling average has fallen ~11% since peaking in May 2018.

2. **Only 3.0% of customers ever place a second order.** Despite this,
   "Big first order" customers (one large purchase, recent or lapsed)
   make up 37.6% of customers but **68.3% of revenue**. Growth depends
   almost entirely on acquiring new customers who spend big on their
   first order, not on repeat purchasing.

3. **Cohort retention confirms this at scale.** Every monthly cohort
   from Jan 2017 to Aug 2018 shows under 1% retention in every
   subsequent month, with no exceptions. This is a structural pattern
   across the whole customer base, not a few weak months.
   Orders delivered 4-7 days late average a 2.10 review score (and 1.70 when 8+ days late), vs 4.32 for orders delivered 8+ days early. Only 6.7% of orders arrive late, but they account for roughly
   a third of all 1-2 star reviews.

5. **Revenue is diversified across product categories** (top category is
   only 9.2% of revenue) but concentrated by seller in several states —
   a single seller in each of Bahia, Pernambuco, and Espírito Santo each account for
   over half their state's revenue, versus under 15% in São Paulo,
   Brazil's largest seller base.

## Recommendations

- **Target "Big first order, lapsed" customers** (20,552 people, 39.9%
  of revenue, average 334 days inactive) with a win-back campaign —
  the single largest revenue segment and the clearest retention
  opportunity.
- **Prioritize orders at risk of 4+ day delays** with proactive
  notifications, since they drive a disproportionate share of negative
  reviews.
- **Recruit backup sellers** in states where one seller carries the
  majority of regional revenue, to reduce single-seller dependency risk.

  ## AI Query Assistant

An extension to this project: a natural-language interface to the same
Olist database, built with the Gemini API. Ask a business question in
plain English, and it generates SQL, runs it safely, charts the result,
and writes a short insight, all in one response.

**Try it:** [[demo video link](https://youtu.be/9L-60VxdE1U)] *(1-2 min walkthrough)*

### How it works
Question → SQL generation (LLM) → Safety validation → Read-only execution
→ Auto-chart → Insight generation (LLM) → Streamlit UI


1. The question and a schema/business-rules prompt (built from the same
   cleaning rules used in `notes.md` — delivered orders only, the
   Jan 2017-Aug 2018 window, `customer_unique_id` over `customer_id`,
   aggregating payments/reviews before joining) are sent to Gemini,
   which returns one SQL query.
2. The query is validated before it ever touches the database: it must
   be a single `SELECT`/`WITH` statement, contain no write/schema
   keywords, and have no chained statements.
3. It then runs through a **read-only PostgreSQL role**
   (`assistant_readonly`), which has `SELECT`-only privileges at the
   database level. This is independent of the validation step above —
   even if the validator had a gap, the database itself would refuse
   a write.
4. Results are auto-charted (line chart for time series, bar chart for
   categories, no chart for single values) and summarized in 2-3 plain
   sentences by a second Gemini call, instructed to use only numbers
   present in the actual query result.
5. Off-topic or unanswerable questions are explicitly refused by the
   model rather than answered with invented data.

### Accuracy

Evaluated against a 20-question benchmark I wrote, covering
aggregations, multi-table joins, time-series grouping, and two
adversarial tests (a prompt-injection attempt and an off-topic
question). Each question has a reference SQL query I wrote independently
and verified against the database before scoring.

**Result: 20/20 (100%)** — see [`assistant/eval_results.csv`](assistant/eval_results.csv)
and [`assistant/eval_set.py`](assistant/eval_set.py).

One early iteration surfaced a real bug this way: the assistant's
generated SQL used `ROUND()` on a `double precision` value, which
PostgreSQL rejects without an explicit cast — the same type issue I'd
handled with `::numeric` in my own queries. Adding that rule to the
assistant's prompt fixed it, and it's now part of the business-rules
context every query is generated against.

### Safety measures

- **Read-only database role**, separate from the main analysis user,
  with `SELECT`-only grants enforced at the database level.
- **Query validation layer** (`assistant/sql_safety.py`): rejects
  anything that isn't a single `SELECT`/`WITH` statement, blocks
  write/schema keywords, and caps result size with an automatic `LIMIT`.
- **Statement timeout** on every query, so a runaway query can't hang
  the app.
- **Explicit refusal** for questions outside the database's scope,
  tested against a direct prompt-injection attempt in the eval set.
- **Retry logic with model fallback**: the free-tier API is rate-limited
  and occasionally overloaded (503s); the assistant retries with
  backoff and falls back to a second model before giving up gracefully.

### Tech stack

Python, Google Gemini API (`gemini-3.8-flash` / `gemini-3.7-flash`
fallback), PostgreSQL (read-only role), Streamlit, pandas, Matplotlib.

### Limitations

- Runs on Gemini's free tier, which is rate-limited (20 requests/day
  per model), so it isn't deployed publicly — a public demo would
  exhaust the quota within a few questions. Run it locally, or watch
  the demo video.
- Evaluated on 20 questions I designed; it isn't guaranteed to handle
  every possible phrasing or edge case equally well.
- Insight generation is a secondary LLM call and can occasionally be
  unavailable under load — when it is, the data table and chart still
  render correctly, so the core result is never lost.

### Run it locally

```bash
cd assistant
pip install -r requirements.txt
# Add a .env file with GEMINI_API_KEY and a read-only DB_URL
streamlit run app.py
```

## Tech Stack

- **SQL** (PostgreSQL): data modeling, joins, window functions
  (`RANK`, `NTILE`, `LAG`, running totals), CTEs
- **Python** (pandas, seaborn, matplotlib): RFM segmentation, cohort
  retention analysis
- **Power BI**: executive dashboard with KPIs, trends, and segments
- **Git/GitHub**: version control

## Repository Structure
├── sql/ 10 analytical queries (Q1-Q10), each answering a specific business question
├── notebooks/ RFM segmentation and cohort retention (Jupyter)
├── dashboard/ Power BI file, PDF export, screenshots
├── notes.md Full findings log and data cleaning decisions
└── load_data.py Loads raw CSVs into PostgreSQL


## How to Run

1. Download the [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
   into a `data/` folder.
2. Create a PostgreSQL database named `olist`.
3. Add a `.env` file with `DB_URL=postgresql+psycopg2://user:password@localhost:5432/olist`.
4. Run `python load_data.py` to load the data.
5. Run queries in `sql/` in order, or open the notebook in `notebooks/`.

## Data Cleaning & Assumptions

- Revenue = item price + freight, delivered orders only (97.0% of orders).
- Analysis window: Jan 2017 - Aug 2018 (earlier/later months have too
  few orders to be reliable).
- Customer identity uses `customer_unique_id`, not `customer_id` (which
  changes with every order).
- Payments and reviews are aggregated to one row per order before
  joining, since some orders have multiple payment or review rows.

Full data validation and cleaning notes: [notes.md](notes.md)

## Limitations

- Findings show association, not proven causation (e.g., late delivery
  and review scores).
- Reviews are self-selected — only customers who chose to leave one are
  included.
- Repeat-purchase and RFM segments reflect a 20-month window; longer-term
  behavior isn't captured.