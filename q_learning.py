import sqlite3
import numpy as np
import os
import time

DB_NAME = os.path.join(os.path.dirname(__file__), 'trading_system.db')

# Q-Learning hyperparameters
ALPHA = 0.1  # Learning rate
GAMMA = 0.9  # Discount factor

def fetch_completed_trades():
    # In a real scenario, you'd fetch from an execution log or PnL database
    # For now, this is a placeholder
    return [
        {"asset": "SPY", "pnl": 50.0},
        {"asset": "QQQ", "pnl": -20.0}
    ]

def update_win_probability(asset, is_win):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT win_probability FROM strategy_metrics WHERE asset_symbol = ?", (asset,))
        row = cursor.fetchone()
        
        if row:
            current_p = row[0]
            # Simple Q-learning inspired update rule for probability
            reward = 1.0 if is_win else 0.0
            new_p = current_p + ALPHA * (reward - current_p)
            new_p = max(0.01, min(0.99, new_p)) # Keep bounded
            
            cursor.execute("UPDATE strategy_metrics SET win_probability = ?, last_updated = CURRENT_TIMESTAMP WHERE asset_symbol = ?", (new_p, asset))
        else:
            # Initialize if not exists
            initial_p = 0.5 + ALPHA * (1.0 if is_win else -0.1)
            cursor.execute("INSERT INTO strategy_metrics (asset_symbol, win_probability) VALUES (?, ?)", (asset, initial_p))
            
        conn.commit()
        conn.close()
        print(f"Updated Q-Learning prob for {asset}. Win={is_win}")
    except Exception as e:
        print(f"Database error in Q-Learning: {e}")

def run_q_learning():
    print("Starting Q-Learning Loop...")
    while True:
        trades = fetch_completed_trades()
        for trade in trades:
            is_win = trade['pnl'] > 0
            update_win_probability(trade['asset'], is_win)
            
        time.sleep(3600) # Run periodically

if __name__ == "__main__":
    run_q_learning()
