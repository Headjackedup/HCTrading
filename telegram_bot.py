import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

DB_NAME = os.path.join(os.path.dirname(__file__), 'trading_system.db')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT market_sentiment, hard_halt FROM system_state ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            sentiment, halt = row
            halt_status = "ACTIVE" if halt else "NORMAL"
            msg = f"📊 *System Status*\nSentiment: {sentiment}\nHalt Status: {halt_status}"
        else:
            msg = "System state not initialized."
    except Exception as e:
        msg = f"Error reading state: {e}"
        
    await update.message.reply_text(msg, parse_mode='Markdown')

async def halt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE system_state SET hard_halt = 1 WHERE id = (SELECT id FROM system_state ORDER BY id DESC LIMIT 1)")
        conn.commit()
        conn.close()
        await update.message.reply_text("🚨 *Manual Halt Triggered!*", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE system_state SET hard_halt = 0, consecutive_stop_losses = 0 WHERE id = (SELECT id FROM system_state ORDER BY id DESC LIMIT 1)")
        conn.commit()
        conn.close()
        await update.message.reply_text("✅ *System Resumed.*", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    print("Starting Telegram Bot Listener...")
    if TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN':
        print("Warning: TELEGRAM_BOT_TOKEN not set. Exiting.")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("halt", halt))
    app.add_handler(CommandHandler("resume", resume))

    print("Polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
