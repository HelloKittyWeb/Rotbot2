# -*- coding: utf-8 -*-
from aiogram import types
from aiogram.dispatcher.filters import Filter
import config

class IsTopic(Filter):
    key = "is_accept_topic"

    async def check(self, message: types.Message):
        if config.accept_topic_ids:
            if message.is_topic_message:
                if message.message_thread_id not in config.accept_topic_ids:
                    return False
        return True
