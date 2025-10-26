import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv
from src.database import db
from src.handlers import user_handlers, config, payment_handlers, profile

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("Токен бота не найден!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def register_handlers():
    dp.message.register(user_handlers.cmd_start, Command("start"))
    dp.message.register(user_handlers.cmd_help, Command("help"))
    
    dp.callback_query.register(user_handlers.check_subscription, F.data == "check_subscription")
    dp.callback_query.register(user_handlers.back_to_main, F.data == "back_main")
    dp.callback_query.register(user_handlers.show_plans, F.data == "plans")
    dp.callback_query.register(user_handlers.show_apps, F.data == "apps")
    dp.callback_query.register(user_handlers.show_help, F.data == "help")
    dp.callback_query.register(profile.show_profile, F.data == "profile")
    dp.callback_query.register(config.download_config, F.data == "download")
    dp.callback_query.register(user_handlers.show_support, F.data == "support")
    dp.callback_query.register(payment_handlers.select_plan, F.data.startswith("plan_"))
    dp.callback_query.register(payment_handlers.process_payment, F.data.startswith("pay_"))
    dp.callback_query.register(user_handlers.download_app, F.data.startswith("app_"))

async def main():
    db.init_db()
    register_handlers()
    logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())