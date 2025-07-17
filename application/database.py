import sqlite3
from flask import g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("app.db")
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with open("tables.sql", "r") as sql_file:
        sql_script = sql_file.read()

    db.executescript(sql_script)
    db.commit()
    close_db()