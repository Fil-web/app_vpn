from aiogram import types, F

async def select_plan(callback: types.CallbackQuery):
    plan_data = callback.data
    
    plans = {
        "plan_1month": {"name": "1 месяц", "price": 299},
        "plan_3months": {"name": "3 месяца", "price": 799},
        "plan_6months": {"name": "6 месяцев", "price": 1399},
        "plan_12months": {"name": "12 месяцев", "price": 2399}
    }
    
    plan = plans.get(plan_data)
    if plan:
        plan_text = f"""
💳 Оплата тарифа

📋 Тариф: {plan['name']}
💰 Стоимость: {plan['price']}₽

Выберите способ оплаты:
        """
        
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="💳 Карта", callback_data=f"pay_card_{plan_data}"))
        keyboard.add(InlineKeyboardButton(text="📱 Qiwi", callback_data=f"pay_qiwi_{plan_data}"))
        keyboard.add(InlineKeyboardButton(text="🎫 ЮMoney", callback_data=f"pay_ymoney_{plan_data}"))
        keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_plans"))
        keyboard.adjust(1)
        
        await callback.message.edit_text(plan_text, reply_markup=keyboard.as_markup(), parse_mode='HTML')

async def process_payment(callback: types.CallbackQuery):
    payment_data = callback.data.split("_")
    payment_method = payment_data[1]
    plan_id = payment_data[2]
    
    payment_text = f"""
💳 Оплата через {payment_method}

Для оплаты перейдите по ссылке:
https://payment.example.com/{payment_method}

После оплаты подписка активируется автоматически.
    """
    
    await callback.message.edit_text(payment_text, parse_mode='HTML')