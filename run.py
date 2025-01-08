import os
import requests
import time
from datetime import datetime
from telegram import Bot
from telegram.ext import Updater, CommandHandler

# Replace with your bot token
TOKEN = '7324758222:AAGCiGsotQ6Y-eVgoXrwPDNRSAP5GFNxsq4'

# ID of the group where the bot will send notifications (starts with @)
CHANNEL_ID = '@percy_verence_poe2'

# URL of the API
API_URL = 'https://pathofexile2.com/internal-api/content/game-ladder/id/Hardcore'

# Name of the character to check
CHARACTER_NAME = 'Percy_Verence'

# Read environment variables
APP_URL = os.environ.get("APP_URL")
PORT = int(os.environ.get('PORT', '8443'))

# Initialize the bot
bot = Bot(token=TOKEN)

# Variable to track the last time a message was sent
last_message_time = None

# Function to fetch data from the API and check the character's status
def fetch_data():
    response = requests.get(API_URL)
    data = response.json()

    for entry in data['context']['ladder']['entries']:
        if entry['character']['name'] == CHARACTER_NAME:
            if entry['dead']:
                rank = entry['rank']
                message = (
                    f"DEAD WARNING  WARNING  WARNING  Character {CHARACTER_NAME} is DEAD. Current rank is {rank}.\n"
                    f"DEAD WARNING  Nhân vật {CHARACTER_NAME} đã chết. Rank hiện tại là {rank}."
                )
                message_ids = []
                for _ in range(5):
                    msg = bot.send_message(chat_id=CHANNEL_ID, text=message)
                    message_ids.append(msg.message_id)
                # Pin the first message out of the 5 sent messages
                bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=message_ids[0])
                return True, rank  # Character is dead
            else:
                rank = entry['rank']
                return False, rank  # Character is not dead
    return None, None  # Character not found

# Function to start the bot and set up data fetching intervals
def start(update, context):
    global last_message_time
    context.bot.send_message(chat_id=update.effective_chat.id, text='Bot đã bắt đầu theo dõi nhân vật.')
    while True:
        character_dead, rank = fetch_data()
        current_time = datetime.now()

        if character_dead is None:
            context.bot.send_message(chat_id=CHANNEL_ID, text=f"Character {CHARACTER_NAME} not found.")
            break
        elif character_dead:
            break
        else:
            if last_message_time is None or (current_time - last_message_time).total_seconds() >= 1800:
                message = (
                    f"YEAH NOT DEAD. Character {CHARACTER_NAME} is NOT DEAD. Current rank is {rank}.\n"
                    f"Nhân vật {CHARACTER_NAME} chưa chết. Rank hiện tại là {rank}."
                )
                bot.send_message(chat_id=CHANNEL_ID, text=message)
                last_message_time = current_time

        time.sleep(60)  # Fetch data every minute

def main() -> None:
    # Initialize updater and dispatcher
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Register the /start command
    dp.add_handler(CommandHandler("start", start))

    # Set up webhook
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=APP_URL + TOKEN)
    
    # Keep the bot running
    updater.idle()

if __name__ == '__main__':
    main()
