from sqlmodel import create_engine

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='.env')  # Load .env file into environment variables

def load_base_ip():

    base_ip=os.getenv("Base_ip")
    
    return base_ip

def load_engine():

    

# Database credentials
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD =os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')

# Create SQLAlchemy engine
    engine = create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        pool_pre_ping=True,          # ✅ Checks if connection is alive before use
        pool_recycle=1800,           # ✅ Prevents MySQL timeout issues
        pool_size=10,                # ✅ Safe pool size
        max_overflow=5,              # ✅ Allow some burst connections
    )
    return engine

