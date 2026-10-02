import os
import threading
import yfinance as yf
import telebot
from flask import Flask
from datetime import datetime, timedelta

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "BOT LIVE"

@bot.message_handler(commands=['start','signal'])
def sig(m):
    try:
        d = yf.download("GBPUSD=X", period="1d", interval="1m")
        price = float(d['Close'].iloc[-1])
        prev = float(d['Close'].iloc[-2])
        dire = "UP 🟢 BUY" if price > prev else "DOWN 🔴 SELL"
        now = datetime.now() + timedelta(hours=5, minutes=30)
        entry = now + timedelta(minutes=1)
        txt = f"{dire}\n\n💰 Price: {price:.5f}\n⏰ Time: {now.strftime('%I:%M:%S %p')}\n🎯 Entry: {entry.strftime('%I:%M %p')}\n⏳ Expiry: 1 Min\n✅ GBP/USD REAL"
        bot.reply_to(m, txt)
    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
