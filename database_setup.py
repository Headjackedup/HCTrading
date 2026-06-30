import sqlite3
import os

DB_NAME = 'trading_system.db'

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. system_state: Stores current sentiment, global HARD_HALT flags, and system metrics.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            market_sentiment TEXT,
            hard_halt BOOLEAN DEFAULT 0,
            consecutive_stop_losses INTEGER DEFAULT 0
        )
    ''')

    # 2. strategy_metrics: Tracks win probabilities (p) and risk-reward ratios (R) for the Kelly Criterion formula.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strategy_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_symbol TEXT UNIQUE,
            win_probability REAL DEFAULT 0.5,
            risk_reward_ratio REAL DEFAULT 1.0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. order_book: Live queue for execution tracking.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_book (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            asset_symbol TEXT,
            order_type TEXT,
            side TEXT,
            quantity REAL,
            price REAL,
            status TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Initialize a default system state if empty
    cursor.execute('SELECT COUNT(*) FROM system_state')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO system_state (market_sentiment, hard_halt) VALUES ('Neutral', 0)")

    conn.commit()
    conn.close()
    print(f"Database {DB_NAME} initialized successfully.")

if __name__ == "__main__":
    create_database()
