from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

load_dotenv()

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DB = os.getenv("DB")
USER = os.getenv("USER")
PASSWORD = quote_plus(os.getenv("PASSWORD"))

engine = create_engine(
    f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}",
    pool_pre_ping=True,
    pool_recycle=3600,
)


def get_df(query: str) -> pd.DataFrame:
    return pd.read_sql(query, engine)
