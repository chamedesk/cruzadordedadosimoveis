from flask import Flask, render_template, request, redirect, send_file
import io, pandas as pd
from .db import init_db, get_conn
from .matcher import score_match
from .scraper_gold import extrair_gold

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
init_db()

@app.route('/')
def index():
    q = request.args.get('q','')
    conn=get_conn()
    rows=conn.execute('''SELECT * FROM sp_imoveis WHERE status != 'ja_cadastrado'
        AND (?='' OR bairro LIKE ? OR codigo LIKE ? OR endereco LIKE ?)
        ORDER BY atualizado_em DESC LIMIT 300''',(q,f'%{q}%',f'%{q}%',f'%{q}%')).fetchall()
    conn.close()
    return render_template('index.html', rows=rows, q=q)

@app.route('/gold/atualizar')
def gold_atualizar():
    total = extrair_gold(max_paginas=3)
    return redirect('/?msg=Gold atualizada: '+str(total))

@app.route('/comparar')
def comparar():
    conn=get_conn(); cur=conn.cursor()
    sp_rows=[dict(r) for r in cur.execute('SELECT * FROM sp_imoveis').fetchall()]
    gold_rows=[dict(r) for r in cur.execute('SELECT * FROM gold_imoveis').fetchall()]
    for sp in sp_rows:
        melhor=(None,0,'')
        for gold in gold_rows:
            sc,mot=score_match(sp,gold)
            if sc>melhor[1]: melhor=(gold,sc,mot)
        if melhor[1] >= 82:
            cur.execute("UPDATE sp_imoveis SET status='ja_cadastrado' WHERE codigo=?",(sp['codigo'],))
            cur.execute('INSERT INTO comparacoes (sp_codigo,gold_codigo,score,status,motivo) VALUES (?,?,?,?,?)', (sp['codigo'], melhor[0]['codigo'], melhor[1], 'ja_cadastrado', melhor[2]))
        else:
            cur.execute("UPDATE sp_imoveis SET status='novo' WHERE codigo=?",(sp['codigo'],))
    conn.commit(); conn.close()
    return redirect('/')

@app.route('/exportar')
def exportar():
    conn=get_conn()
    df=pd.read_sql_query("SELECT * FROM sp_imoveis WHERE status='novo'", conn)
    conn.close()
    bio=io.BytesIO(); df.to_excel(bio,index=False); bio.seek(0)
    return send_file(bio, as_attachment=True, download_name='imoveis_novos_gold_captacao.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/demo')
def demo():
    from .scraper_spimovel import importar_manual
    importar_manual([{
        'codigo':'216661','tipo':'Apartamento para Venda','bairro':'Gleba do Pêssego','cidade':'São Paulo','endereco':'Rua Sho Yoshioka, 395 Bloco 1 AP 12º andar privativo','cep':'08265-381','valor':65000,'valor_comissao':69148.95,'area':48,'dormitorios':2,'vagas':0,'proprietario':'Leila Argolo','telefone':'(11) 98366-1131','whatsapp':'(11) 98917-3414','email':'leila.argolo1979@hotmail.com','descricao':'Apartamento 2 dormitórios pronto para entregar','atualizado_em':'2024-04-02','link':''
    }])
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
