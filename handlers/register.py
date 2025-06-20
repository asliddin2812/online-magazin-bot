from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import db
from project.keyboard import request_keyboard, request_location
from project.states import RegisterStates

reg_router = Router()

def get_categories_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yangi kategoriya qo'shish", callback_data="add_category")],
        [InlineKeyboardButton(text="📋 Kategoriyalarni ko'rish", callback_data="list_categories")],
        [InlineKeyboardButton(text="🗑 Kategoriyani o'chirish", callback_data="delete_category")],
        [InlineKeyboardButton(text="⬅️ Asosiy menyuga", callback_data="back_to_main")]
    ])

@reg_router.message(RegisterStates.first_name)
async def register_first_handler(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text.strip())
    await state.set_state(RegisterStates.last_name)
    await message.answer("Iltimos Familiyangizni kiriting....")

@reg_router.message(RegisterStates.last_name)
async def register_last_handler(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text.strip())
    await state.set_state(RegisterStates.phone)
    await message.answer("Iltimos Telefon raqamingizni yuboring....", reply_markup=request_keyboard)

@reg_router.message(RegisterStates.phone, F.contact)
async def register_contact_handler(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(RegisterStates.address)
    await message.answer("Iltimos location yuboring yoki manzil kiriting....", reply_markup=request_location)

@reg_router.message(RegisterStates.phone)
async def register_contact_error(message: Message, state: FSMContext):
    await message.reply(
        "Iltimos telefon raqamingizni yuboring....",
        reply_markup=request_keyboard,
    )

@reg_router.message(RegisterStates.address, F.location)
async def register_address_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    location = f"{message.location.latitude},{message.location.longitude}" if message.location else message.text.strip()
    db.update_any_col('location' if message.location else 'address', location, message.from_user.id)
    db.set_registered(message.from_user.id)
    await message.answer("✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!", reply_markup=get_categories_menu())
    await state.clear()

@reg_router.message(RegisterStates.address)
async def register_address_error(message: Message, state: FSMContext):
    await message.reply(
        "Iltimos location yuboring yoki manzil kiriting....",
        reply_markup=request_location,
    )