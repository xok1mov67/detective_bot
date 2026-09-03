import asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "7638494951:AAHIB_5bVJp0MqCw9FmX2yZ1kLmN3oPqR"

# 35 ta jinoyat ishi
CASES = [
    {"id": 1, "title": "🏚️ Qora Ko‘l Qasri", "story": "Tog‘li qarorgohda qotillik...", "suspects": ["Bekzod", "Elena", "Otabek"], "clues": ["Issiq choy", "Kamin yonida suv"], "correct": "Bekzod", "hint": "Yomg‘ir va choyga e'tibor"},
    # Qolgan 34 ta ish qo'shiladi
]

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🕵️ Yangi ish"], ["🏆 Ballarim"], ["📖 Yordam"]]
    await update.message.reply_text(
        "🕵️ DETEKTIV BOT\n\n35 ta jinoyat ishini oching!",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def new_case(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_data:
        user_data[user_id] = {"score": 0, "solved": 0, "used": []}
    
    available = [c for c in CASES if c["id"] not in user_data[user_id]["used"]]
    if not available:
        await update.message.reply_text("🎉 Barcha ishlar ochildi!")
        return
    
    case = CASES[len(user_data[user_id]["used"])]
    user_data[user_id]["used"].append(case["id"])
    context.user_data["case"] = case["id"]
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 O'qish", callback_data="read")],
        [InlineKeyboardButton("🔍 Dalillar", callback_data="clues")],
        [InlineKeyboardButton("👤 Gumonlanuvchilar", callback_data="suspects")],
        [InlineKeyboardButton("⚖️ Javob", callback_data="answer")]
    ])
    await update.message.reply_text(f"🕵️ Ish #{case['id']}", reply_markup=keyboard)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    case_id = context.user_data.get("case")
    case = next(c for c in CASES if c["id"] == case_id)
    
    if q.data == "read":
        await q.edit_message_text(f"📖 {case['title']}\n\n{case['story']}")
    elif q.data == "clues":
        await q.edit_message_text("🔍 Dalillar:\n• " + "\n• ".join(case["clues"]))
    elif q.data == "suspects":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(s, callback_data=f"ask_{s}")] for s in case["suspects"]] + [[InlineKeyboardButton("🔙 Orqaga", callback_data="back")]])
        await q.edit_message_text("👤 Gumonlanuvchilar:", reply_markup=keyboard)
    elif q.data.startswith("ask_"):
        name = q.data.replace("ask_", "")
        await q.edit_message_text(f"💬 {name}: \"Men bilmayman!\"")
    elif q.data == "answer":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(s, callback_data=f"ans_{s}")] for s in case["suspects"]])
        await q.edit_message_text("⚖️ Kim jinoyatchi?", reply_markup=keyboard)
    elif q.data.startswith("ans_"):
        answer = q.data.replace("ans_", "")
        if answer == case["correct"]:
            user_data[str(q.from_user.id)]["score"] += 10
            user_data[str(q.from_user.id)]["solved"] += 1
            await q.edit_message_text(f"🎉 TO'G'RI! +10 ball")
        else:
            await q.edit_message_text(f"❌ Noto'g'ri!\n💡 {case['hint']}")
    elif q.data == "back":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 O'qish", callback_data="read")],
            [InlineKeyboardButton("🔍 Dalillar", callback_data="clues")],
            [InlineKeyboardButton("👤 Gumonlanuvchilar", callback_data="suspects")],
            [InlineKeyboardButton("⚖️ Javob", callback_data="answer")]
        ])
        await q.edit_message_text(f"🕵️ Ish #{case['id']}", reply_markup=keyboard)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user = user_data.get(user_id, {"score": 0, "solved": 0})
    await update.message.reply_text(f"🏆 Ball: {user['score']}\n🔓 Ochilgan: {user['solved']}/{len(CASES)}")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🕵️ Detektiv Bot\n\n'Yangi ish' - boshlang\nDalil va gumonlanuvchilarni tekshiring\nJavob bering!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Text("🕵️ Yangi ish"), new_case))
    app.add_handler(MessageHandler(filters.Text("🏆 Ballarim"), stats))
    app.add_handler(MessageHandler(filters.Text("📖 Yordam"), help_cmd))
    app.add_handler(CallbackQueryHandler(button))
    print("✅ Bot ishlayapti!")
    app.run_polling()

if __name__ == "__main__":
    main()
