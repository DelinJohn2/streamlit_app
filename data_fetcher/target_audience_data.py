import pandas as pd
from config import load_engine
from sqlmodel import create_engine



# --- DB Engine ---
engine_name = load_engine()
engine = create_engine(engine_name)




def read_target_audience():
    query = "SELECT * FROM pwani_marketing.target_audience_territory"
    data = pd.read_sql_query(query, engine)

    return data

