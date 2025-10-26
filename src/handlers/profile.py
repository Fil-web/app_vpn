import logging
from aiogram import types, F
from src.database import db

logger = logging.getLogger(__name__)

async def show_profile(callback: types.CallbackQuery):
    if not db.has_user_checked_channel(callback.from_user.id):
        await callback.message.edit_text("❌ Сначала подпишитесь на канал!", reply_markup=db.subscription_check_keyboard())
        return
    
    user_id = callback.from_user.id
    user, subscription = db.get_user_profile(user_id)
    
    if not user:
        await callback.message.edit_text("❌ Профиль не найден")
        return
    
    sub_status = db.get_subscription_status(user_id)
    vpn_status = "✅ Активен" if db.is_config_active(user_id) else "❌ Не активен"
    
    profile_text = f"""
👤 Ваш профиль

🆔 ID: {user_id}
👤 Имя: {user[2]}
📅 Регистрация: {user[3].split()[0] if user[3] else 'Неизвестно'}
📊 Подписка: {sub_status}
🔧 Конфиг: {vpn_status}
    """
    
    await callback.message.edit_text(profile_text, reply_markup=db.profile_menu(), parse_mode='HTML')