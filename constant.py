# -*- coding: utf-8 -*-
import os

version = '0.0.3'

work_dir = os.path.abspath(os.path.split(__file__)[0])
logs_dir = os.path.join(work_dir, 'logs')
database = os.path.abspath(os.path.join(work_dir, 'database.sqlite'))

# Создаем директории при импорте
os.makedirs(logs_dir, exist_ok=True)
