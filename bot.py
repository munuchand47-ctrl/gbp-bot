import os
import threading
import yfinance as yf
import telebot
import pytz
from flask import Flask
from datetime import datetime, timedelta

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return 'GBPJPY Real Market Live'

@bot.message_handler(commands=['start', 'g'])
def sig(m):
    try:
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        df = yf.download('GBPJPY=X', period='1d', interval='1m', progress=False, auto_adjust=True)
        o = float(df['Open'].iloc[-1])
        c = float(df['Close'].iloc[-1])
        p = float(df['Close'].iloc[-2])
        dire = 'DOWN' if o > c and c < p else 'UP'
        entry = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        wait = int((entry - now).total_seconds())
        if wait < 50:
            entry = entry + timedelta(minutes=1)
            wait = int((entry - now).total_seconds())
        end = entry + timedelta(minutes=1)
        tf = "%H:%M"
        msg = dire + " " + str(round(c,3)) + " | GBPJPY Real\nEntry " + entry.strftime(tf) + ":00 (" + str(wait) + "s)\nEnd " + end.strftime(tf) + ":00 | 1 MIN"
        bot.reply_to(m, msg)
    except Exception as e:
        bot.reply_to(m, "Error " + str(e))

def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()
app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
