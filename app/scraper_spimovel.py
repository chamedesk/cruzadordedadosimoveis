from .db import get_conn


def importar_manual(lista):
    """Importa lista de dicionários extraída manualmente/CSV do SP Imóvel."""
    conn = get_conn(); cur = conn.cursor(); total = 0
    for im in lista:
        cur.execute('''INSERT OR REPLACE INTO sp_imoveis
        (codigo,tipo,bairro,cidade,endereco,cep,valor,valor_comissao,area,dormitorios,vagas,proprietario,telefone,whatsapp,email,descricao,atualizado_em,link)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            im.get('codigo'), im.get('tipo'), im.get('bairro'), im.get('cidade'), im.get('endereco'), im.get('cep'),
            im.get('valor'), im.get('valor_comissao'), im.get('area'), im.get('dormitorios'), im.get('vagas'),
            im.get('proprietario'), im.get('telefone'), im.get('whatsapp'), im.get('email'), im.get('descricao'), im.get('atualizado_em'), im.get('link')
        ))
        total += 1
    conn.commit(); conn.close(); return total

# Próxima etapa: automação Playwright com login autorizado no SP Imóvel.
# Isso precisa ser ajustado olhando o HTML real dos campos/botões depois do login.
