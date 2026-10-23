import os, time, yfinance as yf
from flask import Flask
from threading import Thread
import telebot
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = telebot.TeleBot(TOKEN)
app = Flask('')
@app.route('/')
def home(): return "ROBO M1 COMPRA E VENDA 24H"
def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run, daemon=True).start()
def analisar():
    df = yf.download("EURUSD=X", period="1d", interval="1m", progress=False)
    if len(df) < 210: return None
    df['EMA9'] = df['Close'].ewm(span=9).mean()
    df['EMA21'] = df['Close'].ewm(span=21).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    a = df.iloc[-2]
    ant = df.iloc[-3]
    fraqueza_compra = float(ant['Close']) > float(ant['Open']) and float(ant['High'] - ant['Close']) > abs(float(ant['Close']-ant['Open']))
    pavio_baixo = float(ant['Open'] - ant['Low']) if float(ant['Close']) < float(ant['Open']) else float(ant['Close'] - ant['Low'])
    fraqueza_venda = pavio_baixo > abs(float(ant['Close']-ant['Open']))
    venda_ok = float(a['EMA9']) < float(a['EMA21']) < float(a['EMA200']) and float(a['Close']) < float(a['EMA9'])
    compra_ok = float(a['EMA9']) > float(a['EMA21']) > float(a['EMA200']) and float(a['Close']) > float(a['EMA9'])
    if venda_ok and fraqueza_compra and float(a['Close']) < float(a['Open']):
        return f"🔴 VENDA EUR/USD M1\nPreco: {float(a['Close']):.5f}"
    if compra_ok and fraqueza_venda and float(a['Close']) > float(a['Open']):
        return f"🟢 COMPRA EUR/USD M1\nPreco: {float(a['Close']):.5f}"
    return None
ultimo=""
while True:
    try:
        s=analisar()
        if s and s!=ultimo:
            bot.send_message(CHAT_ID, s)
            ultimo=s
        time.sleep(60)
    except: time.sleep(60)
