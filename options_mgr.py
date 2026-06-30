import sqlite3
import datetime
import os

DB_NAME = os.path.join(os.path.dirname(__file__), 'trading_system.db')

def fetch_market_sentiment():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT market_sentiment FROM system_state ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception as e:
        print(f"Database error: {e}")
    return "Neutral"

def scan_options_chain(underlying="SPY", sentiment="Neutral"):
    print(f"Scanning options chain for {underlying} (Sentiment: {sentiment})...")
    # Placeholder for Charles Schwab/Public.com API integration
    # Ideally, we look for 0DTE to 7DTE, Gamma > threshold
    
    selected_options = []
    
    if sentiment == "Bullish":
        selected_options.append({"symbol": f"{underlying}_CALL_0DTE", "gamma": 0.05, "action": "BUY"})
    elif sentiment == "Bearish":
        selected_options.append({"symbol": f"{underlying}_PUT_0DTE", "gamma": 0.06, "action": "BUY"})
        
    return selected_options

def write_orders_to_book(options):
    if not options:
        return
        
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        for opt in options:
            cursor.execute('''
                INSERT INTO order_book (order_id, asset_symbol, order_type, side, quantity, price, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (f"OPT_{int(datetime.datetime.now().timestamp())}", opt['symbol'], "MARKET", opt['action'], 1, 0.0, "PENDING"))
        conn.commit()
        conn.close()
        print(f"Wrote {len(options)} options orders to the database.")
    except Exception as e:
        print(f"Database error: {e}")

def main():
    print(f"[{datetime.datetime.now()}] Options Manager running...")
    sentiment = fetch_market_sentiment()
    
    if sentiment == "Neutral":
        print("Market is neutral, skipping options trades.")
        return
        
    options = scan_options_chain(underlying="SPY", sentiment=sentiment)
    write_orders_to_book(options)

if __name__ == "__main__":
    main()
