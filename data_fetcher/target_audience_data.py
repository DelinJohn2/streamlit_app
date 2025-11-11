import pandas as pd
from config import load_engine




# --- DB Engine ---
engine = load_engine()





def read_target_audience():
    query = "SELECT * FROM pwani_marketing.target_audience_territory"
    data = pd.read_sql_query(query, engine)

    return data

