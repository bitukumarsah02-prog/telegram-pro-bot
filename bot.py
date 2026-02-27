import telebot
from telebot.types import *
import json
import os

# ===== ENV VARIABLES (Render se aayega) =====
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"

# ===== DATA FILE CREATE =====
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({
            "auto": False,
            "welcome": "Welcome to our channel!",
            "users": []
        }, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ===== ADMIN PANEL =====
def admin_panel():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Auto Approve")
    markup.row("Set Welcome")
    markup.row("Broadcast")
    markup.row("Stats")
    return markup

# ===== START COMMAND =====
@bot.message_handler(commands=["start"])
def start(message):
    data = load_data()

    if message.from_user.id not in data["users"]:
        data["users"].append(message.from_user.id)
        save_data(data)

    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔥 ADMIN PANEL", reply_markup=admin_panel())
    else:
        bot.send_message(message.chat.id, data["welcome"])

# ===== JOIN REQUEST HANDLER =====
@bot.chat_join_request_handler()
def handle_join_request(request):
    data = load_data()
    user_id = request.from_user.id

    try:
        bot.send_message(user_id, data["welcome"])
    except:
        pass

    if data["auto"]:
        bot.approve_chat_join_request(CHANNEL_ID, user_id)

# ===== AUTO APPROVE TOGGLE =====
@bot.message_handler(func=lambda m: m.text == "Auto Approve")
def toggle_auto(message):
    if message.from_user.id == ADMIN_ID:
        data = load_data()
        data["auto"] = not data["auto"]
        save_data(data)
        status = "ON ✅" if data["auto"] else "OFF ❌"
        bot.send_message(message.chat.id, f"Auto Approve is now {status}")

# ===== SET WELCOME MESSAGE =====
@bot.message_handler(func=lambda m: m.text == "Set Welcome")
def set_welcome(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "Send new welcome message:")
        bot.register_next_step_handler(msg, save_welcome)

def save_welcome(message):
    data = load_data()
    data["welcome"] = message.text
    save_data(data)
    bot.send_message(message.chat.id, "Welcome message updated ✅")

# ===== BROADCAST =====
@bot.message_handler(func=lambda m: m.text == "Broadcast")
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "Send broadcast message:")
        bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    data = load_data()
    success = 0
    for user in data["users"]:
        try:
            bot.send_message(user, message.text)
            success += 1
        except:
            pass
    bot.send_message(message.chat.id, f"Broadcast sent to {success} users ✅")

# ===== STATS =====
@bot.message_handler(func=lambda m: m.text == "Stats")
def stats(message):
    data = load_data()
    bot.send_message(message.chat.id, f"Total Users: {len(data['users'])}")

print("Bot is running...")
bot.infinity_polling()
