import os, time, yfinance as yf
from flask import Flask
from threading import Thread
import telebot

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = telebot.TeleBot(TOKEN)

app = Flask('')
@app.route('/')
def home(): return "ROBO M1 ONLINE"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🤖 ROBO M1 EUR/USD ATIVO 24H!\nVou te avisar quando tiver COMPRA ou VENDA!")

def analisar():
    try:
        df = yf.download("EURUSD=X", period="1d", interval="1m", progress=False)
        if len(df) < 210: return None
        df['EMA9']=df['Close'].ewm(span=9).mean()
        df['EMA21']=df['Close'].ewm(span=21).mean()
        df['EMA200']=df['Close'].ewm(span=200).mean()
        a=df.iloc[-2]
        venda_ok=float(a['EMA9'])<float(a['EMA21'])<float(a['EMA200'])
        compra_ok=float(a['EMA9'])>float(a['EMA21'])>float(a['EMA200'])
        if venda_ok and float(a['Close'])<float(a['EMA9']):
            return f"🔴 VENDA EUR/USD M1\nPreco:{float(a['Close']):.5f}"
        if compra_ok and float(a['Close'])>float(a['EMA9']):
            return f"🟢 COMPRA EUR/USD M1\nPreco:{float(a['Close']):.5f}"
        return None
    except:
        return None

def loop_sinais():
    ultimo=""
    while True:
        try:
            s=analisar()
            if s and s!=ultimo:
                bot.send_message(CHAT_ID, s)
                ultimo=s
            time.sleep(60)
        except:
            time.sleep(60)

Thread(target=loop_sinais, daemon=True).start()
bot.infinity_polling()
