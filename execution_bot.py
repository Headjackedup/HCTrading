import sqlite3
import time
import os
import requests

DB_NAME = os.path.join(os.path.dirname(__file__), 'trading_system.db')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID')

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

def check_hard_halt():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT hard_halt, consecutive_stop_losses FROM system_state ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return bool(row[0]), row[1]
    except Exception as e:
        print(f"Database error: {e}")
    return False, 0

def trigger_hard_halt():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE system_state SET hard_halt = 1 WHERE id = (SELECT id FROM system_state ORDER BY id DESC LIMIT 1)")
        
        # Cancel open orders
        cursor.execute("UPDATE order_book SET status = 'CANCELLED' WHERE status = 'PENDING'")
        conn.commit()
        conn.close()
        
        send_telegram_alert("🚨 *HARD HALT TRIGGERED* 🚨\n\n3 Consecutive stop-losses hit. System halted. All pending orders cancelled.")
        print("HARD HALT triggered!")
    except Exception as e:
        print(f"Database error during hard halt: {e}")

def execute_pending_orders():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, order_id, asset_symbol, side, quantity FROM order_book WHERE status = 'PENDING'")
        orders = cursor.fetchall()
        
        for order in orders:
            order_pk, order_id, symbol, side, qty = order
            
            # Placeholder for actual API call to Alpaca/Coinbase
            print(f"Executing order {order_id}: {side} {qty} {symbol}")
            
            # Mark as FILLED
            cursor.execute("UPDATE order_book SET status = 'FILLED', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (order_pk,))
            
            send_telegram_alert(f"✅ *Order Filled*\n`{order_id}`\n{side} {qty} {symbol}")
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error during execution: {e}")

def run_execution_bot():
    print("Starting Execution Bot...")
    while True:
        is_halted, stop_losses = check_hard_halt()
        
        if stop_losses >= 3 and not is_halted:
            trigger_hard_halt()
            is_halted = True
            
        if is_halted:
            # System is halted, don't execute orders
            time.sleep(10)
            continue
            
        execute_pending_orders()
        time.sleep(2) # Polling interval

if __name__ == "__main__":
    run_execution_bot()
