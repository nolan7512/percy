import requests
import time
from telegram import Bot
from telegram.ext import Updater, CommandHandler

# Thay thế bằng token bot của bạn
TOKEN = '7324758222:AAGCiGsotQ6Y-eVgoXrwPDNRSAP5GFNxsq4'

# ID của nhóm nơi bot sẽ gửi thông báo (bắt đầu bằng @)
CHANNEL_ID = '@percy_verence_poe2'

# URL của API
API_URL = 'https://pathofexile2.com/internal-api/content/game-ladder/id/Hardcore'

# Tên nhân vật cần kiểm tra
CHARACTER_NAME = 'Percy_Verence'

# Biến cờ để kiểm soát việc tiếp tục fetch dữ liệu và gửi thông điệp
continue_fetching = True

# Khởi tạo bot
bot = Bot(token=TOKEN)

# Hàm fetch dữ liệu từ API và kiểm tra trạng thái của nhân vật
def fetch_data():
    global continue_fetching
    response = requests.get(API_URL)
    data = response.json()

    for entry in data['context']['ladder']['entries']:
        if entry['character']['name'] == CHARACTER_NAME:
            if entry['dead']:
                message = f"Nhân vật {CHARACTER_NAME} đã chết."
                message_ids = []
                for _ in range(5):
                    msg = bot.send_message(chat_id=CHANNEL_ID, text=message)
                    message_ids.append(msg.message_id)
                # Ghim tin nhắn đầu tiên trong số 5 tin nhắn
                bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=message_ids[0])
                # Ngừng việc fetch dữ liệu
                continue_fetching = False
            else:
                rank = entry['rank']
                message = f"Nhân vật {CHARACTER_NAME} chưa chết. Rank hiện tại là {rank}."
                bot.send_message(chat_id=CHANNEL_ID, text=message)
            break

# Hàm khởi động bot và thiết lập thời gian fetch dữ liệu
def start(update, context):
    update.message.reply_text('Bot đã bắt đầu theo dõi nhân vật.')
    while continue_fetching:
        fetch_data()
        time.sleep(60)

# Khởi tạo bot và thiết lập command handler
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
updater.idle()