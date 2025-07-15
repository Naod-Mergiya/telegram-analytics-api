import os
import logging

# Configure logging
logging.basicConfig(
    filename='data_lake_setup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Data lake base path
DATA_LAKE_PATH = 'data/raw/telegram_messages'

def create_data_lake():
    try:
        # Create the base directory structure
        os.makedirs(DATA_LAKE_PATH, exist_ok=True)
        logger.info(f"Successfully created data lake directory: {DATA_LAKE_PATH}")
        print(f"Data lake directory created at: {DATA_LAKE_PATH}")
    except Exception as e:
        logger.error(f"Error creating data lake directory: {str(e)}")
        print(f"Error creating data lake directory: {str(e)}")

if __name__ == '__main__':
    create_data_lake()