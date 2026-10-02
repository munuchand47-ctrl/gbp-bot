from flask import Flask
from threading import Thread
import yfinance as yf,time,requests,os
T=os.environ.get("BOT_TOKEN")
C=os.environ.get("CHAT_ID")
app=Flask("")
@app.route('/')
def h():return"ok"
def r():app.run(host='0.0.0.0',port=8080)
Thread(target=r).start()
def snd(m):requests.get(f"https://api.telegram.org/bot{T}/sendMessage?chat_id={C}&text={m}")
def rs(d):
 a=d['Close'].diff()
 g=a.where(a>0,0).rolling(14).mean()
 l=-a.where(a<0,0).rolling(14).mean()
 return 100-(100/(1+g/l))
snd("BOT STARTED")
while True:
 try:
  df=yf.download("GBPJPY=X",period="1d",interval="1m")
  df['E9']=df['Close'].ewm(span=9).mean()
  df['E21']=df['Close'].ewm(span=21).mean()
  df['RSI']=rs(df)
  c=df.iloc[-1];p=df.iloc[-2]
  v=float(c['RSI'])
  if p['E9']<p['E21'] and c['E9']>c['E21'] and 55<v<75:snd(f"BUY {float(c['Close']):.3f}");time.sleep(300)
  if p['E9']>p['E21'] and c['E9']<c['E21'] and 25<v<45:snd(f"SELL {float(c['Close']):.3f}");time.sleep(300)
  time.sleep(60)
 except:time.sleep(60)
