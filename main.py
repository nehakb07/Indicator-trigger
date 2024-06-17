from flask import Flask, render_template, request, redirect, url_for
import yfinance as yf
import pywhatkit as kit
import threading
import time

app = Flask(__name__)

def calculate_rsi(data, window=14):
    delta = data['Close'].diff(1)
    positive = delta.copy()
    negative = delta.copy()
    positive[positive < 0] = 0
    negative[negative > 0] = 0
    average_gain = positive.rolling(window=window).mean()
    average_loss = abs(negative.rolling(window=window).mean())
    relative_strength = average_gain / average_loss
    rsi = 100.0 - (100.0 / (1.0 + relative_strength))
    return rsi[-1]

def send_whatsapp_messages(ticker, phone_number, sleep_duration):
    while True:
        data = yf.download(ticker, period="7d", interval="1m")
        current_rsi = calculate_rsi(data)
        latest_value = data['Close'].iloc[-1]
        message = f"Latest value for {ticker}: {latest_value}\nLatest RSI value for {ticker}: {current_rsi:.2f}"
        kit.sendwhatmsg_instantly(phone_number, message)
        time.sleep(sleep_duration * 60)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-message', methods=['POST'])
def send_message():
    ticker = request.form['ticker']
    phone_number = request.form['phoneNumber']
    sleep_duration = int(request.form['sleepDuration'])
    
    threading.Thread(target=send_whatsapp_messages, args=(ticker, phone_number, sleep_duration)).start()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
