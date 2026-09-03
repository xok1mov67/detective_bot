import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "7638494951:AAHIB_5bVJp0MqCw9FmX2yZ1kLmN3oPqR"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🕵️ Detektiv Bot ishga tushdi!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
