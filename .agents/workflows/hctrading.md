---
description: Build a quant building firm using bots
---

System Architecture Blueprint: Automated Multi-Bot Trading SystemRole & Core ConstraintYou are an expert Quant Developer and Devops Engineer. Your task is to generate clean, optimized Python 3 code and system configurations for an aggressive multi-agent trading system.CRITICAL DEPLOYMENT CONSTRAINT: The target environment is an existing, active DigitalOcean Ubuntu Droplet with Python, Git, and various development tools already installed. You must write all bash deployment scripts to check if a package, tool, or library exists BEFORE attempting to install it. Do not overwrite existing dependencies.1. Telegram & Webhook Notification IntegrationThe system uses Telegram for execution logging, configuration commands, and the mandatory morning notification.Morning Scan Alert: Every day at 10:00 AM EST, the system must push a concise markdown summary to Telegram containing: Market Sentiment (Bullish/Bearish/Neutral), Sector Momentum, and the generated Options/Stock watch list.Execution Alert: Immediate real-time alerts for any filled order, stop-loss adjustment, or machine learning model change.Telegram Command Listener: Create an asynchronous polling loop (python-telegram-bot or raw requests) that allows the user to send manual commands to the bot (e.g., /status, /halt, /positionsize).2. Multi-Agent Modular Script FrameworkGenerate 5 distinct Python modules that communicate locally via an internal, thread-safe SQLite database (trading_system.db). This avoids resource bloat and keeps operating costs under $1.00/day.       [ 10:00 AM Cron ] ──> [ scan_bot.py ] ──> (Telegram Alert)
                                    │
                                    ▼
[ 24/7 WebSockets ] ──> [ crypto_manager.py ] <── [ portfolio_mgr.py ]
                                    │                     │
                                    ▼                     ▼
                        [ execution_bot.py ] <─── [ options_mgr.py ]
                                    │
                                    ▼
                        [ Alpaca / Coinbase API ]
scan_bot.py (10:00 AM Cron): Computes RSI, ATR, and short-term trends. Writes market_sentiment to the database and pings Telegram.portfolio_mgr.py (Logic Core): Computes asset allocations using the Fractional Kelly Criterion formula. Uses pure math arrays (numpy) to prevent RAM spikes.options_mgr.py (Equity/Options): Targets aggressive short-dated contracts (0DTE to 7DTE) on Charles Schwab / Public.com using high-gamma filters.crypto_manager.py (24/7 Live Stream): Uses asynchronous WebSockets connected to Alpaca and Coinbase Advanced Trade to scan for high-momentum breakouts outside standard market hours.execution_bot.py (Routing Engine): Manages OAuth2 token refreshes, rate limits, and live order placement.3. SQLite Database SchemaGenerate an optimized SQLite schema to track state locally without relying on external databases.system_state: Stores current sentiment, global HARD_HALT flags, and system metrics.strategy_metrics: Tracks win probabilities (p) and risk-reward ratios (R) for the Kelly Criterion formula.order_book: Live queue for execution tracking.4. Machine Learning Loop & GuardrailsLightweight Q-Learning: Write a lightweight learning script using raw arrays. It must ingest completed trade features [Sentiment, Delta, Asset, Entry_RSI] from the database and adjust the strategy's expected win probability (p) based on trade success or failure.Risk Circuit Breaker: Implement a hard rule: If the system registers 3 consecutive maximum stop-loss hits within a rolling 24-hour window, set HARD_HALT = True, cancel all open orders, and notify Telegram immediately.5. Idempotent Environment Setup ScriptProvide an setup script (setup.sh) that builds your execution ecosystem without duplicating or breaking existing tools. Wrap everything in conditional checks like the example below:bash#!/bin/bash
echo "Verifying environment dependencies..."

# Example of safe tool checking
if ! command -v cloudflared &> /dev/null; then
    echo "Cloudflared not found. Installing..."
    # [Insert Cloudflared installation code here]
else
    echo "Cloudflared is already installed. Skipping."
fi

# Check for required python packages safely
python3 -c "import telegram" 2>/dev/null || pip install python-telegram-bot
python3 -c "import numpy" 2>/dev/null || pip install numpy

# Output systemd files configuration for the modules...
Use code with caution.Generate the systemd service files (/etc/systemd/system/) for crypto_manager.py and the system dashboard to ensure they recover automatically if the Droplet reboots.To tailor the generated code exactly to your repository state, let me know:Do you want to use GitHub Actions to pull code updates automat