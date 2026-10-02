import os, yfinance as yf, time, threading, requests
from flask import Flask
from datetime import datetime, timedelta
import pytz

T=os.environ.get("BOT_TOKEN")
C=os.environ.get("CHAT_ID")
app=Flask(__name__)
@app.route('/')
def home(): return "BOT LIVE"
IST=pytz.timezone('Asia/Kolkata')

def snd(m):
    try:
        requests.post(f"https://api.telegram.org/bot{T}/sendMessage",data={"chat_id":C,"text":m,"parse_mode":"Markdown"},timeout=10)
    except: pass

def rsi(df):
    d=df['Close'].diff()
    g=d.clip(lower=0).ewm(alpha=1/14).mean()
    l=(-d.clip(upper=0)).ewm(alpha=1/14).mean()
    return 100-(100/(1+g/l))

def cmd():
    o=0
    while True:
        try:
            r=requests.get(f"https://api.telegram.org/bot{T}/getUpdates?offset={o}&timeout=15",timeout=20).json()
            for u in r.get("result",[]):
                o=u["update_id"]+1
                txt=u.get("message",{}).get("text","")
                if "/start" in txt:
                    snd("✅ *BOT START HO GAYA DIDi!*\n⏰ 1 MIN REAL MARKET SYNC ON HAI\n💹 GBP/JPY")
        except: time.sleep(2)
        time.sleep(2)

def run_flask():
    app.run(host="0.0.0.0",port=8080)

threading.Thread(target=run_flask,daemon=True).start()
threading.Thread(target=cmd,daemon=True).start()

while True:
    try:
        df=yf.download("GBPJPY=X",period="1d",interval="1m",progress=False)
        if len(df)<30:
            time.sleep(30);continue
        df['E9']=df['Close'].ewm(span=9).mean()
        df['E21']=df['Close'].ewm(span=21).mean()
        df['RSI']=rsi(df)
        c=df.iloc[-1]; p=df.iloc[-2]; v=float(c['RSI'])
        now=datetime.now(IST)
        nxt=(now+timedelta(minutes=1)).replace(second=0,microsecond=0)
        entry=nxt.strftime("%I:%M:00 %p")
        expiry=(nxt+timedelta(minutes=2)).strftime("%I:%M:00 %p")
        if now.second>=50:
            if p['E9']<p['E21'] and c['E9']>c['E21'] and 55<v<75:
                snd(f"🟢 *BUY GBP/JPY*\n\n⏰ Entry: `{entry}`\n⏳ Expiry: `{expiry}`\n💹 Price: {float(c['Close']):.3f}\n📈 RSI: {v:.1f}\n\n*ABHI BINARY PE LAGAO*")
                time.sleep(70);continue
            if p['E9']>p['E21'] and c['E9']<c['E21'] and 25<v<45:
                snd(f"🔴 *SELL GBP/JPY*\n\n⏰ Entry: `{entry}`\n⏳ Expiry: `{expiry}`\n💹 Price: {float(c['Close']):.3f}\n📉 RSI: {v:.1f}\n\n*ABHI BINARY PE LAGAO*")
                time.sleep(70);continue
        time.sleep(1)
    except Exception as e:
        print(e);time.sleep(10)
