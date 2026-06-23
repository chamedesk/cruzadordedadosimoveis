import re
import requests
from bs4 import BeautifulSoup
from .db import get_conn

BASE = 'https://www.goldlesteimoveis.com.br/'

def dinheiro(txt):
    if not txt: return None
    n = re.sub(r'[^0-9,]', '', txt).replace('.', '').replace(',', '.')
    try: return float(n)
    except: return None

def numero(txt):
    m = re.search(r'(\d+(?:[,.]\d+)?)', txt or '')
    return float(m.group(1).replace(',', '.')) if m else None

def extrair_gold(max_paginas=5):
    """Coletor inicial. Pode precisar ajuste conforme páginas da Kenlo."""
    conn = get_conn(); cur = conn.cursor()
    total = 0
    for page in range(1, max_paginas + 1):
        url = f'{BASE}imoveis/a-venda?pagina={page}'
        html = requests.get(url, timeout=20, headers={'User-Agent':'Mozilla/5.0'}).text
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a in soup.select('a[href*="/imovel/"]'):
            href = a.get('href')
            if href and href not in links:
                links.append(href if href.startswith('http') else BASE.rstrip('/') + href)
        for link in links:
            try:
                h = requests.get(link, timeout=20, headers={'User-Agent':'Mozilla/5.0'}).text
                s = BeautifulSoup(h, 'html.parser')
                texto = s.get_text(' ', strip=True)
                cod = re.search(r'\b[A-Z]{1,3}\d{2,6}-[A-Z0-9]+\b', texto)
                titulo = s.find(['h1','h2'])
                valor = dinheiro(texto)
                area = numero(re.search(r'(\d+[,.]?\d*)\s*m²', texto).group(0) if re.search(r'(\d+[,.]?\d*)\s*m²', texto) else '')
                dorm = re.search(r'(\d+)\s*dorm', texto, re.I)
                bairro = ''
                if '-' in (titulo.get_text(' ', strip=True) if titulo else ''):
                    partes = titulo.get_text(' ', strip=True).split('-')
                    bairro = partes[-2].strip() if len(partes) >= 2 else ''
                cur.execute('''INSERT OR REPLACE INTO gold_imoveis
                    (codigo,titulo,bairro,cidade,valor,area,dormitorios,link)
                    VALUES (?,?,?,?,?,?,?,?)''', (
                        cod.group(0) if cod else link.split('/')[-1],
                        titulo.get_text(' ', strip=True) if titulo else '',
                        bairro, 'São Paulo', valor, area,
                        int(dorm.group(1)) if dorm else None, link
                    ))
                total += 1
            except Exception:
                continue
    conn.commit(); conn.close()
    return total
