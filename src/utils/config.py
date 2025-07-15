from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DATA_PATH = os.getenv("DATA_PATH")
    LOG_PATH = os.getenv("LOG_PATH")
    
    TELEGRAM_CHANNELS = [
        "Chemed",
        "lobelia4cosmetics",
        "tikvahpharma"
    ]