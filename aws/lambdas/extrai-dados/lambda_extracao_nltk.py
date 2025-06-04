import sys
import os
import json
import logging
import nltk
from nltk.corpus import stopwords

from extracao import extrair_dados_nota

LAYER_SITE_PACKAGES = "/opt/python/lib/python3.10/site-packages"
LAYER_NLTK_DATA = os.path.join(LAYER_SITE_PACKAGES, "nltk_data")

if LAYER_SITE_PACKAGES not in sys.path:
    sys.path.append(LAYER_SITE_PACKAGES)
if LAYER_NLTK_DATA not in nltk.data.path:
    nltk.data.path.append(LAYER_NLTK_DATA)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    _ = stopwords.words("portuguese")
    logger.info("Stopwords carregadas")
except Exception as e:
    logger.error("Erro ao carregar stopwords: %s", str(e))


def lambda_handler(event, context):
    logger.info("Evento recebido: %s", json.dumps(event))
    try:
        body = event.get("body")
        if body:
            # Se o body for uma string JSON, tenta carregar
            if isinstance(body, str):
                try:
                    parsed = json.loads(body)
                    if isinstance(parsed, dict) and "text" in parsed:
                        texto = parsed["text"]
                        origem = "Texto no campo 'text' dentro do JSON"
                    else:
                        texto = body.strip('"')  # texto puro (sem campo "text")
                        origem = "Texto bruto stringificado"
                except json.JSONDecodeError:
                    texto = body.strip('"')  # texto bruto
                    origem = "Texto bruto simples"
            elif isinstance(body, dict) and "text" in body:
                texto = body["text"]
                origem = "Texto no campo 'text' (dict direto)"
            else:
                raise ValueError("Formato do corpo não reconhecido")
        else:
            raise ValueError("Evento sem corpo")

        logger.info("Texto extraído (%s):\n%s", origem, texto)
        dados_extraidos = extrair_dados_nota(texto)
        logger.info("Dados extraídos:")
        for k, v in dados_extraidos.items():
            logger.info(f"{k}: {v}")
        
        logger.info("Chegou no return")
        return {"statusCode": 200, "body": json.dumps(dados_extraidos, ensure_ascii=False)}
    except Exception as e:
        logger.error("Erro no processamento: %s", str(e))
        return {"statusCode": 500, "body": str(e)}
