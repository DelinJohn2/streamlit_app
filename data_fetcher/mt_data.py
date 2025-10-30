import pandas as pd
from config import load_engine
from sqlmodel import create_engine
from datetime import datetime, timedelta



# --- DB Engine ---
engine_name = load_engine()
engine = create_engine(engine_name)



class DataReaderMt:

    def read_mt_pwani_data(self):
        # Calculate the cutoff date (4 months ago)
        cutoff_date = (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d')
        
        query = f"""
            SELECT *
            FROM pwani_marketing.mt_pwani_data_cleaned
            WHERE date >= '{cutoff_date}'
        """
        data = pd.read_sql_query(query, engine)
        return data

    def read_mt_competitor_data(self):
        cutoff_date = (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d')

        query = f"""
            SELECT *
            FROM pwani_marketing.mt_competitor_data_cleaned
            WHERE date >= '{cutoff_date}'
        """
        df = pd.read_sql_query(query, engine)
        return df
