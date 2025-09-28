# -*- coding: utf-8 -*-
import sqlite3
import os
import constant

def init_database():
    """Инициализация базы данных"""
    conn = sqlite3.connect(constant.database)
    cursor = conn.cursor()
    
    # Создание таблицы уведомлений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            tg_id INTEGER,
            note TEXT,
            time TEXT
        )
    ''')
    
    # Создание таблицы заметок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("База данных инициализирована")

if __name__ == '__main__':
    init_database()
