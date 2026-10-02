from flask import Flask
from threading import Thread
import yfinance as yf,time,requests,os
from datetime import datetime, timedelta
import pytz
T=os.environ.get("BOT_TOKEN")
C=os.environ.get("CHAT_ID")
app=Flask("")
@app.route('/')
def h():return "ok"
def r():app.run(host='0.0.0.0',port=8080)
Thread(target=r).start()
def snd(m):
    try:
        url=f"https://api.telegram.org/bot{T}/sendMessage?chat_id={C}&text={m}"
        requests.get(url,timeout=10)
    except:pass
def rs(d):
    try:
        a=d['Close'].diff()
        g=a.where(a>0,0).rolling(14).mean()
        l=-a.where(a<0,0).rolling(14).mean()
        return 100-(100/(1+g/l))
    except:return d['Close']*0+50
IST=pytz.timezone('Asia/Kolkata')
snd("✅ BOT STARTED - GBP/JPY LIVE!")
def cmd_loop():
    offset=0
    while True:
        try:
            u=requests.get(f"https://api.telegram.org/bot{T}/getUpdates?offset={offset}&timeout=20",timeout=25).json()
            for x in u.get("result",[]):
                offset=x["update_id"]+1
                if "message" in x and "/start" in x["message"].get("text",""):
                    snd("🚀 GBP/JPY ULTRA STRONG BOT START!\nDin me 3-5 solid signal ayenge!\nExpiry: 5 Min")
        except:time.sleep(5)
        time.sleep(2)
Thread(target=cmd_loop).start()
while True:
    try:
        df=yf.download("GBPJPY=X",period="1d",interval="5m",progress=False)
        if len(df)<30:time.sleep(60);continue
        df['E9']=df['Close'].ewm(span=9).mean()
        df['E21']=df['Close'].ewm(span=21).mean()
        df['RSI']=rs(df)
        c=df.iloc[-1];p=df.iloc[-2]
        v=float(c['RSI'])
        now=datetime.now(IST)
        entry=now.strftime("%I:%M:%S %p")
        expiry=(now+timedelta(minutes=5)).strftime("%I:%M:%S %p")
        if p['E9']<p['E21'] and c['E9']>c['E21'] and 55<v<75:
            snd(f"🟢 BUY GBP/JPY - BINARY\n\n⏰ Entry: {entry}\n⏳ Expiry: {expiry} (5 Min)\n💰 Price: {float(c['Close']):.3f}\n📊 RSI: {v:.1f}")
        if p['E9']>p['E21'] and c['E9']<c['E21'] and 25<v<45:
            snd(f"🔴 SELL GBP/JPY - BINARY\n\n⏰ Entry: {entry}\n⏳ Expiry: {expiry} (5 Min)\n💰 Price: {float(c['Close']):.3f}\n📊 RSI: {v:.1f}")
        time.sleep(60)
    except:
        time.sleep(60)
