# 🧾 Projeto: API REST para Processamento de Notas Fiscais com AWS

Este projeto foi desenvolvido como parte de uma avaliação prática das sprints 4, 5 e 6, e consiste em uma API para processamento de imagens de notas fiscais. Foram utilizados diversos serviços da AWS, como Lambda, S3, Textract e NLP para extração e organização dos dados. O código foi desenvolvido em Python e estruturado para rodar em um ambiente serverless, garantindo escalabilidade e eficiência no processamento.

---

## 🚀 1. Desenvolvimento da Avaliação

A API foi implementada utilizando **Python** e uma arquitetura **serverless**, aproveitando os seguintes serviços AWS:

- **AWS Lambda**: Para execução das funções em diferentes etapas do processo.
- **Amazon API Gateway**: Para expor a rota `/api/v1/invoice`.
- **Amazon S3**: Para armazenamento das imagens e arquivos processados.
- **Amazon Textract**: Para extração OCR das notas fiscais.
- **NLTK + regex heurístico**: Para identificação dos principais campos do documento.
- **Amazon Bedrock (Titan Text Premier)**: Para refinamento e formatação dos dados com IA.
- **AWS Step Functions**: Para orquestração do fluxo de processamento.
- **Amazon CloudWatch**: Para monitoramento e logging.

Essa abordagem garante escalabilidade, desempenho e modularidade.

---

## ⚙️ 2. Funcionamento do Projeto

### 🔄 Fluxo de Execução:

1. O usuário faz **upload** de uma nota fiscal via site hospedado no **Amazon S3**.
2. A imagem é armazenada no **S3**.
3. Uma **Step Function** é acionada para coordenar o processamento:
   - 🧾 **Extração de texto** via **Amazon Textract**.
   - 🧠 **Estruturação dos dados** via **NLP (NLTK + regex)**.
   - 🤖 **Refinamento com LLM** via **Titan Text Premier (Amazon Bedrock)**.
   - 📂 **Movimentação do arquivo no S3**, baseada na forma de pagamento.
4. O usuário pode visualizar os dados extraídos e refinados diretamente no site.

### 📝 Estrutura da Resposta JSON:

```json
{
  "nome_emissor": "...",
  "CNPJ_emissor": "...",
  "endereco_emissor": "...",
  "CNPJ_CPF_consumidor": "...",
  "data_emissao": "...",
  "numero_nota_fiscal": "...",
  "serie_nota_fiscal": "...",
  "valor_total": "...",
  "forma_pgto": "Dinheiro/Pix ou Cartão(Débito/Crédito)"
}
```

---

## 🛠️ 3. Deploy da Função AWS Lambda

### 🔐 Criar a Política de Permissões

1. Acesse o console do IAM: [IAM – Políticas](https://console.aws.amazon.com/iam/home#/policies)
2. Clique em **“Criar política”**
3. Vá até a aba **“JSON”**
4. Cole o conteúdo do seu arquivo `permissoes.json`
5. Clique em **“Avançar”** (duas vezes)
6. Dê um nome para a política (ex: `PermissoesLambdaNotas`)
7. Clique em **“Criar política”**

### 🚀 Criar a Função Lambda

1. Acesse o [console da AWS Lambda](https://console.aws.amazon.com/lambda)
2. Clique em **“Criar função”**
3. Escolha a opção **“Autor do zero”**
4. Preencha os campos:
   - **Nome da função**: `X` (substitua conforme necessário)
   - **Tempo de execução**: `Python 3.10`
5. Em **Permissões**, clique em **“Alterar configurações padrão de permissões”**:
   - Marque: **“Usar uma função do IAM existente ou nova”**
   - Selecione: **“Criar uma nova função com permissões básicas do Lambda”**
6. Clique em **“Criar função”**

### 🧩 Anexar a Política Criada à Função Lambda
 
1. Após a função ser criada, vá até a aba **“Permissões”**
2. Em **“Função de execução”**, clique no nome da role vinculada  
   (exemplo: `lambda-role-recebeNotasUpload-xxxx`)
3. No console do IAM, clique em **“Anexar políticas”**
4. Busque pela política que você criou (`PermissoesLambdaNotas`)
5. Marque a caixa correspondente
6. Clique em **“Anexar política”**

### 💻 Inserir Código no Lambda

1. Volte ao console da função Lambda
2. Role até a seção **“Código-fonte”**
3. Apague o conteúdo atual do arquivo padrão (`lambda_function.py`)
4. Cole o conteúdo principal da sua função Lambda
5. _(Será utilizado na extrai-dados)_ Clique em **“Adicionar arquivo”** e crie:
   - `extracao.py` → cole as funções auxiliares de extração
   - `algoritmos.py` → cole as funções de distância e fuzzy

---

## 🛠️ 4. Criando a layer para a extrai dados

**1. Carregar o Arquivo no S3**
 
Primeiro, você precisa armazenar o **arquivo-reduzido.zip** o em um bucket S3.
 
- Acesse o console da AWS e vá para **S3**.
- Crie um bucket.
- Faça o upload do arquivo **arquivo-reduzido.zip** para o bucket.
 
**2. Criar a Lambda Layer**
 
Agora, você vai criar a **Layer** para sua função Lambda.
 
- Acesse o console da AWS e vá para **Lambda**.
- No painel à esquerda, clique em **Layers** e depois em **Create layer**.
 
 **3. Configurar a Lambda Layer**
 
- No campo **Name**, dê um nome à sua Layer (por exemplo: `reduzido-layer`).
- No campo **Description**, você pode adicionar uma descrição (opcional).
- No campo **Content**, escolha a opção **Amazon S3** e forneça o **S3 URI** do arquivo **arquivo-reduzido.zip** que você carregou (exemplo: `s3://meu-bucket/arquivo-reduzido.zip`).
 
**4. Selecionar a Compatibilidade da Layer**
 
- Escolha a **versões de runtimes** selecione Python 3.8.
 
**5. Criar a Layer**
 
- Após configurar todos os campos, clique em **Create** para criar a Layer.
 
**6. Adicionar a Layer à Lambda**
 
Agora que a Layer foi criada, você precisa adicioná-la à sua função Lambda **extrai-dados**.
 
- Vá para o console da AWS e acesse **Lambda**.
- Encontre e selecione a função **extrai-dados**.
- Na aba **Layers**, clique em **Add a layer**.
- Selecione **Custom layers** e, no campo **Layer**, escolha a Layer que você acabou de criar (`reduzido-layer`).
- Escolha a versão da Layer (geralmente a mais recente) e clique em **Add**.
---
## 🔧 5. Configuração da API Gateway

1. Criar uma **API REST** no **API Gateway**.
2. Criar um **recurso** `/api/v1/invoice`.
3. Configurar um **método POST** integrado ao Lambda `recebe-nota`.
4. Habilitar **CORS**.
5. Implantar a API e obter a URL pública.

---

## 🌐 6. Hospedagem do Site no S3

**1. Acessar o Amazon S3**
- No console da AWS, busque por **S3** na barra de pesquisa ou vá até **Services** e clique em **S3** na seção de **Storage**.

**2. Criar um Bucket S3**

- Clique em **Create bucket**.
- Dê um nome único para o bucket (exemplo: `meu-site-estatico`), pois o nome do bucket deve ser globalmente único.
- Escolha a região da AWS onde o bucket será hospedado. Normalmente, escolha uma região próxima de seus usuários.
- Deixe as configurações padrão de **Bucket settings for Block Public Access** se for o caso (geralmente, os sites estáticos requerem acesso público).
- Clique em **Create** para criar o bucket.
 
**3. Carregar os Arquivos do Seu Site**

- Abra o bucket recém-criado.
- Clique em **Upload** e, em seguida, arraste e solte os arquivos do seu site (HTML, CSS, JavaScript, imagens, etc.) na área de upload.
- Clique em **Upload** para carregar os arquivos no bucket.
 
**4. Configurar o Bucket para Hospedagem de Site Estático**

- No painel do seu bucket, clique na aba **Properties**.
- Role para baixo até a seção **Static website hosting**.
- Selecione **Use this bucket to host a website**.
- Defina o **Index document** como o arquivo principal do seu site, geralmente `index.html`.
- Se desejar, defina o **Error document**, que pode ser algo como `error.html` para redirecionar os usuários a uma página de erro personalizada em caso de URL inválida.
- Clique em **Save changes** para salvar as configurações.
 
**5. Configurar Permissões para Tornar os Arquivos Públicos**

- Para tornar seu site acessível publicamente, você precisa ajustar as permissões do bucket.
- Vá para a aba **Permissions** e clique em **Bucket Policy**.
- Adicione o conteúdo do arquivo permissões dentro da pasta aws/site/permições.json
- Em seguida adicione o conteudo do arquivo aws/site/cors.json ao campo (CORS) mais abaixo na pagina
 
**6. Subindo os arquivos**

- Clique em carregar e selecione arquivo, então navegue até o arquivo public/index.html
- confirme então clique novamente em carregar e escolhe pasta então navegue até 
- public selecione a pasta static e clique em confirmar

 **7. Acessar o Site**

- Agora, você pode acessar seu site estático pelo endpoint fornecido. Basta copiar e colar o URL no seu navegador.


---

## 🛠️ 7. Como Utilizar o Sistema

1. **Acesse o site** no S3.
2. **Faça upload** da nota fiscal.
3. **Aguarde o processamento**.
4. **Veja os dados extraídos** na interface.

---

## 🌎 8. URL da API

```
https://<sua-api-id>.execute-api.us-east-1.amazonaws.com/prod/api/v1/invoice
```
> ⚠️ Substitua `<sua-api-id>` pela URL gerada no API Gateway.

---

## 📂 9. Estrutura de Pastas do Código

```
📂 aws/
├── 📂 lambdas/
│   ├── 📂 extrai-dados/
│   │   ├── 📜 algoritmos.py
│   │   ├── 📜 extracao.py
│   │   ├── 📜 lambda_extracao_nltk.py
│   │   ├── 📜 permissoes.json
│   ├── 📂 extrai-texto/
│   │   ├── 📜 extrator.py
│   │   ├── 📜 permissoes.json
│   ├── 📂 llm/
│   │   ├── 📜 lambda_llm.py
│   │   ├── 📜 permissoes.json
│   ├── 📂 recebe-notas/
│   │   ├── 📜 lambda_upload.py
│   │   ├── 📜 permissoes.json
├── 📂 step functions/
│   ├── 📜 config.json
│   ├── 📜 permissoes.json
├── 📂 site/
│   ├── 📜 cors.json
│   ├── 📜 permissoes.json

📂 dataset/
├── 📂 NFs/

📂 public/
├── 📂 static/
│   ├── 📂 css/
│   │   ├── 📜 styles.css
│   ├── 📂 js/
│   │   ├── 📜 scripts.js
├── 📂 templates/
│   ├── 📜 index.html
├── 📂 uploads/
├── 📜 api.py

📜 arquivo_reduzido.zip
📜 send_to_bucket.py
📜 README.md
```
---
## 🧠 10. Dificuldades Conhecidas

- **OCR inconsistente**: Textract pode falhar com imagens de baixa qualidade.
- **Heurística sensível a variações**: Notas fiscais variam bastante, exigindo ajustes no NLP.
- **Limites da Lambda**: Algumas bibliotecas ultrapassam o limite de 250MB.
- **Orquestração complexa**: Step Functions exigem formatos bem definidos de entrada e saída.

---

## ✍️ Autores

- Caio Dias Ferreira
   - https://github.com/DiasCaio
- Leonardo De Freitas Nogueira
   - https://github.com/leonardinfn
- Paulo César Soares Carrano
   - https://github.com/paulocarrano3
- Ricardo Menezes Guerra Pinto Bandeira
   - https://github.com/RicardoMenezesBandeira

