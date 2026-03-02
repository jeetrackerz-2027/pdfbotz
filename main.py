import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import json

TOKEN = "8514168337:AAFi-EBRfCttHxQH2iWDfRLirDINqMOfYYY"
ADMIN_ID = 7371121826
CHANNELS = ["@jeetrackerz", "@JEECBSENEETBOOKS"]

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

DATA_FILE = "data.json"

try:
    with open(DATA_FILE) as f:
        data = json.load(f)
except:
    data = {"books": {}}

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def check_join(user_id):
    for ch in CHANNELS:
        member = bot.get_chat_member(ch, user_id)
        if member.status not in ["member", "administrator", "creator"]:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    if not check_join(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🔘 Join Channel 1", url="https://t.me/jeetrackerz")
        )
        markup.add(
            InlineKeyboardButton("🔘 Join Channel 2", url="https://t.me/JEECBSENEETBOOKS")
        )
        markup.add(
            InlineKeyboardButton("🎀 Try Again", callback_data="check_again")
        )

        bot.send_message(
            message.chat.id,
            "⚠️ Access Denied!\n\n"
            "Pehle dono channel join karo.\n"
            "Join karne ke baad 🎀 Try Again dabao.",
            reply_markup=markup
        )
        return

    if len(args) > 1:
        key = args[1]
        file_id = data["books"].get(key)

        if file_id:
            bot.send_document(message.chat.id, file_id)
        else:
            bot.send_message(message.chat.id, "❌ Link expired ya book nahi mili.")
    else:
        bot.send_message(message.chat.id, "Valid link use karo.")

@bot.callback_query_handler(func=lambda call: call.data == "check_again")
def check_again(call):
    user_id = call.from_user.id

    if not check_join(user_id):
        bot.answer_callback_query(call.id, "Abhi bhi join nahi kiya 😒")
        return

    bot.answer_callback_query(call.id, "✅ Join verified!")
    bot.send_message(call.message.chat.id, "Ab link dubara open karo.")

@bot.message_handler(commands=['add'])
def add_book(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "PDF bhejo aur caption me book ka key likho.")

@bot.message_handler(content_types=['document'])
def save_book(message):
    if message.from_user.id != ADMIN_ID:
        return

    key = message.caption
    file_id = message.document.file_id

    data["books"][key] = file_id
    save()

    bot.reply_to(message, f"{key} saved ✅")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "", 200

@app.route("/")
def index():
    return "Bot running"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://jee-cbse-bot.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=10000)
