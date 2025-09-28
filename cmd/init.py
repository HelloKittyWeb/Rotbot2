# -*- coding: utf-8 -*-
from aiogram.dispatcher import Dispatcher
from aiogram import types

import config
from . import start, calc
import logging

log = logging.getLogger('main')

async def error_handler(update: types.Update, exception):
    log.error(update)
    log.exception(exception)
    await update.bot.send_message(config.bot_admins[0], 'Ошибка: ' + str(exception))
    return True

def setup(dp: Dispatcher):
    dp.register_errors_handler(error_handler)
