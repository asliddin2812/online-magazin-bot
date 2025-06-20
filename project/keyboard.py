from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

request_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Telefon raqamini yuborish!', request_contact=True)],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
request_location = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Location yuborish!', request_location=True)],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)