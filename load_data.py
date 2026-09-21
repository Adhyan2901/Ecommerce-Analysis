import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
engine = create_engine(os.getenv("DB_URL"))

date_cols = {
    "olist_orders_dataset": [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "olist_order_items_dataset": ["shipping_limit_date"],
    "olist_order_reviews_dataset": ["review_creation_date", "review_answer_timestamp"],
}

for f in sorted(Path("data").glob("*.csv")):
    table = f.stem.replace("olist_", "").replace("_dataset", "")
    df = pd.read_csv(f, parse_dates=date_cols.get(f.stem, []))
    df.to_sql(table, engine, if_exists="replace", index=False, chunksize=5000)
    print(f"{table}: {len(df):,} rows loaded")