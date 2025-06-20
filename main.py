import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from handlers.general import gen_router
from handlers.register import reg_router
from handlers.shop import shop_router
from project.custom_command import custom_command

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode="HTML",
        )
    )
    await bot.set_my_commands(custom_command)
    dp = Dispatcher()
    dp.include_routers(
        reg_router,
        gen_router,
        shop_router,
    )
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())