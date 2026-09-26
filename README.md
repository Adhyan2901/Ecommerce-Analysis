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

4. **Late delivery is strongly linked to poor reviews.** Orders delivered
   4+ days late average a 2.10 review score vs. 4.32 for orders 8+ days
   early. Only 6.7% of orders arrive late, but they account for roughly
   a third of all 1-2 star reviews.

5. **Revenue is diversified across product categories** (top category is
   only 9.2% of revenue) but concentrated by seller in several states —
   sellers in Bahia, Pernambuco, and Espírito Santo each account for
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