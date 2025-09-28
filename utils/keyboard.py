# -*- coding: utf-8 -*-
import typing
import time
import datetime
from aiogram import types
from utils import database

def get_notification_kb(kb_values: typing.Dict, tg_id):
    kb = types.InlineKeyboardMarkup()
    _id_note = None
    for k, v in kb_values.items():
        sec_to_time = time.gmtime(v['time'])
        dt = datetime.datetime.now() + datetime.timedelta(hours=sec_to_time.tm_hour, minutes=sec_to_time.tm_min, seconds=sec_to_time.tm_sec)

        if not _id_note:
            if v['note']:
                _id_note = database.add_notes(v['note'])
            else:
                _id_note = -1

        data = str(tg_id) + ':' + k + ':' + str(dt.timestamp()) + ':' + str(_id_note)

        kb.insert(types.InlineKeyboardButton(v['name'].replace(':', ''), callback_data=data))
    return kb
