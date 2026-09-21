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

   ## Q4: Customer concentration (sql/04_customer_concentration.sql)

**Rules**
- Delivered orders, Jan 2017 - Aug 2018; revenue = price + freight (R$).
- Customer = customer_unique_id. 93,104 customers in the window.
- NTILE(5) on total spend; quintile 1 = top 20% of spenders.

**Key numbers**
- Top 20% of customers = 53.5% of revenue (R$8.23M of R$15.37M);
  top 40% = 73.5%; bottom 40% = 13.3%.
- Avg spend: top quintile R$442 vs bottom quintile R$40 (~11x).
- Cutoff to enter the top 20%: ~R$208 total spend.
- Avg orders per customer: 1.10 (top quintile) down to 1.00 (bottom).
- Largest single customer: R$13,664.
- Check: quintile revenue sums to R$15.37M, matching Q1 and Q2.

**Findings**
1. Revenue is concentrated but not 80/20: top 20% of customers = ~54%.
2. Top customers are mostly one-time big-basket buyers (1.10 orders), not
   loyal repeat buyers, so "VIP" here means high first-order value.
3. Recommendation: target high-value first-time buyers with a retention
   offer (post-purchase email, second-order incentive). Illustration only:
   if 5% of top-quintile customers bought once more at their average
   spend, that adds ~R$411K, about 2.7% of window revenue.
4. Limitation: spend is measured over a 20-month window with little
   repeat buying, so this measures order size more than customer loyalty.

   ## Q5: Repeat purchase

**Rules**
- Delivered orders, Jan 2017 - Aug 2018.
- Customer = customer_unique_id (customer_id changes with every order).

**Q5a: orders per customer (sql/05a_repeat_rate.sql)**
- 93,104 customers: 90,315 ordered once (97.00%), 2,562 twice (2.75%),
  227 three or more times (0.24%).
- Repeat customers = 2,789 (3.00%), placing 5,896 orders (6.1% of all
  orders), so about 2.1 orders each.
- Check: 93,104 customers matches Q4; 96,211 orders matches the sum of Q1.
- Caveat: 3.00% counts any second order within the 20-month window, so
  customers who first bought late had less time to return.

**Q5b: timing of the second order (sql/05b_days_to_second_order.sql)**
- 93,104 customers, 2,789 repeat (3.00%); matches Q5a.
- 90-day repeat rate (first order before 2018-06-03): 2.28%. Not comparable
  with 3.00%, which counts any second order in the whole window.
- 29.7% of repeaters (~830) ordered again on the same day as their first
  order. This may be a split basket rather than a return visit (not
  verifiable from the data).
- 50.5% of repeaters ordered again within 30 days; median gap is 29 days
  (includes same-day repeats).

**Findings**
1. Repeat buying is rare (3.0% ever, 2.3% within 90 days) and happens early:
   half of repeaters return within a month.
2. About 30% of repeats are same-day, so the true return-visit rate is nearer
   2% (estimate: 2,789 - ~830 = ~1,960 customers, ~2.1%).
3. Together with Q1 (revenue flat through 2018) and Q4 (top customers are
   mostly one-time buyers), this suggests growth depends on acquiring new
   customers.
4. Recommendation: test a retention nudge (email or voucher) in the first
   30 days after delivery. This is a hypothesis; the data can't show whether
   a nudge would change behavior.

   ## Q6: Delivery delay vs review score (sql/06_delivery_delay_vs_reviews.sql)

**Rules**
- Delivered orders, Jan 2017 - Aug 2018, with a delivery date and a review.
- One review per order (latest, via ROW_NUMBER), because 547 orders have
  more than one review.
- delay_days = delivered date - estimated date (negative = early).
- 95,560 orders analyzed = 99.3% of 96,211 delivered orders; 651 dropped
  (no review or no delivery date).

**Key numbers**
- 92.0% of orders arrive before the estimate; 6.7% (6,378) arrive late.
- Avg score: early 8+ days 4.32 | early 1-7 4.20 | on date 4.03 |
  late 1-3 days 3.29 | late 4-7 days 2.10 | late 8+ days 1.70.
- 1-2 star share: 9.0% (early 8+) rising to 79.3% (late 8+).
- Early/on-time avg ~4.29 vs late avg ~2.27 (weighted by orders; calculated
  from the rounded bucket values).
- Late orders are 6.7% of orders but ~a third of 1-2 star reviews (~32%,
  estimated from rounded percentages).

**Findings**
1. Late delivery is strongly associated with low scores. The drop is
   sharpest once the estimate is missed and continues as delay grows.
2. Most orders (92%) arrive early, so the late minority does
   disproportionate damage to ratings.
3. Recommendation: prioritize orders at risk of being 4+ days late with
   proactive notifications or compensation. Hypothesis; not tested.
4. Limitations: association not causation (late orders may also have other
   problems); only customers who left a review are counted.

   ## Q7: Payment methods (sql/07_payment_methods.sql)

**Rules**
- Delivered orders, Jan 2017 - Aug 2018; amounts in R$.
- Payments aggregated to one row per order before joining (some orders
  have several payment rows).
- main_method = payment type with the largest amount in the order; orders
  paid with several methods are counted once, under that method.
- Order value = sum of payment_value for the order.

**Key numbers**
- 96,211 orders; total paid R$15.38M (matches item revenue in Q4, R$15.37M,
  within 0.02%).
- Share of orders / value: credit card 75.5% / 78.5%, boleto 19.9% / 18.0%,
  voucher 3.1% / 2.2%, debit card 1.5% / 1.4%.
- Avg (median) order value: credit card R$166 (R$109), boleto R$144 (R$94),
  voucher R$115 (R$81), debit card R$140 (R$90).
- Credit card orders are ~15% larger than boleto on average, ~17% on median.
- Averages are 41-57% above medians in every method (a few large orders).
- 49.7% of voucher-led orders used another method, vs 1.0% for card-led
  orders; ~2,200 orders (~2.3%) mixed methods (estimated from rounded
  percentages).

**Findings**
1. Credit card and boleto make up 95.4% of orders.
2. Card orders are larger than boleto orders. Consistent with installments
   enabling bigger baskets (tested in Q8), but it could also reflect who
   chooses each method.
3. Use the median (R$94-109) for a typical order; averages are skewed.
4. Vouchers are small and mostly used alongside another method.
5. Limitation: main_method is assigned by the largest payment, so voucher
   use inside card-led orders is not visible in the method mix.

   ## Q8: Installments vs order value (sql/08_installments.sql)

**Rules**
- Delivered orders, Jan 2017 - Aug 2018; credit-card-only orders (no
  voucher/boleto mixed in); installments = installments of the largest
  card payment in the order.
- Order value = item price + freight (from order_items), not amount paid.
- Payments and items each aggregated to one row per order before joining.

**Key numbers**
- 71,918 card-only orders (701 fewer than Q7's card-led 72,619; matches the
  ~1% of card-led orders that also used another method).
- Orders by bucket: paid in full 32.2%, 2-3 installments 30.3%, 4-6 21.5%,
  7-9 8.7%, 10+ 7.4%.
- Avg (median) order value: R$100 (71) -> R$135 (112) -> R$182 (128) ->
  R$268 (181) -> R$409 (236). Average up ~4.1x, median ~3.3x.
- ~68% of card orders use 2+ installments.
- 7+ installments: ~16% of card orders, ~32% of card value (calculated from
  rounded averages).
- Avg paid vs item total: gap 0.0-0.1% in every bucket, so no visible
  installment interest in this data.
- Check: implied card revenue ~R$11.9M = ~98.8% of Q7 card total (R$12.06M).

**Findings**
1. Order value rises steadily with installments; the 10+ bucket has ~4x the
   average order value of paid-in-full orders.
2. Long installments (7+) are a small share of orders but about a third of
   card value.
3. Averages are skewed, most in the 10+ bucket (avg 73% above median).
4. Recommendation: test longer installment options on higher-priced items
   with a randomized experiment. Hypothesis; direction of cause unknown.
5. Limitations: association not causation; order value is not basket size;
   card orders only; no data on interest, defaults, or who bears risk.