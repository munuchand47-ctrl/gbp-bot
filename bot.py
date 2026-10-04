import os
import threading
import yfinance as yf
import telebot
from flask import Flask
from datetime import datetime, timedelta
import pytz

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return 'GBPJPY REAL LIVE'

@bot.message_handler(commands=['start','signal','g'])
def sig(m):
    try:
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)

        if now.weekday() >= 5:
            bot.reply_to(m, 'REAL MARKET CLOSED')
            return

        df = yf.download('GBPJPY=X', period='1d', interval='1m', progress=False, auto_adjust=True)

        if len(df) < 3:
            bot.reply_to(m, 'Market data loading...')
            return

        o = float(df['Open'].iloc[-1])
        c = float(df['Close'].iloc[-1])
        p = float(df['Close'].iloc[-2])

        upper = max(o, c)
        lower = min(o, c)

        bear = o > c and c < p
        dire = "DOWN SELL" if bear else "UP BUY"

        # 50 SECOND LOGIC - MISS HEBA NAHI
        entry = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        if (entry - now).seconds < 50:
            entry = entry + timedelta(minutes=1)

        msg = f"GBPJPY REAL Price: {round(c,3)} Signal: {dire} Entry: {entry.strftime('%H:%M')} - 50 Sec Baki - Miss Heba Nahi"
        bot.reply_to(m, msg)

    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()
app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
