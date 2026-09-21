## Load check
- Row counts: orders 99,441 | customers 99,441 | order_items 112,650 |
  order_payments 103,886 | order_reviews 99,224 | products 32,951 |
  sellers 3,095 | geolocation 1,000,163
- Date range: 2016-09-04 to 2018-10-17 (trend window to be set after monthly check)
- Statuses: delivered 96,478 | shipped 1,107 | canceled 625 | unavailable 609 |
  invoiced 314 | processing 301 | created 5 | approved 2

## Cleaning rules and assumptions
1. Revenue = item price + freight, delivered orders only (97.0% of orders).
2. Canceled and unavailable orders are analyzed separately; in-progress
   statuses are excluded from revenue.
3. Use customer_unique_id for people (99,441 customer_ids vs 96,096 real
   customers, so repeat buying is rare, about 3%).
4. 2,961 orders have >1 payment row: aggregate payments per order in a CTE
   before joining.
5. 547 orders have >1 review: keep the latest review per order before joining.

## Q1: Monthly revenue (sql/01_monthly_revenue.sql)

**Rules**
- Delivered orders only; revenue = item price + freight (in R$).
- Trend window: Jan 2017 - Aug 2018 (20 months). The 2016 months have 1-265
  orders, and Sep/Oct 2018 have no delivered orders.
- Jan 2017 MoM growth is NULL by design (the Dec 2016 base was 1 order).

**Key numbers**
- Nov 2017 is the peak: R$1,153,364 revenue, 7,289 orders.
- Orders rose ~63% vs Oct 2017 (4,478 -> 7,289), revenue rose 53.6%.
- Revenue per order fell from ~R$168 (Oct) to ~R$158 (Nov), about -6%.
- Dec 2017 fell 26.9% vs Nov but stayed above Oct (R$843K vs R$751K).
- Jan 2017 R$127K -> Jan 2018 R$1.08M, then flat at R$0.97M-1.13M/month
  through Aug 2018.

**Findings**
1. November 2017 is the biggest month. It is consistent with a
   Black Friday effect, but not yet confirmed (needs a daily-orders check).
2. Growth flattened in 2018. Hypothesis: with only ~3% repeat buyers, growth
   depends on new customers. Test this in the RFM and cohort analysis.

   ## Q2: Top 10 categories by revenue (sql/02_top_categories.sql)

**Rules**
- Delivered orders, Jan 2017 - Aug 2018; revenue = price + freight (R$).
- Category names come from the English translation table; if there is no
  translation, the Portuguese name is used (LEFT JOIN + COALESCE).
- An order with items from several categories counts once in each, so
  order counts do not add up to total orders.

**Key numbers**
- health_beauty is #1: R$1.41M (9.2% of revenue).
- Top 5 categories = 39.3% of revenue; top 10 = 62.4%.
- bed_bath_table has the most orders (9,267) but ~R$132 per order;
  watches_gifts has 5,491 orders but ~R$230 per order.
- Check: top-10 total implies ~R$15.4M overall, matching the sum of Q1.

**Findings**
1. Revenue is diversified: no category is above 10%.
2. Category rank by orders differs from rank by revenue because order
   value varies a lot (R$132 to R$230).
3. To test in RFM/cohorts: which first-purchase categories lead to
   repeat buying?

   ## Q3: Top 3 sellers per state (sql/03_top_sellers_by_state.sql)

**Rules**
- Delivered orders, Jan 2017 - Aug 2018; revenue = price + freight (R$).
- State = seller location, not customer location.
- RANK() OVER (PARTITION BY seller_state ORDER BY revenue DESC), filtered in
  an outer query because window functions can't be filtered where computed.
- States with <3 rows have <3 sellers with delivered sales in the window.

**Key numbers**
- 56 rows across 22 seller states.
- SP top 3 sellers: R$231K-247K each, only ~2.3-2.5% of SP revenue each.
- Top-seller share: PR 5.5%, MG 11.0%, RJ 14.6%, but BA 77.7%, PB 80.2%,
  PE 62.6%, ES 56.4%.
- MA, PI, PA, AM have one active seller each (100% share, tiny revenue).
- BA top seller: R$230.8K from 348 orders (~R$663/order vs ~R$160 marketplace
  average).

**Findings**
1. Seller concentration falls as state size rises: SP is diversified, while
   BA, PE, PB, and ES depend on one seller for more than half of revenue.
2. A single BA seller earns about as much as SP's best, on ~4x the average
   order value (likely high-ticket products; not verified).
3. Recommendation: recruit backup sellers in mid-sized dependent states
   (BA, PE, ES) to reduce supply risk.
4. Limitation: state = seller location; tiny-state percentages rest on
   small bases.