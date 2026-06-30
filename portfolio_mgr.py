import sqlite3
import numpy as np
import os
import time

DB_NAME = os.path.join(os.path.dirname(__file__), 'trading_system.db')
KELLY_FRACTION = 0.5  # Half-Kelly for risk aversion

def fetch_strategy_metrics():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT asset_symbol, win_probability, risk_reward_ratio FROM strategy_metrics")
    data = cursor.fetchall()
    conn.close()
    return data

def calculate_kelly_allocation(win_probability, risk_reward_ratio):
    """
    Kelly Formula: K = W - ((1 - W) / R)
    W = Win probability
    R = Risk:Reward ratio (e.g. 2 means we make $2 for every $1 risked)
    """
    if risk_reward_ratio <= 0:
        return 0.0
    
    k = win_probability - ((1.0 - win_probability) / risk_reward_ratio)
    k = max(0.0, k) # No negative allocations
    return k * KELLY_FRACTION

def rebalance_portfolio():
    metrics = fetch_strategy_metrics()
    allocations = {}
    
    for asset, win_prob, rr_ratio in metrics:
        allocation = calculate_kelly_allocation(win_prob, rr_ratio)
        allocations[asset] = allocation
        print(f"Asset: {asset} | Win Prob: {win_prob:.2f} | R:R: {rr_ratio:.2f} | Target Allocation: {allocation*100:.2f}%")
        
    return allocations

def run_portfolio_manager():
    print("Starting Portfolio Manager logic core...")
    while True:
        # Rebalance every hour, or triggered via IPC/Database
        allocations = rebalance_portfolio()
        
        # Here, the allocations would be written to the database for execution_bot to action
        # For now, just sleep
        time.sleep(3600)

if __name__ == "__main__":
    run_portfolio_manager()
