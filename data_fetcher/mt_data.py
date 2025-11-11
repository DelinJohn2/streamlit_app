import pandas as pd
from config import load_engine
from sqlmodel import create_engine
from datetime import datetime, timedelta



# --- DB Engine ---
engine=load_engine()



class DataReaderMt:

    def read_mt_pwani_data(self):
        current_year = datetime.now().year

        query = f"""
            SELECT *
            FROM pwani_marketing.mt_pwani_data_cleaned
            WHERE YEAR(date) = {current_year}
        """
        data = pd.read_sql_query(query, engine)
        return data

    def read_mt_competitor_data(self):
        current_year = datetime.now().year

        query = f"""
            SELECT *
            FROM pwani_marketing.mt_competitor_data_cleaned
            WHERE YEAR(date) = {current_year}
        """
        df = pd.read_sql_query(query, engine)
        return df
