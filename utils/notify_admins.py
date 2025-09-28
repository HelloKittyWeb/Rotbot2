# -*- coding: utf-8 -*-
import logging
from aiogram import Bot
from config import bot_admins

log = logging.getLogger('main')

async def notify(bot: Bot, message: str):
    for admin in bot_admins:
        try:
            await bot.send_message(admin, message)
        except Exception as err:
            log.exception(err)
