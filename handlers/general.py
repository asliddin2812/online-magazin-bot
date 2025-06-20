from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import db
from project.states import RegisterStates

gen_router = Router()

def get_categories_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yangi kategoriya qo'shish", callback_data="add_category")],
        [InlineKeyboardButton(text="📋 Kategoriyalarni ko'rish", callback_data="list_categories")],
        [InlineKeyboardButton(text="🗑 Kategoriyani o'chirish", callback_data="delete_category")],
        [InlineKeyboardButton(text="⬅️ Asosiy menyuga", callback_data="back_to_main")]
    ])

@gen_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    if db.has_user(message.from_user.id):
        if db.is_registered(message.from_user.id):
            await message.answer("Qaytganingizdan hursandmiz! Kategoriyalar bilan ishlash:", reply_markup=get_categories_menu())
        else:
            await state.clear()
            await state.set_state(RegisterStates.first_name)
            await message.reply("Xush kelibsiz! Ro'yxatdan o'ting!\nIltimos ismingizni kiriting ....")
    else:
        try:
            db.add_user(dict(message.from_user))
        except Exception as e:
            print(e)
        await state.clear()
        await state.set_state(RegisterStates.first_name)
        await message.reply("Xush kelibsiz! Ro'yxatdan o'ting!\nIltimos ismingizni kiriting ....")

@gen_router.message(Command("register"))
async def register_command(message: Message, state: FSMContext):
    if db.is_registered(message.from_user.id):
        await message.answer("Siz avval ham ro'yxatdan o'tgansiz!", reply_markup=get_categories_menu())
    else:
        await state.clear()
        await state.set_state(RegisterStates.first_name)
        await message.reply("Ro'yxatdan o'ting!\nIltimos ismingizni kiriting ....")

@gen_router.message(Command("help"))
async def help_command(message: Message, state: FSMContext):
    await message.answer("""📝 <b>Ro'yxatdan o'tish bo'yicha yo'riqnoma:</b>

        1️⃣ Botdan foydalanish uchun avval ro'yxatdan o'tishingiz kerak.
        
        2️⃣ /start buyrug'ini yuboring.
        
        3️⃣ Bot sizdan quyidagi ma'lumotlarni so'raydi:
        
        👤 Ismingiz
        
        👥 Familiyangiz
        
        📞 Telefon raqamingiz (kontakt sifatida yuborishingiz mumkin)
        
        📍 Yashash manzilingiz
        
        4️⃣ Barcha ma'lumotlarni to'liq va to'g'ri kiriting.
        
        ✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlangach, botning barcha funksiyalaridan foydalanishingiz mumkin bo'ladi.
        
        ℹ️ Agar xatolik yuz bersa yoki qayta ro'yxatdan o'tmoqchi bo'lsangiz, /start buyrug'ini qaytadan yuboring.
        
        """)