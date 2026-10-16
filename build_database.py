import pandas as pd
import sqlite3
import os

# ---------------------------------------------------------
# Load both CSV files
# ---------------------------------------------------------
sales_df = pd.read_csv("data/EV_sales_sample_5000.csv")
vehicles_df = pd.read_csv("data/EV_Vehicles_sample_5000.csv")

# ---------------------------------------------------------
# Create/connect to SQLite database
# ---------------------------------------------------------
db_path = "ev_data.db"
conn = sqlite3.connect(db_path)

# ---------------------------------------------------------
# Save DataFrames to SQLite tables
# if_exists="replace" makes sure we rebuild cleanly each run
# ---------------------------------------------------------
vehicles_df.to_sql("vehicles", conn, if_exists="replace", index=False)
sales_df.to_sql("sales", conn, if_exists="replace", index=False)

# ---------------------------------------------------------
# Pull just a few rows so we can eyeball column names + sample data
# ---------------------------------------------------------
sales_check = pd.read_sql("SELECT * FROM sales LIMIT 5", conn)
print("\nSample rows from 'sales':")
print(sales_check)

# ---------------------------------------------------------
# Print columns for both tables
# (Using PRAGMA table_info)
# ---------------------------------------------------------
cursor = conn.cursor()
for table in ["sales", "vehicles"]:
    print(f"\n{table} columns:")
    cursor.execute(f"PRAGMA table_info({table})")
    for row in cursor.fetchall():
        print(row)

# ---------------------------------------------------------
# Close connection
# ---------------------------------------------------------
conn.close()
