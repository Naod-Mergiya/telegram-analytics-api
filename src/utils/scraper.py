import asyncio
import json
import logging
import os
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import configparser

# Configure logging
logging.basicConfig(
    filename='telegram_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Read configuration
config = configparser.ConfigParser()
# Use absolute path relative to the script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(script_dir, 'config.ini')

# Debug: Print current working directory and expected config path
current_dir = os.getcwd()
expected_config_path = config_file
logger.info(f"Current working directory: {current_dir}")
logger.info(f"Looking for config file at: {expected_config_path}")
print(f"Current working directory: {current_dir}")
print(f"Looking for config file at: {expected_config_path}")

# Check if config.ini exists
if not os.path.exists(config_file):
    logger.error(f"{config_file} not found in {script_dir}. Creating a template.")
    config['Telegram'] = {
        'api_id': 'YOUR_API_ID',
        'api_hash': 'YOUR_API_HASH',
        'phone': 'YOUR_PHONE_NUMBER'
    }
    with open(config_file, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    logger.info(f"Created {config_file} template. Please fill in your Telegram API credentials and rerun the script.")
    print(f"Created {config_file} template. Please fill in your Telegram API credentials and rerun the script.")
    exit()

# Read the config file
try:
    config.read(config_file, encoding='utf-8')
    logger.info(f"Successfully read {config_file}")
    print(f"Successfully read {config_file}")
except Exception as e:
    logger.error(f"Failed to read {config_file}: {str(e)}")
    print(f"Error: Failed to read {config_file}: {str(e)}")
    exit()

# Validate the Telegram section
try:
    api_id = config.get('Telegram', 'api_id')
    api_hash = config.get('Telegram', 'api_hash')
    phone = config.get('Telegram', 'phone')
    username = config.get('Telegram', 'username', fallback=None)
    logger.info("Successfully loaded Telegram configuration")
    print("Successfully loaded Telegram configuration")
except configparser.NoSectionError:
    logger.error(f"No [Telegram] section found in {config_file}. Please add the required section.")
    print(f"Error: No [Telegram] section found in {config_file}. Please add the section with api_id, api_hash, and phone.")
    exit()
except configparser.NoOptionError as e:
    logger.error(f"Missing required option in {config_file}: {str(e)}")
    print(f"Error: Missing required option in {config_file}: {str(e)}")
    exit()

# Validate that credentials are not placeholders
if api_id == 'YOUR_API_ID' or api_hash == 'YOUR_API_HASH' or phone == 'YOUR_PHONE_NUMBER':
    logger.error(f"Invalid credentials in {config_file}. Please replace placeholder values with actual Telegram API credentials.")
    print(f"Error: Invalid credentials in {config_file}. Please replace placeholder values with actual Telegram API credentials.")
    exit()

# List of channels to scrape
channels = [
    'https://t.me/lobelia4cosmetics',
    'https://t.me/tikvahpharma',
    'https://t.me/Chemed123'  # Chemed Telegram Channel
]

# Data lake base path
DATA_LAKE_PATH = 'data/raw/telegram_messages'

async def scrape_channel(client, channel_url):
    try:
        # Extract channel name from URL
        channel_name = channel_url.split('/')[-1]
        entity = await client.get_entity(channel_url)
        
        # Create directory structure
        today = datetime.now().strftime('%Y-%m-DD')
        output_dir = os.path.join(DATA_LAKE_PATH, today, channel_name)
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f'{channel_name}_{today}.json')
        messages_data = []
        
        logger.info(f"Starting scrape for channel: {channel_name}")
        
        async for message in client.iter_messages(entity, limit=100):  # Adjustable limit
            message_data = {
                'id': message.id,
                'date': message.date.isoformat(),
                'text': message.text,
                'sender_id': message.sender_id,
                'has_media': message.media is not None,
                'media_type': None,
                'media_path': None
            }
            
            # Handle media (images)
            if message.media and hasattr(message.media, 'photo'):
                message_data['media_type'] = 'photo'
                media_dir = os.path.join(output_dir, 'media')
                os.makedirs(media_dir, exist_ok=True)
                
                # Download media
                media_path = os.path.join(media_dir, f'message_{message.id}.jpg')
                await client.download_media(message.media, media_path)
                message_data['media_path'] = media_path
                logger.info(f"Downloaded image for message {message.id} in {channel_name}")
            
            messages_data.append(message_data)
        
        # Save messages to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(messages_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Successfully scraped {len(messages_data)} messages from {channel_name}")
        
    except Exception as e:
        logger.error(f"Error scraping {channel_name}: {str(e)}")

async def main():
    # Initialize Telegram client
    client = TelegramClient('session_name', api_id, api_hash)
    
    try:
        await client.start(phone=phone)
        
        # If 2FA is enabled, handle it
        if not await client.is_user_authorized():
            try:
                await client.sign_in(phone=phone)
            except SessionPasswordNeededError:
                password = input("Enter your 2FA password: ")
                await client.sign_in(password=password)
        
        # Scrape all channels
        for channel in channels:
            await scrape_channel(client, channel)
            
    except Exception as e:
        logger.error(f"Main process error: {str(e)}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())