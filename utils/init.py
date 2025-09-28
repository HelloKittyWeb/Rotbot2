# -*- coding: utf-8 -*-
from aiogram.dispatcher import Dispatcher
from aiogram import types

from .hook import bot_calc, create_notification
from cmd import filters

def setup(dp: Dispatcher):
    dp.register_message_handler(bot_calc, filters.IsTopic(), state='*')
    dp.register_callback_query_handler(create_notification, state='*')
