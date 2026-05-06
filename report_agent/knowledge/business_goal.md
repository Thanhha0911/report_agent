# Olist Marketplace — Business Goals & Analytics Guidance
 
> **Purpose:** This document serves as the analytical brief for the data analytics agent.
> Each business goal is defined with a clear objective, success metrics, key dimensions to slice by,
> relevant tables from the Olist SQLite dataset, and the exact analytical questions the agent must answer.
 
---
 
## Context
 
Olist is a Brazilian e-commerce marketplace that connects small and medium-sized sellers to major retail channels.
The platform operates as a B2B2C model:
- **B2B layer:** Olist onboards sellers through a marketing and sales funnel (MQLs → closed deals).
- **B2C layer:** End-customers place orders, receive products, and leave reviews.
The dataset covers orders placed between **2016 and 2018**, with 9 core tables:
`orders`, `order_items`, `order_payments`, `order_reviews`, `customers`,
`sellers`, `products`, `product_category_name_translation`, `geolocation`,
and 2 seller funnel tables: `leads_qualified`, `leads_closed`.
 
---
 
## Goal G1 — Grow Gross Merchandise Value (GMV) by 30% YoY
 
### Business Statement
Accelerate marketplace revenue by expanding the active seller base with high-quality sellers
and increasing purchase frequency among existing customers.
 
### North Star Metric
- **GMV** = `SUM(price + freight_value)` on delivered orders
- **Target:** GMV ≥ R$20M / month by Q4 2024
### Supporting KPIs
 
| KPI | Definition | Target |
|---|---|---|
| Monthly order volume | `COUNT(order_id)` WHERE `order_status = 'delivered'` | +25% MoM growth |
| Repeat purchase rate | Customers with ≥ 2 orders / total unique customers | ≥ 15% |
| Lead-to-seller conversion | `COUNT(won)` / `COUNT(mql_id)` in `leads_qualified` | ≥ 12% |
| Active sellers | Sellers with ≥ 1 delivered order in the last 30 days | +20% YoY |
 
### Key Dimensions to Slice By
- `product_category_name_english` — which categories drive the most GMV?
- `customer_state` / `seller_state` — regional concentration and white-space
- `order_purchase_timestamp` (monthly cohort) — growth trend over time
- `payment_type` — credit card vs boleto vs voucher mix
- `leads_closed.business_segment` — which seller segments convert best?
### Tables Required
```
orders, order_items, customers, sellers,
leads_qualified, leads_closed, order_payments
```
 
### Analytical Questions for the Agent
 
1. What is the monthly GMV trend from 2016 to 2018? Identify the peak month and any seasonal patterns.
2. Which 10 product categories account for the top 60% of GMV? (Pareto analysis)
3. What is the repeat purchase rate per customer cohort (by first order month)?
4. What is the MQL → won conversion rate by `origin` and `lead_type`?
5. Which seller states generate the highest GMV per active seller?
6. Among churned sellers (no order in last 60 days), what is their historical GMV contribution?
---
 
## Goal G2 — Improve Customer Satisfaction to avg Review Score ≥ 4.2
 
### Business Statement
Reduce the late delivery rate — the primary driver of low review scores — to below 8%,
and identify the seller and geographic segments most responsible for poor customer experience.
 
### North Star Metric
- **Average review score** = `AVG(review_score)` from `order_reviews`
- **Target:** avg score ≥ 4.2 stars (baseline: ~4.07 in the dataset)
### Supporting KPIs
 
| KPI | Definition | Target |
|---|---|---|
| Late delivery rate | `COUNT` where `order_delivered_customer_date > order_estimated_delivery_date` / total delivered | < 8% |
| 1-star review rate | `COUNT(review_score = 1)` / total reviews | < 5% |
| Avg days to deliver | `AVG(order_delivered_customer_date - order_purchase_timestamp)` | ≤ 10 days |
| Review response rate | Orders with a review / total delivered orders | ≥ 70% |
 
### Key Dimensions to Slice By
- `seller_state` → `customer_state` pair — which delivery routes are most problematic?
- `product_category_name_english` — are certain categories associated with lower scores?
- Delivery time bucket (0–5 days, 6–10, 11–20, 20+) — score distribution by speed tier
- `order_purchase_timestamp` (month) — is satisfaction improving or declining over time?
### Tables Required
```
orders, order_reviews, order_items, sellers, customers, products,
product_category_name_translation
```
 
### Analytical Questions for the Agent
 
1. What is the distribution of review scores (1 to 5)? What % of orders receive a score ≤ 2?
2. What is the correlation between late delivery (binary flag) and review score ≤ 3?
3. Which seller_state → customer_state delivery corridors have the highest late delivery rate?
4. For orders delivered within 5 days, what is the average review score vs orders taking 15+ days?
5. Which product categories have the lowest average review score? Are these also the heaviest/largest products?
6. Is there a time-of-year pattern in late deliveries (e.g., holiday peaks)?
---
 
## Goal G3 — Achieve Seller Ship-on-Time Rate ≥ 92%
 
### Business Statement
Hold sellers accountable to their committed `shipping_limit_date`.
Identify chronic violators for performance improvement programs or offboarding,
and surface early warning signals before violations impact the end customer.
 
### North Star Metric
- **Ship-on-time rate** = orders where carrier pickup ≤ `shipping_limit_date` / total order items
- **Target:** ≥ 92% of all order items shipped on time
### Supporting KPIs
 
| KPI | Definition | Target |
|---|---|---|
| Ship-on-time rate | `shipped_on_time = 1` items / total items | ≥ 92% |
| Avg days late (violators) | `AVG(carrier_date - shipping_limit_date)` for late shipments | < 2 days |
| Chronic violator rate | Sellers with < 80% on-time across ≥ 10 orders | < 5% of active sellers |
| Violation by segment | Late rate grouped by `leads_closed.business_segment` | Monitor |
 
### Key Dimensions to Slice By
- `seller_id` — individual seller ranking
- `seller_state` — geographic concentration of violations
- `product_category_name_english` — are violations clustered in specific categories?
- `leads_closed.business_segment` / `business_type` — which seller profiles violate most?
- `order_purchase_timestamp` (month) — is compliance improving?
### Tables Required
```
order_items, orders, sellers, leads_closed,
products, product_category_name_translation
```
 
### Analytical Questions for the Agent
 
1. What is the overall ship-on-time rate across all order items in the dataset?
2. Rank sellers by ship-on-time rate (minimum 10 orders). Who are the bottom 20?
3. Among late shipments, what is the average number of days past the shipping limit?
4. Do violations correlate with product weight (`product_weight_g`) or size (`product_length_cm`, etc.)?
5. Which `business_segment` (from `leads_closed`) has the worst shipping compliance?
6. Is there a monthly trend — did seller compliance improve or deteriorate over 2017–2018?
---
 
## Goal G4 — Increase Average Order Value (AOV) to R$180
 
### Business Statement
Grow revenue per transaction by improving product category mix,
encouraging multi-item baskets, and reducing the freight cost burden on lower-value orders.
 
### North Star Metric
- **AOV** = `SUM(price + freight_value)` / `COUNT(DISTINCT order_id)` on delivered orders
- **Target:** AOV ≥ R$180 (baseline: ~R$154 in the dataset)
### Supporting KPIs
 
| KPI | Definition | Target |
|---|---|---|
| Avg basket size | `COUNT(order_item_id)` / `COUNT(DISTINCT order_id)` | ≥ 1.3 items/order |
| Avg item price | `AVG(price)` across all delivered order items | ≥ R$130 |
| Freight-to-price ratio | `AVG(freight_value / price)` | < 18% |
| High-AOV category share | % of GMV from categories with avg price > R$200 | ≥ 35% |
 
### Key Dimensions to Slice By
- `product_category_name_english` — which categories drive high vs low AOV?
- `payment_type` + `payment_installments` — do installment buyers have higher AOV?
- `customer_state` — regional AOV differences (purchasing power)
- `seller_state` — freight cost varies by seller location
- Order size bucket (1 item, 2–3 items, 4+ items) — basket size impact on AOV
### Tables Required
```
order_items, orders, products, product_category_name_translation,
order_payments, customers, sellers
```
 
### Analytical Questions for the Agent
 
1. What is the current AOV overall, and how does it trend month over month?
2. What is the AOV by product category? Which 5 categories have the highest and lowest AOV?
3. What % of orders contain more than 1 item? What is the AOV uplift for 2-item vs 1-item orders?
4. What is the freight-to-price ratio by product category? Which categories have the worst ratio?
5. Do customers paying by installments (`payment_installments > 1`) place higher AOV orders?
6. Which customer states have the highest AOV? Is it correlated with freight cost or product mix?
---
 
## Data Layer Reference
 
### Naming Convention Expected from Data Engineer
 
| Layer | Prefix | Example |
|---|---|---|
| Raw ingestion | `stg_` | `stg_orders`, `stg_order_items` |
| Dimension tables | `dim_` | `dim_customer`, `dim_seller`, `dim_product` |
| Fact tables | `fact_` | `fact_orders`, `fact_delivery`, `fact_seller_shipment`, `fact_order_items_enriched` |
 
### Pre-computed Columns the Agent Can Rely On
 
| Column | Table | Logic |
|---|---|---|
| `is_late` | `fact_delivery` | `order_delivered_customer_date > order_estimated_delivery_date` |
| `days_to_deliver` | `fact_delivery` | `order_delivered_customer_date - order_purchase_timestamp` |
| `shipped_on_time` | `fact_seller_shipment` | `order_delivered_carrier_date <= shipping_limit_date` |
| `freight_ratio` | `fact_order_items_enriched` | `freight_value / NULLIF(price, 0)` |
| `category_en` | `fact_order_items_enriched` | Joined from `product_category_name_translation` |
| `is_repeat_buyer` | `dim_customer` | `COUNT(orders) > 1` per `customer_unique_id` |
| `gmv` | `fact_orders` | `price + freight_value` per order |
| `order_month` | `fact_orders` | `DATE_TRUNC('month', order_purchase_timestamp)` |
 
### Filtering Convention
 
Unless otherwise specified, all analyses should:
- Filter on `order_status = 'delivered'` for revenue and satisfaction metrics
- Exclude `order_status IN ('canceled', 'unavailable')` from funnel metrics
- Use `customer_unique_id` (not `customer_id`) for customer-level deduplication
---
 
## Output Format Expected from BI Analyst
 
Each goal should produce a separate markdown dashboard file with the following structure:
 
```
# G{N} Dashboard — {Goal Name}
## Summary KPIs   ← 4 metric cards with current value vs target
## Key Findings   ← 3–5 bullet insights in plain English
## Data Tables    ← SQL query results as markdown tables
## Recommended Actions  ← 2–3 actionable recommendations for the CEO
```
 
Files: `g1_growth_dashboard.md`, `g2_satisfaction_dashboard.md`,
`g3_seller_dashboard.md`, `g4_monetization_dashboard.md`
