import pandas as pd
from config import load_engine
from sqlmodel import create_engine



# --- DB Engine ---
engine_name = load_engine()
engine = create_engine(engine_name)



class DataReaderGT:

    def read_gt_pwani_data(self):
        query = """
            SELECT *
            FROM pwani_marketing.gt_data_pwani
            WHERE date = (SELECT MAX(date) FROM pwani_marketing.gt_data_pwani)
        """
      
        data = pd.read_sql(query, engine)
        return data
   

    def read_gt_competitor_data(self):
        query = """
            SELECT *
            FROM pwani_marketing.gt_competitor_data
            WHERE date = (SELECT MAX(date) FROM pwani_marketing.gt_competitor_data)
        """
        
        df = pd.read_sql(query, engine)
        return df
    

    def read_rtm_data(self):
        query = "SELECT * FROM pwani_marketing.rtm_data_cleaned"
        df = pd.read_sql(query, engine)
        return df

