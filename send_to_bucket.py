import base64
import requests

# Caminho da imagem que será enviada
image_path = r"C:\Users\ricar\OneDrive\Imagens\wallpaper\596583.jpg"

# Codificar a imagem em Base64
with open(image_path, "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

# Montar o payload para a API
payload = {"file": base64_image}

# URL da API
url = "https://gf0hs3rhm3.execute-api.us-east-1.amazonaws.com/prod/api/v1/invoice"

# Cabeçalhos (caso precise de autenticação, adicione aqui)
headers = {"Content-Type": "application/json"}

# Enviar a requisição POST
response = requests.post(url, json=payload, headers=headers)

# Exibir a resposta da API
print(response.status_code)
print(response.json())
