# -*- coding: utf-8 -*-
try:
    import aiogram
    import aiofiles
    import aiohttp
    print("✅ Все зависимости успешно загружены")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    exit(1)

# остальной код бота...
# -*- coding: utf-8 -*-
import asyncio
import datetime
import logging
import threading
import concurrent.futures as pool
import os
import sys

# Добавляем путь для импортов
sys.path.append(os.path.dirname(__file__))

from aiogram import executor
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import logger
import cmd
import config
import constant

from utils.throttling import ThrottlingMiddleware
from utils import notify_admins, database

# Инициализация базы данных при старте
try:
    from init_db import init_database
    init_database()
except Exception as e:
    print(f"Ошибка инициализации БД: {e}")

log = logging.getLogger('main')

async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Информация о боте"),
    ])

async def on_startup(dispatcher: Dispatcher):
    try:
        # Устанавливаем дефолтные команды
        await set_default_commands(dispatcher)

        # Уведомляет про запуск
        await notify_admins.notify(bot, f"Бот запущен. v.{constant.version}")
        log.info(f'Бот запущен v.{constant.version} : @{(await dispatcher.bot.get_me())["username"]}')
    except Exception as e:
        log.error(f"Ошибка в on_startup: {e}")

async def on_shutdown(dp):
    log.warning('Бот останавливается...')
    try:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await dp.bot.session.close()
        log.warning('Бот остановлен')
    except Exception as e:
        log.error(f"Ошибка в on_shutdown: {e}")

async def notification(bot: Bot):
    log.info("Запущен мониторинг уведомлений!")
    while True:
        try:
            all_notifications = database.get_all_notifications()
            for i in all_notifications:
                tg_id = i[0]
                message_body = i[1]
                dt = datetime.datetime.fromtimestamp(float(i[2]))

                if (dt - datetime.datetime.now()).total_seconds() <= 300:
                    log.info(f"Отправляю уведомление для {tg_id}")
                    try:
                        await bot.send_message(tg_id, message_body)
                    except Exception as e:
                        log.error(f"Ошибка отправки уведомления: {e}")
                    database.del_notification(tg_id, i[2])
        except Exception as e:
            log.error(f"Ошибка в notification loop: {e}")
        
        await asyncio.sleep(30)

if __name__ == '__main__':
    # Проверка токена
    if not config.bot_token:
        log.error("BOT_TOKEN не установлен!")
        sys.exit(1)
    
    try:
        PoolExecutor = pool.ThreadPoolExecutor()
        bot = Bot(token=config.bot_token, timeout=300)
        storage = MemoryStorage()
        dp = Dispatcher(bot, storage=storage)
        dp.middleware.setup(LoggingMiddleware('main'))
        dp.middleware.setup(ThrottlingMiddleware())

        cmd.setup(dp)
        cmd.start.setup(dp)

        dp['poolexecuter'] = PoolExecutor
        loop = asyncio.get_event_loop()
        loop.create_task(notification(bot))
        
        log.info("Запускаем бота...")
        executor.start_polling(dp, skip_updates=True, fast=False, 
                             on_startup=on_startup, on_shutdown=on_shutdown)
                             
    except Exception as e:
        log.error(f"Критическая ошибка при запуске бота: {e}")
        sys.exit(1)
