import os, time, threading, telebot, pytz
from flask import Flask
from datetime import datetime, timedelta
import yfinance as yf

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return 'GBPJPY Real Live - OK'

@bot.message_handler(commands=['g','start'])
def sig(m):
    try:
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        df = yf.download("GBPJPY=X", period='1d', interval='1m', progress=False, auto_adjust=True)
        c = float(df['Close'].iloc[-1].values[0])
        o = float(df['Open'].iloc[-1].values[0])
        dire = 'UP' if c >= o else 'DOWN'
        entry = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        wait = int((entry - now).total_seconds())
        if wait < 50:
            entry = entry + timedelta(minutes=1)
            wait = int((entry - now).total_seconds())
        expiry = entry + timedelta(minutes=1)
        msg = f"📊 {dire} * {round(c,3)} * | GBPJPY Real\nEntry * {entry.strftime('%H:%M:%S')} * ({wait}s)\nExpiry * {expiry.strftime('%H:%M:%S')}"
        bot.reply_to(m, msg)
    except Exception as e:
        bot.reply_to(m, f'Error {e}')

def run_bot():
    while True:
        try:
            print("Bot Started")
            bot.infinity_polling(timeout=20, long_polling_timeout=30)
        except Exception as e:
            print(f"Restart: {e}")
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
