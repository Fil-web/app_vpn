import sqlite3
import logging
import uuid
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
CHANNEL_USERNAME = "@feel_and_trop"

def init_db():
    conn = sqlite3.connect('vpn_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            balance REAL DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            has_checked_channel BOOLEAN DEFAULT FALSE,
            vmess_uuid TEXT UNIQUE,
            config_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan_name TEXT,
            price REAL,
            duration_days INTEGER,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_ip TEXT,
            server_name TEXT,
            country TEXT,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Добавляем тестовый сервер
    cursor.execute('SELECT * FROM servers WHERE server_ip = ?', ('45.12.142.195',))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO servers (server_ip, server_name, country) VALUES (?, ?, ?)', 
                      ('45.12.142.195', 'Основной сервер', 'Россия'))
    
    conn.commit()
    conn.close()
    logger.info("База данных инициализирована")

def register_user(user_id, username, first_name):
    conn = sqlite3.connect('vpn_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    if not cursor.fetchone():
        vmess_uuid = str(uuid.uuid4())
        cursor.execute('INSERT INTO users (user_id, username, first_name, vmess_uuid) VALUES (?, ?, ?, ?)', 
                      (user_id, username, first_name, vmess_uuid))
    
    conn.commit()
    conn.close()

def mark_channel_checked(user_id: int):
    conn = sqlite3.connect('vpn_bot.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET has_checked_channel = TRUE WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def has_user_checked_channel(user_id: int) -> bool:
    conn = sqlite3.connect('vpn_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT has_checked_channel FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return bool(result[0]) if result else False

def get_user_vmess_uuid(user_id: int) -> str:
    conn = sqlite3.connect('vpn_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT vmess_uuid FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else str(uuid.uuid4())

def get_active_server():
    conn = sqlite3.connect('vpn_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM servers WHERE is_active = TRUE LIMIT 1')
    server = cursor.fetchone()
    conn.close()
    return server

def is_config_active(user_id: int) -> bool:
    conn = sqlite3.connect('vpn_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT config_active FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return bool(result[0]) if result else True

def get_user_subscription(user_id: int):
    conn = sqlite3.connect('vpn_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subscriptions WHERE user_id = ? AND is_active = TRUE ORDER BY end_date DESC LIMIT 1', (user_id,))
    subscription = cursor.fetchone()
    conn.close()
    return subscription

def get_subscription_status(user_id: int) -> str:
    subscription = get_user_subscription(user_id)
    if subscription:
        end_date = subscription[6]
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        if end_date > datetime.now():
            return f"✅ Активна до {end_date.strftime('%d.%m.%Y')}"
        return "❌ Истекла"
    return "❌ Отсутствует"

def get_user_profile(user_id: int):
    conn = sqlite3.connect('vpn_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    subscription = get_user_subscription(user_id)
    return user, subscription

# Функции меню
def main_menu():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    keyboard = InlineKeyboardBuilder()
    buttons = [
        ("📱 Приложения", "apps"),
        ("💳 Тарифы", "plans"), 
        ("🛠️ Помощь", "help"),
        ("👤 Профиль", "profile"),
        ("🌐 Конфиг", "download"),
        ("📞 Поддержка", "support")
    ]
    
    for text, callback_data in buttons:
        keyboard.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    
    keyboard.adjust(2, 2, 1, 1)
    return keyboard.as_markup()

def subscription_check_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📢 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
    keyboard.add(InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription"))
    keyboard.adjust(1)
    return keyboard.as_markup()

def help_menu():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    return keyboard.as_markup()

def profile_menu():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    return keyboard.as_markup()