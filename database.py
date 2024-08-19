import sqlite3
from flask import g

DATABASE = 'seu_banco_de_dados.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with sqlite3.connect(DATABASE) as db:
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())

def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()