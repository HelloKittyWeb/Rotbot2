# -*- coding: utf-8 -*-
from aiogram import types

async def bot_start(msg: types.Message):
    await msg.answer(f"🫶Приветствую тебя, пользователь. 🤖Я Бот гниения в RUST. Напиши количество HP строения, а я посчитаю для тебя время в минутах⏱")

def setup_start_handlers(dp):
    """Регистрация обработчиков старта"""
    from aiogram import types
    dp.register_message_handler(bot_start, commands='start', chat_type=types.ChatType.PRIVATE, state='*')
