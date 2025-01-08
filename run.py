import os
import requests
import time
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

# Function to fetch data from the API and check the character's status
def fetch_data():
    response = requests.get(API_URL)
    data = response.json()

    for entry in data['context']['ladder']['entries']:
        if entry['character']['name'] == CHARACTER_NAME:
            if entry['dead']:
                rank = entry['rank']
                message = (
                    f"WARNING  WARNING  WARNING  Character {CHARACTER_NAME} is dead. Current rank is {rank}.\n"
                    f"WARNING  Nhân vật {CHARACTER_NAME} đã chết. Rank hiện tại là {rank}."
                )
                message_ids = []
                for _ in range(5):
                    msg = bot.send_message(chat_id=CHANNEL_ID, text=message)
                    message_ids.append(msg.message_id)
                # Pin the first message out of the 5 sent messages
                bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=message_ids[0])
            else:
                rank = entry['rank']
                message = (
                    f"Character {CHARACTER_NAME} is not dead. Current rank is {rank}.\n"
                    f"Nhân vật {CHARACTER_NAME} chưa chết. Rank hiện tại là {rank}."
                )
                bot.send_message(chat_id=CHANNEL_ID, text=message)
            break

# Function to start the bot and set up data fetching intervals
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Bot đã bắt đầu theo dõi nhân vật.')
    while True:
        fetch_data()
        time.sleep(60)

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
