import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "gold_captacao.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS imoveis_sp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT,
            tipo TEXT,
            bairro TEXT,
            cidade TEXT,
            endereco TEXT,
            cep TEXT,
            valor REAL,
            area REAL,
            dormitorios INTEGER,
            vagas INTEGER,
            proprietario TEXT,
            telefone TEXT,
            whatsapp TEXT,
            email TEXT,
            link TEXT,
            status TEXT DEFAULT 'novo'
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS imoveis_gold (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT,
            titulo TEXT,
            bairro TEXT,
            cidade TEXT,
            endereco TEXT,
            cep TEXT,
            valor REAL,
            area REAL,
            dormitorios INTEGER,
            vagas INTEGER,
            link TEXT
        )
    ''')
    conn.commit()
    conn.close()
