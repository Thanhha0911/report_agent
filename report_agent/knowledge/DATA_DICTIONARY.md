# Olist Data Warehouse - Data Dictionary

This document describes the structure, meaning, and transformation logic of the Olist Data Warehouse system on DuckDB, built and managed with dbt.

The system follows a multi-layer data architecture, consisting of:
1. **Raw (Source):** Original raw data.
2. **Staging:** Cleaning layer — normalizes column names and handles data type casting.
3. **Intermediate:** Denormalization layer — light aggregation and feature engineering.
4. **Marts:** Business layer — aggregated data serving reports and in-depth analysis.

---

## 1. Raw Layer (`raw_olist` schema)

This layer contains all raw tables (raw 1-1) ingested from the source (e.g., PostgreSQL). Data here is unmodified, preserving the original structure and relationships.

**Main tables:**
- `orders`, `order_items`, `customers`, `sellers`, `products`
- `order_payments`, `order_reviews`, `geolocation`
- `product_category_translation`
- `marketing_qualified_leads`, `closed_deals`

---

## 2. Staging Layer (`main_staging` schema)

The Staging layer (`stg_`) extracts data from `raw_olist` and performs basic cleaning steps: renaming columns for consistency (naming convention), deduplication, and data type casting.

| Table Name (Model) | Meaning / Purpose |
| :--- | :--- |
| `stg_olist__orders` | Central orders table. Contains order status and key timestamps (purchased, approved, shipped, delivered). |
| `stg_olist__order_items` | Line-item details for each product within an order. Contains price (`item_price`) and shipping cost (`freight_value`). |
| `stg_olist__customers` | Customer identity and geographic location information. |
| `stg_olist__sellers` | Seller identity and geographic location information. |
| `stg_olist__products` | Product dimensions, weight, and category classification. |
| `stg_olist__payments` | Order payment history (payment type, amount, number of installments). |
| `stg_olist__reviews` | Customer review scores and comments for orders. |
| `stg_olist__geolocation` | Geographic coordinate data. *Deduplicated* by `zip_code` (one row per postal code). |
| `stg_olist__marketing_qualified_leads` | Potential customers (leads) captured through marketing campaigns. |
| `stg_olist__closed_deals` | Leads that have been successfully converted (into sellers). Contains declared revenue and business segment information. |
| `stg_olist__product_category_translation` | Mapping table translating product category names from Portuguese to English. |

---

## 3. Intermediate Layer (`main_intermediate` schema)

The Intermediate layer (`int_`) joins staging tables together and prepares data (denormalize) into dimensions and intermediate models before loading into the Marts.

| Table Name (Model) | Meaning / Transformation Logic |
| :--- | :--- |
| `int_customers_geo` | Enriches customer data by joining with `geolocation` to retrieve `lat` and `lng` coordinates. Supports geographic analysis. |
| `int_orders_enriched` | Central aggregation table with information for **each order (1 row per order)**. Aggregates total revenue (`order_revenue`), total shipping cost, and primary payment method from items and payments. |
| `int_order_lifecycle` | Calculates the duration of each fulfillment stage (approval_hours, handling_hours, transit_hours) and classifies delivery SLA status (`on_time`, `slightly_late`, `significantly_late`). |
| `int_delivery_sla` | **Feature Table** for an **ML Model** predicting late deliveries. Carefully computes the seller's historical delay rate (`seller_historical_delay_rate`) to avoid data leakage. |
| `int_sellers_performance` | KPI summary table for **each seller (1 row per seller)**: total GMV, order count, on-time delivery rate, and average review score. |

---

## 4. Mart Layer (`main_mart_...` schemas)

The Marts layer (`mart_`) contains tables aggregated at the highest level, serving BI Dashboards directly and answering specific business questions. Organized by business domain.

### 4.1. Customer Domain (`main_mart_customer`)
Focused on analyzing customer behavior and lifetime value.

*   **`mart_customer_ltv`**:
    *   **Purpose:** Calculates Lifetime Value (LTV) for each unique customer (`customer_unique_id`).
    *   **Metrics:** Total orders, total revenue, purchase lifespan (days).
    *   **Segmentation:** Uses `NTILE(4)` to classify customers into 4 tiers (1 = highest LTV, 4 = lowest LTV).
*   **`mart_customer_cohorts`**:
    *   **Purpose:** Cohort analysis (Customer Retention Rate) by month.
    *   **Logic:** Groups customers by their first purchase month (`cohort_month`) and tracks return rates in subsequent months (`activity_month`).

### 4.2. Finance Domain (`main_mart_finance`)
Focused on revenue and cash flow.

*   **`mart_finance`** *(Incremental Model)*:
    *   **Purpose:** Records revenue for valid orders (delivered, shipped, invoiced).
    *   **Metrics:** Order revenue, payment method, number of installments, shipping cost.
    *   **Optimization:** Uses Incremental materialization to load only new orders, reducing compute cost.

### 4.3. Operations & Logistics Domain (`main_mart_operations`)
Focused on operational optimization, SLA monitoring, and seller performance.

*   **`mart_operations_fulfillment`** *(Incremental Model)*:
    *   **Purpose:** Provides a full picture of an order's lifecycle and operational risks (delay prediction features).
    *   **Includes:** Combined from `int_order_lifecycle` and `int_delivery_sla`.
*   **`mart_seller_performance`**:
    *   **Purpose:** Tracks seller health metrics and rankings.
    *   **Metrics:** GMV, on-time orders (`on_time_orders`), review score, GMV ranking (`rank_by_gmv`).

### 4.4. Product Domain (`main_mart_product`)
Focused on product category performance.

*   **`mart_product_performance`**:
    *   **Purpose:** Evaluates the effectiveness of each product category (using English names).
    *   **Metrics:** Order count, total revenue, average price, cancellation rate (`cancellation_rate`), average weight (`avg_weight_g`).
