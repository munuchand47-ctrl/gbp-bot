import requests, pytz
from datetime import datetime
from collections import deque
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8985357955:AAHUQLYoSgxF0Oawjqoo_xQAfxoiLy_r6L0"
URL = "https://api.exchangerate.host/convert"
price_history = deque(maxlen=5)
chat_ids = set()

def get_price():
    try:
        r = requests.get(f"{URL}?from=GBP&to=JPY", timeout=10).json()
        return float(r['result'])
    except: return None

async def q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ids.add(update.effective_chat.id)
    p = get_price()
    if not p:
        await update.message.reply_text("Market Error")
        return
    price_history.append(p)

    # Analysis
    msg = f"📊 GBP/JPY LIVE\nPrice: {p:.3f}\n\n"

    # 1 Min Check
    if len(price_history) >= 2:
        d1 = price_history[-1] - price_history[-2]
        if d1 > 0: msg += f"1 Min: UP 🟢 (+{d1:.4f})\n"
        elif d1 < 0: msg += f"1 Min: DOWN 🔴 ({d1:.4f})\n"
        else: msg += f"1 Min: WAIT ⚪\n"

    # 3 Min Check
    if len(price_history) >= 3:
        d3 = price_history[-1] - price_history[-3]
        if d3 > 0.02: msg += f"3 Min: UP TREND 🟢🟢 ({d3:+.4f}) - BUY Dekha\n"
        elif d3 < -0.02: msg += f"3 Min: DOWN TREND 🔴🔴 ({d3:+.4f}) - SELL Dekha\n"
        else: msg += f"3 Min: WAIT ⚪ Sideways\n"

    # 5 Min Check
    if len(price_history) >= 5:
        d5 = price_history[-1] - price_history[0]
        ups = sum(1 for i in range(1,5) if price_history[i] > price_history[i-1])
        if ups >= 3 and d5 > 0:
            msg += f"\n5 Min FINAL: ✅ UP - ENTRY BUY\n({ups}/4 bar up, {d5:+.4f})"
        elif ups <= 1 and d5 < 0:
            msg += f"\n5 Min FINAL: ✅ DOWN - ENTRY SELL\n({4-ups}/4 bar down, {d5:+.4f})"
        else:
            msg += f"\n5 Min FINAL: ⏳ WAIT - Entry Nahi\nMarket Confuse Achhi"
    else:
        msg += f"\nData: {len(price_history)}/5 min - {5-len(price_history)} min pare full analysis asiba"

    t = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%I:%M:%S %p")
    msg += f"\nTime: {t}"
    await update.message.reply_text(msg)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("q1", q1))
app.add_handler(CommandHandler("start", q1))
app.run_polling()
