import json
import boto3
import logging
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MODEL_ID = "amazon.titan-text-premier-v1:0"
REGIAO = "us-east-1"

bedrock = boto3.client("bedrock-runtime", region_name=REGIAO)
s3 = boto3.client("s3")


def lambda_handler(event, context):
    logger.info("🔹 Evento recebido: %s", json.dumps(event))

    try:
        # Trata o corpo vindo da Lambda anterior (pode vir como string ou dict)
        if isinstance(event.get("body"), str):
            dados = json.loads(event["body"])
        elif isinstance(event.get("body"), dict):
            dados = event["body"]
        else:
            dados = event

        # Gera o prompt com os dados extraídos
        prompt = gerar_prompt(dados)
        logger.info("🧠 Prompt enviado para o Titan:\n%s", prompt)

        # Envia o prompt para o modelo Titan via Bedrock
        resposta = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 500,
                    "temperature": 0.2,
                    "topP": 1,
                    "stopSequences": []
                }
            }),
            contentType="application/json",
            accept="application/json"
        )

        # Decodifica a resposta
        resultado = json.loads(resposta['body'].read().decode())
        texto_gerado = resultado['results'][0]['outputText']
        logger.info("✅ Resposta da LLM:\n%s", texto_gerado)

        # Tenta carregar diretamente o JSON, se possível
        try:
            json_final = json.loads(texto_gerado)
        except json.JSONDecodeError:
            # Fallback: remove marcações e busca primeiro bloco JSON
            texto_gerado = texto_gerado.replace("```json", "").replace("```", "").strip()
            match = re.search(r'\{.*\}', texto_gerado, re.DOTALL)
            if not match:
                raise ValueError("Não foi possível extrair um JSON válido da resposta da LLM.")
            json_str_puro = match.group(0)
            json_final = json.loads(json_str_puro)

        # Substitui None por "None" (string)
        for k, v in json_final.items():
            if v is None:
                json_final[k] = "None"
        logger.info("Chegou no return")
        return {
            "statusCode": 200,
            "body": json.dumps(json_final, ensure_ascii=False)
        }

    except Exception as e:
        logger.error("❌ Erro: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


def gerar_prompt(dados):
    return f"""
Você é um assistente que formata dados extraídos de notas fiscais.

Retorne apenas um JSON puro, sem explicações, código ou marcações, com os seguintes campos. 
Se algum dado estiver ausente, use o valor 'None' (como string). 

IMPORTANTE: não inclua nenhuma explicação, nem markdown (```), apenas o JSON puro como saída.

Campos esperados:
{{
  "nome_emissor": <string ou 'None'>,
  "CNPJ_emissor": <string ou 'None'>,
  "endereco_emissor": <string ou 'None'>,
  "CNPJ_CPF_consumidor": <string ou 'None'>,
  "data_emissao": <string ou 'None'>,
  "numero_nota_fiscal": <string ou 'None'>,
  "serie_nota_fiscal": <string ou 'None'>,
  "valor_total": <string ou 'None'>,
  "forma_pgto": <string ou 'None'>
}}

Aqui estão os dados extraídos:
{json.dumps(dados, ensure_ascii=False, indent=2)}

Apenas retorne o JSON no formato abaixo, nada mais:
{{
  "nome_emissor": ...,
  "CNPJ_emissor": ...,
  "endereco_emissor": ...,
  "CNPJ_CPF_consumidor": ...,
  "data_emissao": ...,
  "numero_nota_fiscal": ...,
  "serie_nota_fiscal": ...,
  "valor_total": ...,
  "forma_pgto": ...
}}
"""
