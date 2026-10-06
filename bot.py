import telebot
import random
import time
from datetime import datetime, timedelta

BOT_TOKEN = '8985357955:AAHUQLYoSgxF00awjqoo_xQAfcoiIy_r6LQ'
bot = telebot.TeleBot(BOT_TOKEN)


last_signal = 0
last_direction = "UP"

def make_signal():
    global last_direction
    # 50/50 Mix Logic - UP UP kebe heba nahi
    if last_direction == "UP":
        direction = random.choices(["DOWN", "UP"], weights=[70, 30])[0]
    else:
        direction = random.choices(["UP", "DOWN"], weights=[70, 30])[0]

    last_direction = direction
    price = round(random.uniform(208.500, 209.800), 3)
    tf = random.choice([1, 2, 3, 5])
    wait = random.randint(85, 95)
    now = datetime.now()
    entry = now + timedelta(seconds=wait)
    expiry = entry + timedelta(minutes=tf)

    return f"""{direction} * {price} * | GBPJPY Real
Entry * {entry.strftime('%H:%M:%S')} * ({wait}s)
Expiry * {expiry.strftime('%H:%M:%S')} * [{tf}M]"""

@bot.message_handler(commands=['g'])
def g_signal(message):
    global last_signal
    if time.time() - last_signal < 40:
        bot.reply_to(message, f"⏳ Wait {int(40-(time.time()-last_signal))}s Sango!")
        return
    last_signal = time.time()
    bot.reply_to(message, make_signal())

print("Bot Started... Sango!")
bot.infinity_polling()
