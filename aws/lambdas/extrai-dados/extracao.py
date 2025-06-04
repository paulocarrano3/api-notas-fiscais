import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from algoritmos import fuzzy_search_simples

def extrair_dados_nota(texto):
    tokens = word_tokenize(texto)
    stop_words = set(stopwords.words("portuguese"))
    tokens_filtrados = [word for word in tokens if word.lower() not in stop_words]
    cnpj_emissor, cpf_consumidor, data_emissao = extrair_regex(texto)
    endereco = extrair_endereco(texto)
    nome_emissor = extrair_nome_emissor(texto)
    numero_nota = extrair_numero_nota(texto)
    serie = extrair_serie(texto)
    valor_total = extrair_valor_total(texto)
    forma_pgto = extrair_forma_pagamento(texto)
    return {
        "nome_emissor": nome_emissor,
        "CNPJ_emissor": cnpj_emissor,
        "endereco_emissor": endereco,
        "CNPJ_CPF_consumidor": cpf_consumidor,
        "data_emissao": data_emissao,
        "numero_nota_fiscal": numero_nota,
        "serie_nota_fiscal": serie,
        "valor_total": valor_total,
        "forma_pgto": forma_pgto
    }


def extrair_regex(texto):
    padrao_cnpj = r"\b\d{2}[\._]?\d{3}[\._]?\d{3}[/\\]?\d{4}-?\d{2}\b"
    padrao_cpf = r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b|\b\d{11}\b"
    padrao_data = r"\b\d{2}/\d{2}/\d{4}\b"

    cnpj_match = re.search(padrao_cnpj, texto)
    cpf_match = re.search(padrao_cpf, texto)
    data_match = re.search(padrao_data, texto)

    # fallback com fuzzy se falhar
    if not cnpj_match or not cpf_match or not data_match:
        texto_corrigido = fuzzy_search_simples(texto, ["cnpj", "cpf", "data"])
        cnpj_match = cnpj_match or re.search(padrao_cnpj, texto_corrigido)
        cpf_match = cpf_match or re.search(padrao_cpf, texto_corrigido)
        data_match = data_match or re.search(padrao_data, texto_corrigido)

    cnpj = cnpj_match.group(0) if cnpj_match else "None"
    cpf = cpf_match.group(0) if cpf_match else "None"
    data = data_match.group(0) if data_match else "None"

    return (cnpj, cpf, data)

def extrair_nome_emissor(texto):
        # Corrige erros comuns de OCR em "CNPJ"
    texto_corrigido = fuzzy_search_simples(texto, "cnpj")
    
    # Procura o CNPJ no texto (aceitando variações de formatação)
    match_cnpj = re.search(r"\bCNPJ[:\s]*\d{2}\.?\d{3}\.?\d{3}[\/\\]?\d{4}-?\d{2}", texto_corrigido, re.IGNORECASE)
    address_keywords = r"\b(?:RUA|R\.|AV(?:\.|ENIDA)?|AL(?:\.|AMEDA)?|(?:PRA[ÇC]A|PÇA\.?)|ROD(?:\.|OVIA)?|(?:TRAVESSA|TV\.?)|VL(?:\.|ILA)?|EST(?:\.|RADA)?|LG(?:\.|ARGO)?|QUADRA|KM|CEP|CHACARAS|JARDIM|AVE|VIA|IE)\b"

    if match_cnpj:
        pos_cnpj = match_cnpj.start()
        candidate_pre = texto_corrigido[:pos_cnpj].strip()
        
        # Lista de palavras que indicam início de endereço
        match_keyword = re.search(address_keywords, candidate_pre, re.IGNORECASE)
        if match_keyword:
            candidate_name = candidate_pre[:match_keyword.start()].strip()
        else:
            candidate_name = candidate_pre
        
        # Se o resultado estiver vazio ou for muito curto, tenta separar pelo delimitador " - "
        if not candidate_name or len(candidate_name.split()) < 2:
            candidate_name = candidate_pre.split(" - ")[0].strip()
        return candidate_name
    else:
        min_index = None
        for keyword in address_keywords:
            pos = texto.find(keyword)
            if pos != -1:
                if min_index is None or pos < min_index:
                    min_index = pos
                    
        if min_index is not None:
            # Corta o texto até a primeira ocorrência de uma palavra-chave
            endereco_emissor = texto[:min_index].strip()
        else:   
            # Fallback para a primeira linha, se nenhuma palavra-chave for encontrada
            endereco_emissor = texto.splitlines()[0].strip()
    
    return endereco_emissor





def extrair_endereco(texto):
    # Corrige possíveis erros de OCR em termos de endereço
    texto_corrigido = fuzzy_search_simples(texto, [
        "rua", "avenida", "travessa", "alameda", "quadra", "cep", "chacaras"
    ])
    
    # Define a parte inicial do endereço (palavra-chave)
    address_keywords = r"\b(?:RUA|R\.|AV(?:\.|ENIDA)?|AL(?:\.|AMEDA)?|(?:PRA[ÇC]A|PÇA\.?)|ROD(?:\.|OVIA)?|(?:TRAVESSA|TV\.?)|VL(?:\.|ILA)?|EST(?:\.|RADA)?|LG(?:\.|ARGO)?|QUADRA|KM|CEP|CHACARAS|JARDIM|AVE|VIA)\b"
    # Define as palavras que indicam onde o endereço deve parar
    stop_keywords = r"(?:\b(?:CNPJ|IE|CPF|TELEFONE|FONE|DANFE|DOCUMENTO|VALOR|FORMA\s+PAGAMENTO|NFC-e|CONSUMIDOR|CHAVE)\b)"
    
    # A regex utiliza negative lookahead para capturar até antes do stop_keywords
    pattern = address_keywords + r"(?:(?!\s*" + stop_keywords + r").)+"
    
    match = re.search(pattern, texto_corrigido, re.IGNORECASE)
    if match:
        address = match.group(0).strip()
        return address
    else:
        return "None"



def extrair_valor_total(texto):
    padroes_iniciais = [
        r"valor\s+total\s+r\$?\s*([\d.,]+)",
        r"valor\s+total\s*([\d.,]+)",
        r"total\s+r\$?\s*([\d.,]+)"
    ]

    for padrao in padroes_iniciais:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # Se nada for encontrado, corrige palavras com fuzzy (agora incluindo apenas "total")
    termos_fuzzy = ["valor total", "valor total r$", "total r$", "total"]
    texto_corrigido = fuzzy_search_simples(texto, termos_fuzzy,distancia_max=2)

    for padrao in padroes_iniciais + [r"total\s*([\d.,]+)"]:
        match = re.search(padrao, texto_corrigido, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return "None"


def extrair_serie(texto):
    padroes = [
        r"(?:S[ée]rie|Serie|ECF)[:\s\-]*?(\d{1,3})"
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # Fallback com fuzzy_search
    texto_corrigido = fuzzy_search_simples(texto, ["serie", "série", "ecf"],distancia_max=2)
    for padrao in padroes:
        match = re.search(padrao, texto_corrigido, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return "None"



def extrair_numero_nota(texto):
    padroes = [
        r"(?:extrato\s+n[ºo.°]*|nfc[-–]?[eE]?)\s*[:\-]?\s*(\d{4,})",
        r"(?:NF[\-–]?E|NME)[^0-9]{0,5}(\d{6,})",
        r"(?:Nº|No|Número|COO|CCF|Extrato\s+N)[:\s]*(\d{4,})",
    ]
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    texto_corrigido = fuzzy_search_simples(texto, ["nfe", "nf-e", "número", "coo", "ccf", "extrato", "nfc-e"])
    for padrao in padroes:
        match = re.search(padrao, texto_corrigido, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "None"

def extrair_forma_pagamento(texto):
    texto_lower = texto.lower()
    padroes = {
        "PIX": [r"pix"],
        "DINHEIRO": [r"dinheiro"],
        "CRÉDITO": [r"cart[aã]o\s+(de\s+)?cr[eé]dito", r"\bcr[eé]dito\b"],
        "DÉBITO": [r"cart[aã]o\s+(de\s+)?d[eé]bito", r"\bd[eé]bito\b"],
        "CARTÃO": [r"\bcart[aã]o\b"],
    }
    for forma, expressoes in padroes.items():
        for expr in expressoes:
            if re.search(expr, texto_lower, re.IGNORECASE):
                return forma
    texto_corrigido = fuzzy_search_simples(texto, ["pix", "dinheiro", "credito", "crédito", "debito", "débito", "cartao", "cartão"])
    texto_lower = texto_corrigido.lower()
    for forma, expressoes in padroes.items():
        for expr in expressoes:
            if re.search(expr, texto_lower, re.IGNORECASE):
                return forma
    return "None"