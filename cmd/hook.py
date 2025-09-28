# -*- coding: utf-8 -*-
import datetime

from aiogram import types
import time
import logging

import config
from utils import keyboard
from utils import database

log = logging.getLogger('main')

materials = {
    'soloma': '🕸Солома:',
    'wood': '🌴Дерево:',
    'stone': '🪨Камень:',
    'metall': '🦾Металл:',
    'mvk': '⚙МВК:',
    'garage': '🚪🏗Гаражная дверь:',
    'metal_door': '🚪🦾Металлическая дверь:',
    'wood_door': '🚪🌴Деревянная дверь:',
    'mvk_door': '🚪⚙МВК дверь:',
}

def generate_time(sec):
    text = ''
    _time = time.gmtime(sec)
    if _time.tm_hour > 0:
        text = f'{_time.tm_hour} ч. {_time.tm_min} м.'
    else:
        text = f'{_time.tm_min} м.'
    return text

async def create_notification(msg: types.CallbackQuery):
    tg_id = msg.data.split(':')[0]
    material = msg.data.split(':')[1]
    timestamp = msg.data.split(':')[2]
    note_id = msg.data.split(':')[3]

    if datetime.datetime.fromtimestamp(float(timestamp)) < datetime.datetime.now():
        await msg.message.delete_reply_markup()
        await msg.answer('Время для гниения истекло!')
        return

    if msg.from_user.id != int(tg_id):
        await msg.answer("Сообщение не для тебя!")
        return

    try:
        await msg.bot.get_chat(tg_id)
    except:
        await msg.message.answer("Не удалось добавить напоминание. Скорее всего необходимо написать мне в личное сообщение, чтобы меня активировать для твоего профиля. После попробуй еще раз")
        return

    if note_id != '-1':
        gnote = database.get_note(note_id)
    else:
        gnote = ''

    note = f'Уведомление для ресурса {materials[material]}\n\n{gnote}\n\nОсталось менее 5 минут до гниения!'
    database.add_notification(int(tg_id), note, timestamp)
    await msg.bot.send_message(tg_id, 'Заметка добавлена')

async def bot_calc(msg: types.Message):
    try:
        bot_username = await msg.bot.get_me()
        if msg.chat.type != 'private':
            if bot_username['username'].lower() not in msg.text.lower():
                return
            health = msg.text.split(' ')[1]
            if not health:
                await msg.answer(f"Неверное число HP постройки\n @{bot_username} 200 заметка")
                return
            if len(msg.text.split(' ')) > 3:
                notification_note = ' '.join(msg.text.split(' ')[2:])
            else:
                notification_note = None
        else:
            if len(msg.text.split(' ')) > 1:
                notification_note = ' '.join(msg.text.split(' ')[1:])
                health = msg.text.split(' ')[0]
            else:
                notification_note = None
                health = msg.text

            if not health:
                await msg.answer(f"Неверное число HP постройки\n 200 заметка")
                return

        if int(health) < 0:
            raise Exception("Bad number")
    except:
        log.exception('')
        if msg.chat.type == 'private':
            await msg.answer("🥵Похоже ты написал не цифру или отрицательное число. Напиши количество HP строения цифрой, а я посчитаю оставшееся время до полного гниения✍")
        return

    bulding = {
        'soloma': {'max': 10, 'name': '🕸Солома:', 'time': round(int(health) * 60 / 10)},
        'wood': {'max': 250, 'name': '🌴Дерево:', 'time': round(int(health) * 180 / 250)},
        'stone': {'max': 500, 'name': '🪨Камень:', 'time': round(int(health) * 300 / 500)},
        'metall': {'max': 1000, 'name': '🦾Металл:', 'time': round(int(health) * 480 / 1000)},
        'mvk': {'max': 2000, 'name': '⚙МВК:', 'time': round(int(health) * 720 / 2000)},
        'garage': {'max': 600, 'name': '🚪🏗Гаражная дверь:', 'time': round(int(health) * 480 / 600)},
        'metal_door': {'max': 250, 'name': '🚪🦾Металлическая дверь:', 'time': round(int(health) * 480 / 250)},
        'wood_door': {'max': 200, 'name': '🚪🌴Деревянная дверь:', 'time': round(int(health) * 180 / 200)},
        'mvk_door': {'max': 1000, 'name': '🚪⚙МВК дверь:', 'time': round(int(health) * 720 / 1000)},
    }

    _text = ''
    kb_values = {}
    for k, v in bulding.items():
        if not int(health) > v['max']:
            _t = generate_time(v['time'] * 60)
            _text += v['name'] + ' ' + _t + '\n'
            kb_values[k] = {'time': v['time'] * 60, 'name': v['name'], 'note': notification_note}
    if kb_values:
        kb = keyboard.get_notification_kb(kb_values, msg.from_user.id)
    else:
        kb = None

    _text += f'\n\nЧтобы добавить уведомление, нажми на кнопку ниже'
    if not notification_note:
        if msg.chat.type != 'private':
            _ct = f'@{bot_username["username"]}'
        else:
            _ct = ''
        _text += f'\nЧтобы добавить заметку:\n{_ct} {health} <заметка>'

    await msg.answer(_text, reply_markup=kb)
