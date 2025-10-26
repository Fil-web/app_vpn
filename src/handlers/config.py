import logging
from aiogram import types, F, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.database import db

logger = logging.getLogger(__name__)

# Создаем роутер
router = Router()

def config_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    return keyboard.as_markup()

@router.callback_query(F.data == "download")
async def download_config(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    # Проверяем подписку
    if not db.has_user_checked_channel(user_id):
        await callback.message.edit_text("❌ Сначала подпишитесь на канал!", reply_markup=db.subscription_check_keyboard())
        return
    
    # Получаем UUID пользователя
    vmess_uuid = db.get_user_vmess_uuid(user_id)
    server = db.get_active_server()
    
    if not server:
        await callback.message.edit_text("❌ Сервер временно недоступен", reply_markup=config_menu())
        return
    
    server_ip = server[1]  # server_ip находится во второй колонке
    
    # Создаем VMess конфиг
    vmess_config = {
        "v": "2",
        "ps": "Bunker VPN",
        "add": server_ip,
        "port": "443",
        "id": vmess_uuid,
        "aid": "0",
        "scy": "auto",
        "net": "ws",
        "type": "none",
        "host": "",
        "path": "/vmess",
        "tls": "tls",
        "sni": ""
    }
    
    import json
    import base64
    
    # Кодируем конфиг в base64
    vmess_url = "vmess://" + base64.b64encode(json.dumps(vmess_config).encode()).decode()
    
    config_text = f"""
🌐 <b>Ваш VPN конфиг</b>

📡 <b>Сервер:</b> {server_ip}
🔑 <b>UUID:</b> <code>{vmess_uuid}</code>

📥 <b>VMess конфигурация:</b>
<code>{vmess_url}</code>

📖 <b>Инструкция по использованию:</b>
1. Скопируйте конфигурацию выше
2. Вставьте в ваше VPN приложение
3. Подключитесь к серверу

⚠️ <b>Внимание:</b> Не передавайте ваш конфиг третьим лицам!
    """
    
    await callback.message.edit_text(config_text, reply_markup=config_menu(), parse_mode='HTML')