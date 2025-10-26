from aiogram import types, F, Router
from aiogram.filters import Command
from src.database import db

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Регистрируем пользователя
    db.register_user(user_id, username, first_name)
    
    # Проверяем подписку на канал
    if not db.has_user_checked_channel(user_id):
        subscription_text = f"""
👋 Добро пожаловать, {first_name}!

📢 <b>Для использования бота необходимо подписаться на наш канал:</b>

{db.CHANNEL_USERNAME}

После подписки нажмите кнопку "✅ Я подписался"
        """
        
        await message.answer(subscription_text, reply_markup=db.subscription_check_keyboard(), parse_mode='HTML')
        return
    
    # Если подписка проверена, показываем главное меню
    await show_main_menu(message, first_name)

async def show_main_menu(message: types.Message, first_name: str = None):
    if first_name is None:
        first_name = message.from_user.first_name
    
    welcome_text = f"""
👋 Добро пожаловать, {first_name}!

🚀 <b>Bunker VPN</b> - надежный и быстрый VPN сервис

📲 <b>Возможности:</b>
• 🔒 Безопасное соединение
• 🌐 Доступ к заблокированным сайтам
• 🚀 Высокая скорость
• 📱 Поддержка всех устройств
• 🔄 Неограниченный трафик

Выберите действие из меню ниже:
    """
    
    await message.answer(welcome_text, reply_markup=db.main_menu(), parse_mode='HTML')