-- AUD, excluding GST. Keys are synthetic. Facts preserve separate grains.
PRAGMA foreign_keys=ON;
CREATE TABLE dim_date(date_id TEXT PRIMARY KEY, month TEXT NOT NULL, weekday INTEGER NOT NULL CHECK(weekday BETWEEN 0 AND 6), week_start TEXT NOT NULL);
CREATE TABLE dim_location(location_id INTEGER PRIMARY KEY, name TEXT NOT NULL, state TEXT NOT NULL, region TEXT NOT NULL);
CREATE TABLE dim_product(product_id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL, list_price REAL NOT NULL CHECK(list_price>0), unit_cost REAL NOT NULL CHECK(unit_cost>=0));
CREATE TABLE dim_customer(customer_id INTEGER PRIMARY KEY, segment TEXT NOT NULL);
CREATE TABLE dim_channel(channel_id INTEGER PRIMARY KEY, name TEXT NOT NULL, fee_rate REAL NOT NULL CHECK(fee_rate BETWEEN 0 AND 1));
CREATE TABLE dim_promotion(promotion_id INTEGER PRIMARY KEY, name TEXT NOT NULL, discount_rate REAL NOT NULL CHECK(discount_rate BETWEEN 0 AND 1));
CREATE TABLE dim_employee(employee_id INTEGER PRIMARY KEY, location_id INTEGER NOT NULL REFERENCES dim_location, role TEXT NOT NULL);
CREATE TABLE fact_sales(sale_id INTEGER PRIMARY KEY, date_id TEXT NOT NULL REFERENCES dim_date, location_id INTEGER NOT NULL REFERENCES dim_location, product_id INTEGER NOT NULL REFERENCES dim_product, customer_id INTEGER NOT NULL REFERENCES dim_customer, channel_id INTEGER NOT NULL REFERENCES dim_channel, promotion_id INTEGER NOT NULL REFERENCES dim_promotion, daypart TEXT NOT NULL CHECK(daypart IN ('Morning','Lunch','Evening')), quantity INTEGER NOT NULL CHECK(quantity>0), list_sales REAL NOT NULL CHECK(list_sales>=0), discount REAL NOT NULL CHECK(discount>=0), refund REAL NOT NULL CHECK(refund>=0), cogs REAL NOT NULL CHECK(cogs>=0), channel_fee REAL NOT NULL CHECK(channel_fee>=0), CHECK(discount+refund<=list_sales+0.001));
CREATE TABLE fact_labour(labour_id INTEGER PRIMARY KEY, date_id TEXT NOT NULL REFERENCES dim_date, location_id INTEGER NOT NULL REFERENCES dim_location, employee_id INTEGER NOT NULL REFERENCES dim_employee, hours REAL NOT NULL CHECK(hours>0), labour_cost REAL NOT NULL CHECK(labour_cost>=0));
CREATE TABLE fact_inventory(inventory_id INTEGER PRIMARY KEY, date_id TEXT NOT NULL REFERENCES dim_date, location_id INTEGER NOT NULL REFERENCES dim_location, product_id INTEGER NOT NULL REFERENCES dim_product, available INTEGER NOT NULL CHECK(available IN (0,1)), closing_units INTEGER NOT NULL CHECK(closing_units>=0), UNIQUE(date_id,location_id,product_id));
CREATE TABLE fact_operating_costs(cost_id INTEGER PRIMARY KEY, date_id TEXT NOT NULL REFERENCES dim_date, location_id INTEGER NOT NULL REFERENCES dim_location, overhead REAL NOT NULL CHECK(overhead>=0), UNIQUE(date_id,location_id));
CREATE TABLE fact_promotions(spend_id INTEGER PRIMARY KEY, date_id TEXT NOT NULL REFERENCES dim_date, location_id INTEGER NOT NULL REFERENCES dim_location, promotion_id INTEGER NOT NULL REFERENCES dim_promotion, campaign_spend REAL NOT NULL CHECK(campaign_spend>=0), UNIQUE(date_id,location_id));
CREATE TABLE fact_feedback(feedback_id INTEGER PRIMARY KEY, sale_id INTEGER NOT NULL REFERENCES fact_sales, rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5), UNIQUE(sale_id));
CREATE INDEX sales_location_date ON fact_sales(location_id,date_id);
CREATE INDEX sales_date ON fact_sales(date_id);
CREATE INDEX sales_customer_date ON fact_sales(customer_id,date_id);
CREATE INDEX sales_product_date ON fact_sales(product_id,date_id);
