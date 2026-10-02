nimport os
import time
import threading
import yfinance as yf
import telebot
from flask import Flask

# Token Render ke ENV se lega
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN") or "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)
@app.route('/')
def home():
    return "GBP/JPY BOT LIVE!"

@bot.message_handler(commands=['start'])
def start_msg(m):
    bot.reply_to(m, "✅ GBP/JPY BOT LIVE ON RENDER!\n\nCommands:\n/price - Live Price\n/signal - Strong Signal")

@bot.message_handler(commands=['price'])
def price_msg(m):
    try:
        df = yf.download("GBPJPY=X", period="1d", interval="5m", progress=False)
        price = float(df['Close'].iloc[-1])
        bot.reply_to(m, f"💰 GBP/JPY: {price:.3f}")
    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

@bot.message_handler(commands=['signal'])
def signal_msg(m):
    try:
        df = yf.download("GBPJPY=X", period="1d", interval="5m", progress=False)
        close = df['Close']
        ema9 = close.ewm(span=9).mean().iloc[-1]
        ema21 = close.ewm(span=21).mean().iloc[-1]
        if ema9 > ema21:
            bot.reply_to(m, f"📈 STRONG BUY Signal\nEMA9 {ema9:.3f} > EMA21 {ema21:.3f}")
        else:
            bot.reply_to(m, f"📉 STRONG SELL Signal\nEMA9 {ema9:.3f} < EMA21 {ema21:.3f}")
    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

def run_bot():
    while True:
        try:
            print("Polling Started...")
            bot.infinity_polling()
        except Exception as e:
            print(f"Bot Error: {e}")
            time.sleep(5)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    run_flask()
