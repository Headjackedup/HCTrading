#!/bin/bash
echo "Verifying environment dependencies..."

# Ensure we're in the right directory
cd /opt/HCTrading || echo "Warning: Not in /opt/HCTrading"

# Check for required python packages safely
echo "Checking Python dependencies..."
python3 -c "import telegram" 2>/dev/null || pip3 install python-telegram-bot
python3 -c "import numpy" 2>/dev/null || pip3 install numpy
python3 -c "import pandas" 2>/dev/null || pip3 install pandas
python3 -c "import websockets" 2>/dev/null || pip3 install websockets
python3 -c "import alpaca_trade_api" 2>/dev/null || pip3 install alpaca-trade-api
python3 -c "import coinbase" 2>/dev/null || pip3 install coinbase-advanced-py

echo "Initializing Database..."
python3 database_setup.py

echo "Setting up systemd services..."
if [ -f "crypto_manager.service" ]; then
    sudo cp crypto_manager.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable crypto_manager.service
    sudo systemctl restart crypto_manager.service
else
    echo "Warning: crypto_manager.service not found."
fi

echo "Setting up Cron Jobs..."
if [ -f "scan_bot.cron" ]; then
    crontab scan_bot.cron
else
    echo "Warning: scan_bot.cron not found."
fi

echo "Setup Complete!"
