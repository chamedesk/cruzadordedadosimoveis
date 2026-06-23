from rapidfuzz import fuzz


def faixa(valor, gold_valor, percentual=5):
    if not valor or not gold_valor:
        return False
    return abs(valor - gold_valor) <= valor * percentual / 100


def score_match(sp, gold):
    score = 0
    motivos = []
    if sp.get('endereco') and gold.get('endereco'):
        s = fuzz.token_set_ratio(sp['endereco'], gold['endereco'])
        score += s * 0.40
        motivos.append(f'endereço {s:.0f}%')
    bairro_score = fuzz.token_set_ratio(sp.get('bairro') or '', gold.get('bairro') or '')
    score += bairro_score * 0.20
    motivos.append(f'bairro {bairro_score:.0f}%')
    if sp.get('dormitorios') == gold.get('dormitorios'):
        score += 10
        motivos.append('dorms igual')
    if sp.get('area') and gold.get('area') and abs(float(sp['area']) - float(gold['area'])) <= 3:
        score += 15
        motivos.append('metragem parecida')
    if faixa(float(sp.get('valor') or 0), float(gold.get('valor') or 0)):
        score += 15
        motivos.append('valor parecido')
    return min(score, 100), ', '.join(motivos)
