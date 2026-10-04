import os,threading
import yfinance as yf,telebot
from flask import Flask
from datetime import datetime,timedelta
import pytz

BOT_TOKEN=os.getenv("BOT_TOKEN")
bot=telebot.TeleBot(BOT_TOKEN)
app=Flask(__name__)

@app.route('/')
def home():
    return 'GBPJPY REAL LIVE'

@bot.message_handler(commands=['start','signal','g'])
def sig(m):
    try:
        ist=pytz.timezone('Asia/Kolkata')
        now=datetime.now(ist)
        if now.weekday()>=5:
            bot.reply_to(m,"REAL MARKET CLOSED")
            return
        df=yf.download("GBPJPY=X",period="1d",interval="1m",progress=False,auto_adjust=True)
        o=float(df['Open'].iloc[-1])
        h=float(df['High'].iloc[-1])
        l=float(df['Low'].iloc[-1])
        c=float(df['Close'].iloc[-1])
        p=float(df['Close'].iloc[-2])
        upper=h-max(o,c)
        lower=min(o,c)-l
        bear=c<o and c<p and upper>lower
        dire="DOWN SELL" if bear else "UP BUY"
        entry=now+timedelta(minutes=1)
        msg=f"GBPJPY REAL Price:{round(c,3)} Signal:{dire} Entry:{entry.strftime('%H:%M:00')}"
        bot.reply_to(m,msg)
    except Exception as e:
        bot.reply_to(m,f"Error:{e}")

def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot,daemon=True).start()
app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
