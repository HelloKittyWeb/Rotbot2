# -*- coding: utf-8 -*-
from aiogram import types

async def bot_start(msg: types.Message):
    await msg.answer(f"🫶Приветствую тебя, пользователь. 🤖Я Бот гниения в RUST. Напиши количество HP строения, а я посчитаю для тебя время в минутах⏱")
