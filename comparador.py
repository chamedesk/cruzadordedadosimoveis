from rapidfuzz import fuzz


def parecido(sp, gold):
    pontos = 0

    if sp.get("cep") and gold.get("cep") and sp["cep"] == gold["cep"]:
        pontos += 45

    if sp.get("endereco") and gold.get("endereco"):
        pontos += fuzz.token_set_ratio(sp["endereco"], gold["endereco"]) * 0.25

    if sp.get("bairro") and gold.get("bairro"):
        pontos += fuzz.token_set_ratio(sp["bairro"], gold["bairro"]) * 0.15

    if sp.get("area") and gold.get("area"):
        if abs(float(sp["area"]) - float(gold["area"])) <= 3:
            pontos += 10

    if sp.get("valor") and gold.get("valor"):
        valor_sp = float(sp["valor"])
        valor_gold = float(gold["valor"])
        if valor_sp > 0:
            diferenca = abs(valor_sp - valor_gold) / valor_sp
            if diferenca <= 0.08:
                pontos += 15

    return pontos >= 70, round(pontos, 2)
