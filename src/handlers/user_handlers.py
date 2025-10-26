import logging
from aiogram import types, F
from aiogram.filters import Command
from src.database import db

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    db.register_user(user_id, username, first_name)
    
    if not db.has_user_checked_channel(user_id):
        subscription_text = f"""
👋 Добро пожаловать, {first_name}!

📢 Для использования бота необходимо подписаться на наш канал:

{db.CHANNEL_USERNAME}

После подписки нажмите кнопку "✅ Я подписался"
        """
        await message.answer(subscription_text, reply_markup=db.subscription_check_keyboard(), parse_mode='HTML')
        return
    
    await show_main_menu(message, first_name)

async def show_main_menu(message: types.Message, first_name: str = None):
    if first_name is None:
        first_name = message.from_user.first_name
    
    welcome_text = f"""
👋 Добро пожаловать, {first_name}!

🚀 Bunker VPN - надежный и быстрый VPN сервис

📲 Возможности:
• 🔒 Безопасное соединение
• 🌐 Доступ к заблокированным сайтам
• 🚀 Высокая скорость
• 📱 Поддержка всех устройств

Выберите действие из меню ниже:
    """
    await message.answer(welcome_text, reply_markup=db.main_menu(), parse_mode='HTML')

async def cmd_help(message: types.Message):
    if not db.has_user_checked_channel(message.from_user.id):
        await message.answer("❌ Сначала подпишитесь на канал!", reply_markup=db.subscription_check_keyboard())
        return
    
    help_text = """
🛠️ Помощь по использованию Bunker VPN

📱 Установка приложения:
1. Выберите вашу платформу в меню "Приложения"
2. Скачайте и установите приложение
3. Загрузите конфигурационный файл

🔧 Настройка подключения:
1. Скачайте конфиг в меню "Скачать конфиг"
2. Импортируйте его в приложение
3. Подключитесь к серверу
    """
    await message.answer(help_text, reply_markup=db.help_menu(), parse_mode='HTML')

async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    try:
        from aiogram import Bot
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        bot = Bot(token=os.getenv('BOT_TOKEN'))
        
        chat_member = await bot.get_chat_member(chat_id=db.CHANNEL_USERNAME, user_id=user_id)
        is_subscribed = chat_member.status in ['member', 'administrator', 'creator']
        
        if is_subscribed:
            db.mark_channel_checked(user_id)
            await callback.message.edit_text("✅ Отлично! Теперь вы можете пользоваться ботом.", parse_mode='HTML')
            await show_main_menu(callback.message, callback.from_user.first_name)
        else:
            await callback.message.edit_text("❌ Вы не подписались на канал!", reply_markup=db.subscription_check_keyboard())
            
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        await callback.message.edit_text("❌ Ошибка проверки подписки!")

async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=db.main_menu())

async def back_to_plans(callback: types.CallbackQuery):
    await show_plans(callback)

async def show_plans(callback: types.CallbackQuery):
    if not db.has_user_checked_channel(callback.from_user.id):
        await callback.message.edit_text("❌ Сначала подпишитесь на канал!", reply_markup=db.subscription_check_keyboard())
        return
    
    plans_text = """
💳 Выберите тарифный план:

🔥 1 месяц - 299₽
• Все функции включены

💥 3 месяца - 799₽
• Экономия 98₽

🚀 6 месяцев - 1399₽  
• Экономия 395₽

⚡ 12 месяцев - 2399₽
• Максимальная экономия
    """
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔥 1 месяц - 299₽", callback_data="plan_1month"))
    keyboard.add(InlineKeyboardButton(text="💥 3 месяца - 799₽", callback_data="plan_3months"))
    keyboard.add(InlineKeyboardButton(text="🚀 6 месяцев - 1399₽", callback_data="plan_6months"))
    keyboard.add(InlineKeyboardButton(text="⚡ 12 месяцев - 2399₽", callback_data="plan_12months"))
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    keyboard.adjust(1)
    
    await callback.message.edit_text(plans_text, reply_markup=keyboard.as_markup(), parse_mode='HTML')

async def show_apps(callback: types.CallbackQuery):
    if not db.has_user_checked_channel(callback.from_user.id):
        await callback.message.edit_text("❌ Сначала подпишитесь на канал!", reply_markup=db.subscription_check_keyboard())
        return
    
    apps_text = "📱 Приложения для всех платформ:"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📱 Android", callback_data="app_android"))
    keyboard.add(InlineKeyboardButton(text="🍎 iOS", callback_data="app_ios"))
    keyboard.add(InlineKeyboardButton(text="💻 Windows", callback_data="app_windows"))
    keyboard.add(InlineKeyboardButton(text="🖥️ macOS", callback_data="app_macos"))
    keyboard.add(InlineKeyboardButton(text="🐧 Linux", callback_data="app_linux"))
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    keyboard.adjust(2)
    
    await callback.message.edit_text(apps_text, reply_markup=keyboard.as_markup(), parse_mode='HTML')

async def show_help(callback: types.CallbackQuery):
    if not db.has_user_checked_channel(callback.from_user.id):
        await callback.message.edit_text("❌ Сначала подпишитесь на канал!", reply_markup=db.subscription_check_keyboard())
        return
    
    help_text = "🛠️ Помощь - используйте /help для подробной информации"
    await callback.message.edit_text(help_text, reply_markup=db.help_menu(), parse_mode='HTML')

async def show_support(callback: types.CallbackQuery):
    if not db.has_user_checked_channel(callback.from_user.id):
        await callback.message.edit_text("❌ Сначала подпишитесь на канал!", reply_markup=db.subscription_check_keyboard())
        return
    
    support_text = """
📞 Техническая поддержка

👨‍💻 Техподдержка: @bunker_support
📧 Email: support@bunker-vpn.ru

⏰ Время работы: круглосуточно
    """
    await callback.message.edit_text(support_text, parse_mode='HTML')

async def download_app(callback: types.CallbackQuery):
    if not db.has_user_checked_channel(callback.from_user.id):
        await callback.message.edit_text("❌ Сначала подпишитесь на канал!", reply_markup=db.subscription_check_keyboard())
        return
    
    app_data = callback.data.split("_")[1]
    
    apps = {
        "android": {"name": "Android", "url": "https://play.google.com/store/apps/details?id=com.bunkervpn"},
        "ios": {"name": "iOS", "url": "https://apps.apple.com/app/bunker-vpn/id123456789"},
        "windows": {"name": "Windows", "url": "https://bunker-vpn.ru/download/windows"},
        "macos": {"name": "macOS", "url": "https://bunker-vpn.ru/download/macos"},
        "linux": {"name": "Linux", "url": "https://bunker-vpn.ru/download/linux"}
    }
    
    app = apps.get(app_data)
    if app:
        app_text = f"📱 Скачать для {app['name']}:\n{app['url']}"
        await callback.message.edit_text(app_text, parse_mode='HTML')