import asyncio
import websockets
import json
import sqlite3
import os
import time
import numpy as np
from datetime import datetime

DB_NAME = os.path.join(os.path.dirname(__file__), 'trading_system.db')
APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID', 'YOUR_KEY')
APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY', 'YOUR_SECRET')

# Strategy Parameters
PERIOD = 20
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
BB_STD = 2.0

# State
price_history = {
    'BTC/USD': [],
    'ETH/USD': []
}
current_candle = {
    'BTC/USD': {'start': 0, 'close': 0},
    'ETH/USD': {'start': 0, 'close': 0}
}
CANDLE_TIMEFRAME_SEC = 60 # 1 minute candles

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50 # Default neutral
    prices_array = np.array(prices)
    deltas = np.diff(prices_array)
    seed = deltas[:period]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down if down != 0 else 0
    rsi = np.zeros_like(prices_array)
    rsi[:period] = 100. - 100./(1.+rs)
    for i in range(period, len(prices_array)):
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

def calculate_bollinger_bands(prices, period=20, std_dev=2.0):
    if len(prices) < period:
        return None, None, None
    prices_array = np.array(prices)
    sma = np.mean(prices_array[-period:])
    std = np.std(prices_array[-period:])
    upper_band = sma + (std_dev * std)
    lower_band = sma - (std_dev * std)
    return sma, upper_band, lower_band

def log_order(asset, side, price):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        qty = 0.01 if asset == 'BTC/USD' else 0.1 # Dummy fixed quantities for now
        cursor.execute('''
            INSERT INTO order_book (order_id, asset_symbol, order_type, side, quantity, price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (f"crypto_{int(time.time())}", asset, 'market', side, qty, price, 'pending'))
        conn.commit()
        conn.close()
        print(f"[{datetime.now()}] Signal logged: {side} {qty} {asset} @ {price}")
    except Exception as e:
        print(f"Error logging order: {e}")

def process_crypto_message(message_data):
    try:
        data = json.loads(message_data)
        for msg in data:
            if msg.get('T') == 't': # Trade message
                sym = msg.get('S')
                price = msg.get('p')
                timestamp_str = msg.get('t')
                
                if not price or sym not in current_candle:
                    continue
                
                now = time.time()
                candle = current_candle[sym]
                
                if candle['start'] == 0:
                    candle['start'] = now
                
                candle['close'] = price
                
                # Check if candle time is up
                if now - candle['start'] >= CANDLE_TIMEFRAME_SEC:
                    price_history[sym].append(candle['close'])
                    candle['start'] = now # Reset for next candle
                    
                    # Keep max 50 prices to save memory
                    if len(price_history[sym]) > 50:
                        price_history[sym].pop(0)
                        
                    # Evaluate Strategy
                    evaluate_strategy(sym)

    except Exception as e:
        print(f"Error processing crypto stream: {e}")

def evaluate_strategy(asset):
    prices = price_history[asset]
    if len(prices) < PERIOD:
        return
    
    current_price = prices[-1]
    rsi = calculate_rsi(prices, period=14)
    sma, upper_bb, lower_bb = calculate_bollinger_bands(prices, period=PERIOD, std_dev=BB_STD)
    
    if sma is None:
        return

    print(f"[{datetime.now()}] {asset} - Price: {current_price}, RSI: {rsi:.2f}, BB Lower: {lower_bb:.2f}, BB Upper: {upper_bb:.2f}")

    # Mean Reversion + Breakout Strategy Logic
    if current_price < lower_bb and rsi < RSI_OVERSOLD:
        print(f"*** BULLISH SIGNAL DETECTED for {asset} ***")
        log_order(asset, 'buy', current_price)
    elif current_price > upper_bb and rsi > RSI_OVERBOUGHT:
        print(f"*** BEARISH SIGNAL DETECTED for {asset} ***")
        log_order(asset, 'sell', current_price)


async def connect_alpaca_stream():
    uri = "wss://stream.data.alpaca.markets/v1beta3/crypto/us"
    print(f"Connecting to Alpaca Crypto Stream at {uri}...")
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                auth_message = {"action": "auth", "key": APCA_API_KEY_ID, "secret": APCA_API_SECRET_KEY}
                await websocket.send(json.dumps(auth_message))
                auth_response = await websocket.recv()
                print(f"Auth response: {auth_response}")
                
                subscribe_message = {"action": "subscribe", "trades": ["BTC/USD", "ETH/USD"]}
                await websocket.send(json.dumps(subscribe_message))
                sub_response = await websocket.recv()
                print(f"Sub response: {sub_response}")

                async for message in websocket:
                    process_crypto_message(message)
        except Exception as e:
            print(f"WebSocket connection error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

def main():
    print("Starting 24/7 Crypto Manager...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_alpaca_stream())

if __name__ == "__main__":
    main()
