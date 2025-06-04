import json
import boto3
import logging

# Nome do bucket de origem onde as imagens das notas fiscais são armazenadas
SOURCE_BUCKET = "meu-bucket-notas"

# Inicializa os clientes AWS
s3_client = boto3.client("s3")
textract_client = boto3.client("textract")

# Configura o logger da Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Função principal da Lambda, chamada automaticamente pela AWS
def lambda_handler(event, context):
    # Recupera o nome do arquivo (chave) do evento recebido
    key = event.get("key") or event.get("input", {}).get("key")

    # Verificação de segurança: garante que a chave foi informada
    if not key:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Chave do arquivo não fornecida"})
        }

    try:
        logger.info(f"📄 Iniciando OCR do arquivo: {key}")

        # OCR síncrono usando Textract - mais rápido para imagens até 5MB
        response = textract_client.detect_document_text(
            Document={'S3Object': {'Bucket': SOURCE_BUCKET, 'Name': key}}
        )

        # Filtra os blocos do tipo "LINE" e junta todo o texto extraído em uma única string
        extracted_text = " ".join(
            block["Text"]
            for block in response["Blocks"]
            if block["BlockType"] == "LINE"
        )

        logger.info(f"✅ Texto extraído com sucesso.")

        # Retorna o texto extraído em formato JSON para o próximo passo da Step Function
        return {
            "statusCode": 200,
            "body": json.dumps({
                "text": extracted_text,  # Texto OCR extraído
                "key": key               # Nome do arquivo (útil para rastreabilidade)
            }, ensure_ascii=False)
        }

    except Exception as e:
        # Em caso de erro, registra o erro no log e retorna código 500 com mensagem de erro
        logger.error(f"❌ Erro ao processar OCR: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
