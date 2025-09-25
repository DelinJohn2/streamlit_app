import pandas as pd
from config import load_engine
from sqlmodel import create_engine



# --- DB Engine ---
engine_name = load_engine()
engine = create_engine(engine_name)



class DataReaderMt:

  

    def read_mt_pwani_data(self):
        query = "SELECT * FROM pwani_marketing.mt_pwani_data_cleaned"
        data = pd.read_sql_query(query, engine)
 
        return data
       

    def read_mt_competitor_data(self):
        query = "SELECT * FROM pwani_marketing.mt_competitor_data_cleaned"
        df = pd.read_sql_query(query, engine)

        return df
