function mostrarNomeArquivo() {
    let input = document.getElementById('fileInput');
    let fileNameSpan = document.getElementById('fileName');
  
    if (input.files.length > 0) {
        fileNameSpan.textContent = Array.from(input.files).map(f => f.name).join(", ");
    } else {
        fileNameSpan.textContent = "Nenhum arquivo selecionado";
    }
  }
  
  
  async function enviarNota() {
      let input = document.getElementById('fileInput');
  
      if (input.files.length === 0) {
          alert("Selecione ao menos um arquivo antes de enviar!");
          return;
      }
  
      document.querySelector(".InfosNota").innerHTML = "<p>Processando notas...</p>";
  
      let respostas = [];
      let uploadPromises = Array.from(input.files).map(async (file) => {
          let reader = new FileReader();
  
          return new Promise((resolve, reject) => {
              reader.onload = async () => {
                  let base64File = reader.result.split(',')[1]; // Remove o prefixo "data:application/pdf;base64,"
  
                  let payload = { file: base64File };
                  let url = "https://gf0hs3rhm3.execute-api.us-east-1.amazonaws.com/prod/api/v1/invoice";
  
                  try {
                      let response = await fetch(url, {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify(payload)
                      });
  
                      if (!response.ok) {
                          throw new Error(`Erro ao enviar ${file.name} - CÃ³digo: ${response.status}`);
                      }
  
                      let data = await response.json();
                      console.log(`Resposta da API para ${file.name}:`, data);
  
                      let bodyData = data.response_from_aws ? data.response_from_aws.text : data.text;
  
                      resolve({ nomeArquivo: file.name, dados: bodyData });
                  } catch (error) {
                      console.error(`Erro ao enviar ${file.name}:`, error);
                      resolve({ nomeArquivo: file.name, erro: `Erro ao processar ${file.name}: ${error.message}` });
                  }
              };
              reader.readAsDataURL(file); // Converte o arquivo para Base64
          });
      });
  
      let resultados = await Promise.allSettled(uploadPromises);
  
      resultados.forEach(result => {
          if (result.status === "fulfilled") {
              respostas.push(result.value);
          } else {
              respostas.push({ nomeArquivo: "Arquivo desconhecido", erro: "Erro ao processar um dos arquivos" });
          }
      });
  
      document.querySelector(".InfosNota").innerHTML = respostas.map(res => {
          if (res.erro) {
              return `<p><strong>${res.nomeArquivo}:</strong> ${res.erro}</p>`;
          } else {
              return `<h3>Arquivo: ${res.nomeArquivo}</h3>` + formatarResposta(res.dados);
          }
      }).join("<br>");
  }
  
  
  // FunÃ§Ã£o para formatar a resposta da AWS
  function formatarResposta(responseData) {
    if (!responseData) {
      return "<p>Erro ao processar resposta</p>";
    }
  
    let {
      nome_emissor,
      endereco_emissor,
      CNPJ_emissor,
      CNPJ_CPF_consumidor,
      data_emissao,
      numero_nota_fiscal,
      serie_nota_fiscal,
      valor_total,
      forma_pgto
    } = responseData;
  
    return `
      <h3>Resposta da AWS</h3>
      <div><strong>Empresa:</strong> ${nome_emissor ?? "NÃ£o informado"}</div>
      <div><strong>CNPJ Emissor:</strong> ${CNPJ_emissor ?? "NÃ£o disponÃ­vel"}</div>
      <div><strong>EndereÃ§o:</strong> ${endereco_emissor ?? "NÃ£o disponÃ­vel"}</div>
      <div><strong>CPF/CNPJ Consumidor:</strong> ${CNPJ_CPF_consumidor ?? "NÃ£o disponÃ­vel"}</div>
      <div><strong>Data de EmissÃ£o:</strong> ${data_emissao ?? "NÃ£o disponÃ­vel"}</div>
      <div><strong>NÃºmero da NF:</strong> ${numero_nota_fiscal ?? "NÃ£o disponÃ­vel"}</div>
      <div><strong>SÃ©rie da NF:</strong> ${serie_nota_fiscal ?? "NÃ£o disponÃ­vel"}</div>
      <div><strong>Valor Total:</strong> ${valor_total ?? "NÃ£o disponÃ­vel"}</div>
      <div><strong>Forma de Pagamento:</strong> ${forma_pgto ?? "NÃ£o disponÃ­vel"}</div>
    `;
  }
  
  
  