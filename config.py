

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='.env')  # Load .env file into environment variables

def load_anthropic_api_config():
    """
    Loads API configuration from environment variables.
    Returns a dictionary with API key, model, and provider.
    """
    api_key = os.getenv("ANTHROPIC_KEY")
    model = os.getenv("model")
    provider = os.getenv("MODEL_PROVIDER")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")

    return {
        "api_key": api_key,
        "model": model,
        "provider": provider
    }


def load_open_ai_api_config():
    """
    Loads API configuration from environment variables.
    Returns a dictionary with API key, model, and provider.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("GPT_model")
    provider = os.getenv("GPT_model_provider")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")

    return {
        "api_key": api_key,
        "model": model,
        "provider": provider
    }

def load_engine():

    

# Database credentials
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD =os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')

# Create SQLAlchemy engine
    engine = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return engine
