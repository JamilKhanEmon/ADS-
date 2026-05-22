from sqlalchemy import create_engine, text
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DB = os.getenv("DB")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

print("[INFO] Connecting to database...")
print(f"       Host: {HOST}:{PORT} | DB: {DB} | User: {USER}")

try:
    engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}")

    with engine.connect() as conn:
        print("\n[OK] Connection successful!\n")

        # 1. Show all tables
        print("[INFO] Tables in database:")
        tables = conn.execute(text("SHOW TABLES")).fetchall()
        for t in tables:
            print(f"       - {t[0]}")

        # 2. Row counts
        print("\n[INFO] Row counts:")
        table_names = [t[0] for t in tables]
        for table in table_names:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"       {table}: {count} rows")

        # 3. Test the 3 views
        print("\n[INFO] Testing views...")
        views = ["vw_harvest_full", "vw_revenue_by_crop_year", "vw_farm_profitability"]
        for view in views:
            try:
                df = pd.read_sql(f"SELECT * FROM {view} LIMIT 3", engine)
                print(f"\n       [OK] {view} - {len(df.columns)} columns")
                print(f"            Columns: {list(df.columns)}")
            except Exception as e:
                print(f"       [FAIL] {view} - Error: {e}")

except Exception as e:
    print(f"\n[FAIL] Connection failed!\n       Error: {e}")
