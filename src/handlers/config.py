import logging
from aiogram import types, F
from src.database import db

logger = logging.getLogger(__name__)

async def download_config(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    if not db.has_user_checked_channel(user_id):
        await callback.message.edit_text("❌ Сначала подпишитесь на канал!", reply_markup=db.subscription_check_keyboard())
        return
    
    vmess_uuid = db.get_user_vmess_uuid(user_id)
    server = db.get_active_server()
    
    if not server:
        await callback.message.edit_text("❌ Сервер временно недоступен")
        return
    
    server_ip = server[1]
    
    import json
    import base64
    
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
        "path": "/vmess",
        "tls": "tls"
    }
    
    vmess_url = "vmess://" + base64.b64encode(json.dumps(vmess_config).encode()).decode()
    
    config_text = f"""
🌐 Ваш VPN конфиг

📡 Сервер: {server_ip}
🔑 UUID: {vmess_uuid}

📥 VMess конфигурация:
{vmess_url}

📖 Инструкция:
1. Скопируйте конфигурацию
2. Вставьте в VPN приложение
3. Подключитесь к серверу
    """
    
    await callback.message.edit_text(config_text, parse_mode='HTML')