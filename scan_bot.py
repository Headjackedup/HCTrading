import sqlite3
import datetime
import numpy as np
import requests
import os

DB_NAME = os.path.join(os.path.dirname(__file__), 'trading_system.db')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID')

def get_market_data():
    # Placeholder for fetching data via Alpaca or another source
    # E.g., fetch SPY daily candles
    return {
        'SPY': np.random.randn(100).cumsum() + 400
    }

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50 # Default neutral
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100./(1.+rs)
    for i in range(period, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up*(period-1) + upval)/period
        down = (down*(period-1) + downval)/period
        rs = up/down if down != 0 else 0
        rsi[i] = 100. - 100./(1.+rs)
    return rsi[-1]

def determine_sentiment(rsi_value):
    if rsi_value > 70:
        return "Bearish" # Overbought
    elif rsi_value < 30:
        return "Bullish" # Oversold
    else:
        return "Neutral"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def main():
    print(f"[{datetime.datetime.now()}] Running morning scan...")
    data = get_market_data()
    spy_prices = data.get('SPY')
    
    rsi = calculate_rsi(spy_prices)
    sentiment = determine_sentiment(rsi)
    
    # Write to database
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE system_state SET market_sentiment = ?, timestamp = CURRENT_TIMESTAMP WHERE id = (SELECT id FROM system_state ORDER BY id DESC LIMIT 1)", (sentiment,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

    # Send telegram message
    message = f"☀️ *Morning Scan Alert*\n\n" \
              f"**Market Sentiment:** {sentiment}\n" \
              f"**SPY RSI:** {rsi:.2f}\n" \
              f"**Sector Momentum:** Neutral\n" \
              f"**Watchlist:** SPY, QQQ, IWM"
    
    send_telegram_alert(message)
    print("Scan complete.")

if __name__ == "__main__":
    main()
