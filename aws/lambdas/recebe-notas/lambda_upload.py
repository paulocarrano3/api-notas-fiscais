import json
import boto3
import base64
import uuid
import logging
import time
# Configurações
S3_BUCKET = "meu-bucket-notas"
REGIAO = "us-east-1"
 
# Inicializar clientes AWS
s3_client = boto3.client("s3")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
 
def lambda_handler(event, context):
    logger.info("🔹 Evento recebido: %s", json.dumps(event))
 
    try:
        # Certificar-se de que a requisição contém um body válido
        body = event.get("body", None)
        if not body:
            logger.error("❌ Erro: Requisição sem corpo válido.")
            return {"statusCode": 400, "body": json.dumps({"error": "Requisição sem corpo válido."})}
 
        # API Gateway envia `body` como string, então precisamos convertê-lo para JSON
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            logger.error("❌ Erro: Formato JSON inválido.")
            return {"statusCode": 400, "body": json.dumps({"error": "Formato JSON inválido."})}
 
        # Verificar se a chave 'file' está presente
        if "file" not in body or not body["file"]:
            logger.error("❌ Erro: Arquivo não encontrado na requisição.")
            return {"statusCode": 400, "body": json.dumps({"error": "Arquivo não encontrado na requisição."})}
 
        # Decodificar imagem Base64
        try:
            file_data = base64.b64decode(body["file"])
            logger.info(f"✅ Arquivo recebido. Tamanho: {len(file_data)} bytes")
        except Exception as e:
            logger.error(f"❌ Erro ao decodificar Base64: {str(e)}")
            return {"statusCode": 400, "body": json.dumps({"error": f"Erro ao decodificar Base64: {str(e)}"})}
 
        file_name = f"nota-{uuid.uuid4()}.jpg"
 
        # Salvar no S3
        s3_client.put_object(Bucket=S3_BUCKET, Key=file_name, Body=file_data)
        file_url = f"https://{S3_BUCKET}.s3.{REGIAO}.amazonaws.com/{file_name}"
 
        logger.info(f"✅ Upload concluído! URL: {file_url}")
        logger.info("Iniciando a step_function notas")
        response_json = start_step_function(file_name)
        if isinstance(response_json, str):  # Se for string, converta para JSON
            response_json = json.loads(response_json)

        response = json.loads(response_json["body"])

        logger.info(f"fim da step_function notas:{response}")
        
        mover_arquivo(S3_BUCKET,file_name, response["forma_pgto"])        
        
        return {
            "statusCode": 200,
            "body": json.dumps({"text":response})
        }
        
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": "erro na recebe nota"})}

def start_step_function(key):
    client = boto3.client('stepfunctions')

    # ARN correto da Step Function
    state_machine_arn = "arn:aws:states:us-east-1:491085429967:stateMachine:step_function_sprint4-6"

    # Criar JSON de entrada
    input_data = {
        "key": key
    }

    response = client.start_execution(
        stateMachineArn=state_machine_arn,
        name=f"exec-{uuid.uuid4()}",  # Nome único para evitar conflitos
        input=json.dumps(input_data)  # Convertendo JSON para string
    )
    # Aguarda a conclusão da Step Function
    
    execution_arn = response["executionArn"]
    while True:
        execution_response = client.describe_execution(executionArn=execution_arn)
        status = execution_response["status"]

        if status in ["SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"]:
            break  # Sai do loop quando a execução termina
        
        time.sleep(2)  # Espera 2 segundos antes de verificar novamente

    if status == "SUCCEEDED":
        # Retorna o output final da Step Function
        output = execution_response.get("output", "")
        return output

def mover_arquivo(bucket, nome_arquivo, nova_pasta):
    logger.info(f"Movendo para a bucket correta")
    if nova_pasta.lower() =="dinheiro" or nova_pasta.lower() == "pix":
        nova_pasta ="dinheiro"
        chave_destino = f"{nova_pasta}/{nome_arquivo}"
    else:
        nova_pasta="outros"
        chave_destino = f"{nova_pasta}/{nome_arquivo}"
    

    s3_client.copy_object(
        Bucket=bucket,
        CopySource={"Bucket": bucket, "Key": nome_arquivo},
        Key=chave_destino
    )
    s3_client.delete_object(Bucket=bucket, Key=nome_arquivo)

    
    return chave_destino