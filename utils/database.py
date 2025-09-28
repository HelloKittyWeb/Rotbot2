# -*- coding: utf-8 -*-

import sqlite3
from contextlib import contextmanager
import constant
import logging

log = logging.getLogger('main')

@contextmanager
def db_connect() -> sqlite3.Cursor:
    db = sqlite3.connect(constant.database)
    cur = db.cursor()
    yield cur
    db.commit()
    cur.close()
    db.close()

def add_notes(note_text):
    try:
        with db_connect() as cur:
            cur.execute("INSERT INTO notes(note) VALUES (?)", (note_text,))
    except sqlite3.IntegrityError:
        pass

    with db_connect() as cur:
        cur.execute("select id from notes where note=?", (note_text,))
        res = cur.fetchone()

    return res[0]

def get_note(id):
    with db_connect() as cur:
        cur.execute("select note from notes where id=?", (id,))
        res = cur.fetchone()
    return res[0]

def add_notification(tg_id, note, timestamp):
    with db_connect() as cur:
        cur.execute("select * from notifications where tg_id=? and time=?", (tg_id,timestamp))
        res = cur.fetchone()
        if res:
            log.warning(f"Не добавлено уведомление для {tg_id}. Оно уже было добавлено")
            return

    with db_connect() as cur:
        cur.execute("INSERT INTO notifications(tg_id, note, time) VALUES (?, ?, ?)", (tg_id,note, timestamp))

def del_notification(tg_id, timestamp):
    with db_connect() as cur:
        cur.execute("delete from notifications where tg_id=? and time=?", (tg_id, timestamp))

def get_all_notifications():
    with db_connect() as cur:
        cur.execute("select * from notifications")
        res = cur.fetchall()
    return res
