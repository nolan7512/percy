import os
import pytz
import requests
import time
from datetime import datetime, timedelta
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler

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
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        for entry in data['context']['ladder']['entries']:
            if entry['character']['name'] == CHARACTER_NAME:
                experience = entry['character']['experience']
                if entry['dead']:
                    rank = entry['rank']
                    message = (
                        f"DEAD WARNING  Character {CHARACTER_NAME} is DEAD. Current rank is {rank}.\n"
                        f"DEAD WARNING  Nhân vật {CHARACTER_NAME} đã chết. Rank hiện tại là {rank}."
                    )
                    message_ids = []
                    for _ in range(10):
                        try:
                            msg = bot.send_message(chat_id=CHANNEL_ID, text=message)
                            message_ids.append(msg.message_id)
                        except Exception as e:
                            print(f"An error occurred while sending message: {e}")
                    try:
                        # Pin the first message out of the 5 sent messages
                        bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=message_ids[0])
                    except Exception as e:
                        print(f"An error occurred while pinning message: {e}")
                    return True, rank, experience  # Character is dead
                else:
                    rank = entry['rank']
                    return False, rank, experience  # Character is not dead
        return None, None, None  # Character not found
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return None, None, None

# Function to format experience with commas
def format_experience(experience):
    return f"{experience:,}"

def monitor_character() -> None:
    global last_message_time

    try:
        character_dead, rank, experience = fetch_data()
        current_time = datetime.now()

        if character_dead is None:
            try:
                bot.send_message(chat_id=CHANNEL_ID, text=f"Error API")
            except Exception as e:
                print(f"An error occurred while sending not found message: {e}")
            return
        elif character_dead:
            return
        else:
            formatted_experience = format_experience(experience)
            if last_message_time is None or (current_time - last_message_time).total_seconds() >= 3600:  # 1 hour
                message = (
                    f"NOT DEAD. Character {CHARACTER_NAME} is NOT DEAD."
                    f"Rank : {rank}.\n"                   
                    f"Experience is : {formatted_experience}.\n"
                    f"Nhân vật {CHARACTER_NAME} chưa chết. Rank hiện tại là {rank}."
                )
                try:
                    bot.send_message(chat_id=CHANNEL_ID, text=message)
                    last_message_time = current_time  # Update last_message_time only if the message is sent successfully
                except Exception as e:
                    print(f"An error occurred while sending not dead message: {e}")

            # Check if rank is 1 and send a special notification
            if rank == 1:
                special_message = (
                    f"CONGRATULATIONS! Character {CHARACTER_NAME} has reached rank 1!\n"
                    f"Experience is : {formatted_experience}.\n"
                    f"CHÚC MỪNG! Nhân vật {CHARACTER_NAME} đã đạt hạng 1!"
                )
                try:
                    bot.send_message(chat_id=CHANNEL_ID, text=special_message)
                except Exception as e:
                    print(f"An error occurred while sending rank 1 message: {e}")

    except Exception as e:
        print(f"An error occurred in the main loop: {e}")

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Bot started monitoring the character.")
    # Start monitoring immediately when the bot receives the /start command
    monitor_character()

def main() -> None:
    global last_message_time
    last_message_time = datetime.now() - timedelta(seconds=180)  # Initialize to allow immediate first message

    # Initialize updater and dispatcher
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Register the /start command
    dp.add_handler(CommandHandler("start", start))

    # Set up webhook
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=APP_URL + TOKEN)

    # Initialize APScheduler
    scheduler = BackgroundScheduler(timezone=pytz.utc)
    scheduler.add_job(monitor_character, 'interval', minutes=2)
    scheduler.start()

    # Keep the bot running
    updater.idle()

if __name__ == '__main__':
    main()
