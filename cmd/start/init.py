# -*- coding: utf-8 -*-
from aiogram.dispatcher import Dispatcher
from aiogram import types

from .hook import bot_start

def setup(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands='start', chat_type=types.ChatType.PRIVATE, state='*')
