import os
import requests
import asyncio
from datetime import datetime, timedelta
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes

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
monitoring = False

# Function to fetch data from the API and check the character's status
async def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
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
                        msg = await bot.send_message(chat_id=CHANNEL_ID, text=message)
                        message_ids.append(msg.message_id)
                    # Pin the first message out of the 5 sent messages
                    await bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=message_ids[0])
                    return True, rank  # Character is dead
                else:
                    rank = entry['rank']
                    return False, rank  # Character is not dead
        return None, None  # Character not found
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None, None

# Function to start the bot and set up data fetching intervals
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    global last_message_time, monitoring
    if monitoring:
        await update.message.reply_text("Monitoring is already running.")
        return
    monitoring = True
    last_message_time = None
    await update.message.reply_text('Bot đã bắt đầu theo dõi nhân vật.')

    while monitoring:
        character_dead, rank = await fetch_data()
        current_time = datetime.now()

        if character_dead is None:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=f"Character {CHARACTER_NAME} not found.")
            break
        elif character_dead:
            break
        else:
            if last_message_time is None or (current_time - last_message_time).total_seconds() >= 1800:
                message = (
                    f"YEAH NOT DEAD. Character {CHARACTER_NAME} is NOT DEAD. Current rank is {rank}.\n"
                    f"Nhân vật {CHARACTER_NAME} chưa chết. Rank hiện tại là {rank}."
                )
                await bot.send_message(chat_id=CHANNEL_ID, text=message)
                last_message_time = current_time

        await asyncio.sleep(31)  # Fetch data every minute

async def stop(update, context: ContextTypes.DEFAULT_TYPE):
    global monitoring
    if not monitoring:
        await update.message.reply_text("Bot is not currently monitoring.")
        return
    monitoring = False
    await update.message.reply_text("Bot has stopped monitoring.")

async def restart(update, context: ContextTypes.DEFAULT_TYPE):
    await stop(update, context)
    await start(update, context)

async def fetch(update, context: ContextTypes.DEFAULT_TYPE):
    character_dead, rank = await fetch_data()
    if character_dead is None:
        await update.message.reply_text(f"Character {CHARACTER_NAME} not found or an error occurred.")
    elif character_dead:
        await update.message.reply_text(f"DEAD WARNING: Character {CHARACTER_NAME} is DEAD. Current rank is {rank}.")
    else:
        await update.message.reply_text(f"Character {CHARACTER_NAME} is NOT DEAD. Current rank is {rank}.")

async def status(update, context: ContextTypes.DEFAULT_TYPE):
    global last_message_time
    if not monitoring:
        await update.message.reply_text("Bot is not currently monitoring.")
    else:
        next_message_time = last_message_time + timedelta(seconds=1800) if last_message_time else "N/A"
        await update.message.reply_text(f"Monitoring is active. Last message sent at: {last_message_time}. Next message will be sent at: {next_message_time}.")

async def main():
    # Initialize application
    application = Application.builder().token(TOKEN).build()
    
    # Register the /start, /stop, /restart, /fetch, and /status commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("restart", restart))
    application.add_handler(CommandHandler("fetch", fetch))
    application.add_handler(CommandHandler("status", status))

    # Set up webhook
    await application.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=APP_URL + TOKEN)
    
    # Keep the bot running
    await application.updater.start_polling()
    await application.idle()

if __name__ == '__main__':
    asyncio.run(main())
