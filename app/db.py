import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'instance' / 'gold_captacao.db'

def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS sp_imoveis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        tipo TEXT,
        bairro TEXT,
        cidade TEXT,
        endereco TEXT,
        cep TEXT,
        valor REAL,
        valor_comissao REAL,
        area REAL,
        dormitorios INTEGER,
        vagas INTEGER,
        proprietario TEXT,
        telefone TEXT,
        whatsapp TEXT,
        email TEXT,
        descricao TEXT,
        atualizado_em TEXT,
        link TEXT,
        status TEXT DEFAULT 'pendente'
    )''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS gold_imoveis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        titulo TEXT,
        bairro TEXT,
        cidade TEXT,
        endereco TEXT,
        valor REAL,
        area REAL,
        dormitorios INTEGER,
        vagas INTEGER,
        link TEXT
    )''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS comparacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sp_codigo TEXT,
        gold_codigo TEXT,
        score REAL,
        status TEXT,
        motivo TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
