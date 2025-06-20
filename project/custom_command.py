from aiogram.types import BotCommand

custom_command = (
    BotCommand(
    command = "start",
    description="Botni qayta ishga tushirish!",
),
    BotCommand(
        command="register",
        description="Botdan ro'yxatdan o'tish!",
    ),
    BotCommand(
        command="help",
        description="Botdan foydalanish qo'llanmasi"
    )
)