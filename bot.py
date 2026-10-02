import os, yfinance as yf, time, threading, requests
from flask import Flask
from datetime import datetime, timedelta
import pytz
T=os.environ.get("BOT_TOKEN")
C=os.environ.get("CHAT_ID")
app=Flask(__name__)
@app.route('/')
def home(): return "BOT IS LIVE - GBP/JPY 1MIN SYNC"
IST=pytz.timezone('Asia/Kolkata')
def snd(m):
 try: requests.post(f"https://api.telegram.org/bot{T}/sendMessage",data={"chat_id":C,"text":m,"parse_mode":"HTML"},timeout=10)
 except: pass
def rsi(df):
 d=df['Close'].diff()
 g=d.clip(lower=0).ewm(alpha=1/14).mean()
 l=(-d.clip(upper=0)).ewm(alpha=1/14).mean()
 return 100-(100/(1+g/l))
def get_data():
 try:
  df=yf.download("GBPJPY=X",period="1d",interval="1m",progress=False,auto_adjust=True)
  if df.empty: return None
  if hasattr(df.columns, 'levels'): df.columns=df.columns.get_level_values(0)
  return df
 except: return None
def analyze():
 df=get_data()
 if df is None or len(df)<50: return None,None,None
 df['RSI']=rsi(df)
 df['EMA9']=df['Close'].ewm(span=9).mean()
 df['EMA21']=df['Close'].ewm(span=21).mean()
 last=df.iloc[-1]; prev=df.iloc[-2]
 price=float(last['Close']); r=float(last['RSI'])
 e9=float(last['EMA9']); e21=float(last['EMA21'])
 if e9>e21 and price>e9: trend="BULLISH 🟢"
 elif e9<e21 and price<e9: trend="BEARISH 🔴"
 else: trend="SIDEWAYS 🟡"
 sig=None
 if prev['EMA9']<prev['EMA21'] and last['EMA9']>last['EMA21'] and r<70: sig="BUY"
 elif prev['EMA9']>prev['EMA21'] and last['EMA9']<last['EMA21'] and r>30: sig="SELL"
 return price,f"GBP/JPY: {price:.3f}\nRSI: {r:.1f}\nTrend: {trend}\nEMA9/21: {e9:.3f}/{e21:.3f}",sig
def market_open():
 now=datetime.now(IST)
 return now.weekday()<5
def cmd():
 o=0
 while True:
  try:
   r=requests.get(f"https://api.telegram.org/bot{T}/getUpdates?offset={o+1}&timeout=20",timeout=25).json()
   for u in r.get("result",[]):
    o=u["update_id"]
    txt=u.get("message",{}).get("text","")
    cid=str(u.get("message",{}).get("chat",{}).get("id",""))
    if cid!=str(C): continue
    if txt=="/start": snd("✅ BOT START HO GAYA DIDI!\n\nGBP/JPY 1-MIN LIVE SYNC ACTIVE 🚀\nCommands:\n/price - Live Price\n/status - Status")
    elif txt=="/price":
     p,det,s=analyze()
     snd(det if p else "Data loading...")
    elif txt=="/status": snd(f"BOT LIVE ✅\nTime: {datetime.now(IST).strftime('%H:%M:%S')} IST")
  except: time.sleep(2)
  time.sleep(1)
def loop():
 snd("🤖 BOT RESTARTED & LIVE\nGBP/JPY 1-Min Sync Started!")
 last=datetime.now(IST)-timedelta(minutes=10)
 while True:
  try:
   if market_open():
    p,det,s=analyze()
    if p and s:
     now=datetime.now(IST)
     if (now-last).total_seconds()>300:
      snd(f"🚨 <b>{s} SIGNAL</b> 🚨\n\n{det}\nTime: {now.strftime('%H:%M:%S')} IST")
      last=now
   time.sleep(60)
  except: time.sleep(60)
threading.Thread(target=lambda: app.run(host='0.0.0.0',port=10000),daemon=True).start()
threading.Thread(target=cmd,daemon=True).start()
loop()
