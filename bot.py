import os, threading, yfinance as yf, telebot
from flask import Flask
from datetime import datetime, timedelta
import pytz
BOT_TOKEN=os.getenv("BOT_TOKEN")
bot=telebot.TeleBot(BOT_TOKEN)
app=Flask(__name__)
@app.route('/')
def home():return 'BOT LIVE'
@bot.message_handler(commands=['start','signal'])
def sig(m):
 try:
  d=yf.download("GBPJPY=X",period="1d",interval="1m",progress=False,auto_adjust=True)
  price=float(d['Close'].iloc[-1])
  prev=float(d['Close'].iloc[-2])
  dire="UP BUY" if price>prev else "DOWN SELL"
  ist=pytz.timezone('Asia/Kolkata')
  now=datetime.now(ist)
  entry=now+timedelta(minutes=1)
  bot.reply_to(m,f"GBPJPY REAL\n{dire}\nPrice:{round(price,5)}\nTime:{now.strftime('%H:%M:%S')}\nEntry:{entry.strftime('%H:%M:%S')}")
 except Exception as e:bot.reply_to(m,f"Error:{e}")
def run_bot():bot.infinity_polling()
threading.Thread(target=run_bot,daemon=True).start()
app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
