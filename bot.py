import os
import json
import random
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    TOKEN = 8545471952:AAH1tCgLuffjh-ltmdPsmu8mqX7r-kXMAno
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

with open("cases.json", "r", encoding="utf-8") as f:
    CASES = json.load(f)

class GameStates(StatesGroup):
    playing = State()

user_data = {}

def get_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🕵️ Yangi ish")],
            [KeyboardButton(text="🏆 Mening ballarim")],
            [KeyboardButton(text="📖 Yordam")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        user_data[user_id] = {
            "score": 0,
            "money": 0,
            "solved": 0,
            "used_cases": []
        }
    
    await message.answer(
        "🕵️ *Detektiv Botga xush kelibsiz!*\n\n"
        "35 ta jinoyat ishini oching!\n"
        "💰 Har bir ish uchun 10 ball\n"
        "🎯 15 va 20-ishda 1000$ bonus!",
        parse_mode="Markdown",
        reply_markup=get_keyboard()
    )

@dp.message(F.text == "🕵️ Yangi ish")
async def new_case(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user = user_data[user_id]
    
    available = [c for c in CASES if c["id"] not in user["used_cases"]]
    if not available:
        await message.answer("🎉 Barcha ishlarni ochdingiz!")
        return
    
    case = random.choice(available)
    user["used_cases"].append(case["id"])
    user["current_case"] = case["id"]
    await state.update_data(case_id=case["id"])
    await state.set_state(GameStates.playing)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Jinoyat haqida", callback_data="read_story")],
            [InlineKeyboardButton(text="🔍 Dalillar", callback_data="show_clues")],
            [InlineKeyboardButton(text="👤 Gumonlanuvchilar", callback_data="show_suspects")],
            [InlineKeyboardButton(text="⚖️ Javob berish", callback_data="give_answer")]
        ]
    )
    
    await message.answer(
        f"🕵️ *Yangi ish #{case['id']}*\n\nTergovni boshlang!",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "read_story")
async def read_story(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    case = next(c for c in CASES if c["id"] == data["case_id"])
    await callback.message.edit_text(
        f"📖 *{case['title']}*\n\n{case['story']}",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "show_clues")
async def show_clues(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    case = next(c for c in CASES if c["id"] == data["case_id"])
    text = "🔍 *Dalillar:*\n\n" + "\n".join(f"• {c}" for c in case["clues"])
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "show_suspects")
async def show_suspects(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    case = next(c for c in CASES if c["id"] == data["case_id"])
    buttons = [[InlineKeyboardButton(text=s, callback_data=f"suspect_{s}")] for s in case["suspects"]]
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")])
    await callback.message.edit_text(
        "👤 *Gumonlanuvchilar:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("suspect_"))
async def interrogate(callback: types.CallbackQuery):
    name = callback.data.replace("suspect_", "")
    await callback.message.edit_text(
        f"💬 *So'roq: {name}*\n\n\"Men hech narsa bilmayman!\"",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "give_answer")
async def give_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    case = next(c for c in CASES if c["id"] == data["case_id"])
    buttons = [[InlineKeyboardButton(text=s, callback_data=f"ans_{s}")] for s in case["suspects"]]
    await callback.message.edit_text(
        "⚖️ *Kim jinoyatchi?*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("ans_"))
async def check_answer(callback: types.CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    answer = callback.data.replace("ans_", "")
    data = await state.get_data()
    case = next(c for c in CASES if c["id"] == data["case_id"])
    
    if answer == case["correct"]:
        user_data[user_id]["score"] += 10
        user_data[user_id]["solved"] += 1
        solved = user_data[user_id]["solved"]
        bonus = ""
        if solved == 15 or solved == 20:
            user_data[user_id]["money"] += 1000
            bonus = f"\n💰 1000$ bonus! ({solved}-ish)"
        
        await callback.message.edit_text(
            f"🎉 *TO'G'RI!*\n\n✅ Jinoyatchi: {case['correct']}\n⭐ +10 ball\n📊 Ball: {user_data[user_id]['score']}\n🔓 Ochilgan: {solved}/{len(CASES)}\n💰 Pul: {user_data[user_id]['money']}$\n{bonus}",
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            f"❌ *NOTO'G'RI!*\n\n💡 Maslahat: {case['hint']}",
            parse_mode="Markdown"
        )
    
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    case = next(c for c in CASES if c["id"] == data["case_id"])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Jinoyat haqida", callback_data="read_story")],
            [InlineKeyboardButton(text="🔍 Dalillar", callback_data="show_clues")],
            [InlineKeyboardButton(text="👤 Gumonlanuvchilar", callback_data="show_suspects")],
            [InlineKeyboardButton(text="⚖️ Javob berish", callback_data="give_answer")]
        ]
    )
    await callback.message.edit_text(
        f"🕵️ *Ish #{case['id']}* - Tergovni davom ettiring",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.message(F.text == "🏆 Mening ballarim")
async def show_stats(message: types.Message):
    user_id = str(message.from_user.id)
    user = user_data.get(user_id, {"score": 0, "money": 0, "solved": 0})
    await message.answer(
        f"🏆 *Statistika:*\n\n⭐ Ball: {user['score']}\n🔓 Ochilgan: {user['solved']}/{len(CASES)}\n💰 Pul: {user['money']}$",
        parse_mode="Markdown"
    )

@dp.message(F.text == "📖 Yordam")
async def help_cmd(message: types.Message):
    await message.answer(
        "🕵️ *Detektiv Bot*\n\n1. 'Yangi ish' - yangi jinoyat\n2. Dalillar va gumonlanuvchilarni tekshiring\n3. Javob bering\n\n💰 Har bir ish 10 ball\n🎯 15 va 20-ishda 1000$ bonus",
        parse_mode="Markdown"
    )

async def main():
    print("🕵️ Detektiv Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
