from flask import Blueprint, render_template, request, redirect, send_file
from openpyxl import Workbook
from io import BytesIO
from .database import get_conn
from .comparador import parecido

bp = Blueprint("main", __name__)


def row_to_dict(row):
    return dict(row)


@bp.route("/")
def index():
    bairro = request.args.get("bairro", "").strip()
    status = request.args.get("status", "").strip()

    conn = get_conn()
    sp = [row_to_dict(r) for r in conn.execute("SELECT * FROM imoveis_sp ORDER BY id DESC").fetchall()]
    gold = [row_to_dict(r) for r in conn.execute("SELECT * FROM imoveis_gold").fetchall()]
    conn.close()

    resultados = []
    for imovel in sp:
        achou = False
        melhor_score = 0
        for g in gold:
            ok, score = parecido(imovel, g)
            melhor_score = max(melhor_score, score)
            if ok:
                achou = True
                break
        imovel["comparacao"] = "ja_cadastrado" if achou else "novo"
        imovel["score"] = melhor_score
        resultados.append(imovel)

    if bairro:
        resultados = [r for r in resultados if bairro.lower() in (r.get("bairro") or "").lower()]
    if status:
        resultados = [r for r in resultados if r["comparacao"] == status]

    return render_template("index.html", imoveis=resultados, bairro=bairro, status=status)


@bp.route("/demo")
def demo():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM imoveis_sp")
    cur.execute("DELETE FROM imoveis_gold")
    cur.execute('''INSERT INTO imoveis_sp
        (codigo,tipo,bairro,cidade,endereco,cep,valor,area,dormitorios,vagas,proprietario,telefone,whatsapp,email,link)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        ("216661","Apartamento","Gleba do Pêssego","São Paulo","Rua exemplo, 100","00000-000",65000,48,2,1,"Leila Argolo","(11) 0000-0000","11999999999","email@exemplo.com","#"))
    cur.execute('''INSERT INTO imoveis_sp
        (codigo,tipo,bairro,cidade,endereco,cep,valor,area,dormitorios,vagas,proprietario,telefone,whatsapp,email,link)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        ("230237","Apartamento","Jardim Vila Carrão","São Paulo","Rua das Estrelas, 920","08330-422",180000,25,1,0,"Marina","","","","#"))
    cur.execute('''INSERT INTO imoveis_gold
        (codigo,titulo,bairro,cidade,endereco,cep,valor,area,dormitorios,vagas,link)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
        ("AP1480-GASD","Apartamento Artur Alvim","Artur Alvim","São Paulo","Rua exemplo cadastrada, 50","11111-111",280000,36,2,1,"#"))
    conn.commit()
    conn.close()
    return redirect("/")


@bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        data = request.form
        conn = get_conn()
        conn.execute('''INSERT INTO imoveis_sp
            (codigo,tipo,bairro,cidade,endereco,cep,valor,area,dormitorios,vagas,proprietario,telefone,whatsapp,email,link)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (data.get("codigo"),data.get("tipo"),data.get("bairro"),data.get("cidade"),data.get("endereco"),data.get("cep"),data.get("valor") or 0,data.get("area") or 0,data.get("dormitorios") or 0,data.get("vagas") or 0,data.get("proprietario"),data.get("telefone"),data.get("whatsapp"),data.get("email"),data.get("link")))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("novo.html")


@bp.route("/exportar")
def exportar():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM imoveis_sp ORDER BY id DESC").fetchall()
    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Imoveis SP"
    headers = ["codigo","tipo","bairro","cidade","endereco","cep","valor","area","dormitorios","vagas","proprietario","telefone","whatsapp","email","link"]
    ws.append(headers)
    for r in rows:
        ws.append([r[h] for h in headers])

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="imoveis_gold_captacao.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
