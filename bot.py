import yfinance as yf, time, requests
BOT_TOKEN="PASTE_TOKEN_HERE"
CHAT_ID="PASTE_CHAT_ID_HERE"
def send(m):
 requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",data={"chat_id":CHAT_ID,"text":m})
def rsi(d):
 a=d['Close'].diff();g=a.where(a>0,0).rolling(14).mean();l=-a.where(a<0,0).rolling(14).mean();return 100-(100/(1+g/l))
send("BOT START")
while True:
 try:
  df=yf.download("GBPJPY=X",period="1d",interval="1m",progress=False)
  df['E9']=df['Close'].ewm(span=9).mean();df['E21']=df['Close'].ewm(span=21).mean();df['RSI']=rsi(df)
  la=df.iloc[-1];pr=df.iloc[-2]
  if pr['E9']<pr['E21'] and la['E9']>la['E21'] and 55<float(la['RSI'])<70:
   send(f"BUY GBP/JPY {float(la['Close'])}");time.sleep(120)
  if pr['E9']>pr['E21'] and la['E9']<la['E21'] and 30<float(la['RSI'])<45:
   send(f"SELL GBP/JPY {float(la['Close'])}");time.sleep(120)
  time.sleep(60)
 except: time.sleep(60)
