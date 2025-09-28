# -*- coding: utf-8 -*-
import asyncio
import datetime
import logging
import concurrent.futures as pool
import os
import sys

from aiogram import executor
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

# Импорты из нашего кода
import config
import constant

# Инициализация логгера
logger_module = __import__('logger')
logger = logger_module.logger

# Инициализация базы данных при старте
init_db_module = __import__('init_db')
init_db_module.init_database()

# Импорты утилит
utils_module = __import__('utils')
database = utils_module.database
notify_admins = utils_module.notify_admins
throttling_module = __import__('utils.throttling', fromlist=['ThrottlingMiddleware'])
ThrottlingMiddleware = throttling_module.ThrottlingMiddleware

# Импорты обработчиков
cmd_hook_module = __import__('cmd.hook', fromlist=['bot_calc', 'create_notification'])
bot_calc = cmd_hook_module.bot_calc
create_notification = cmd_hook_module.create_notification

cmd_start_hook_module = __import__('cmd.start.hook', fromlist=['bot_start'])
bot_start = cmd_start_hook_module.bot_start

cmd_filters_module = __import__('cmd.filters', fromlist=['IsTopic'])
IsTopic = cmd_filters_module.IsTopic

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

def setup_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    # Обработчик команды /start
    dp.register_message_handler(bot_start, commands='start', chat_type=types.ChatType.PRIVATE, state='*')
    
    # Обработчики калькулятора
    dp.register_message_handler(bot_calc, IsTopic(), state='*')
    dp.register_callback_query_handler(create_notification, state='*')
    
    # Обработчик ошибок
    dp.register_errors_handler(error_handler)

async def error_handler(update: types.Update, exception):
    log.error(update)
    log.exception(exception)
    await update.bot.send_message(config.bot_admins[0], 'Ошибка: ' + str(exception))
    return True

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

        # Регистрируем обработчики
        setup_handlers(dp)

        dp['poolexecuter'] = PoolExecutor
        loop = asyncio.get_event_loop()
        loop.create_task(notification(bot))
        
        log.info("Запускаем бота...")
        executor.start_polling(dp, skip_updates=True, fast=False, 
                             on_startup=on_startup, on_shutdown=on_shutdown)
                             
    except Exception as e:
        log.error(f"Критическая ошибка при запуске бота: {e}")
        sys.exit(1)
