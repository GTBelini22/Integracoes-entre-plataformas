function AvisoDataPrevisao() {
  // Função responsável por enviar um e-mail ao pessoa que está atendendo o chamado para quando estiver se esgotando o prazo estipulado
  const dflistdata = readSheets_previsao(SPREADSHEET_ID, 0)
  const sheet = dflistdata[1]
  const data = formatSummary_previsao(dflistdata[0])// Formatando o campo de assunto

  const dataToSend = processPlanilhaData_previsao(data);


  if (dataToSend.length > 0) {
    // Verificando no Jira se foi dado uma estimativa de tempo para o usuário

    dataToSend.forEach(row => {
      let previsaoChamado = getDataJira_previsao(row);
      if (previsaoChamado == null){
        // Se ainda não foi dado nenhuma previsão apenas encerra o código
        return;
      }

      const difdias = calculoData_previsao(previsaoChamado)

        if (difdias==1){
        // Mensagem avisando que apenas resta 1 dia

        enviarEmail_previsao(row, difdias);

        // Função que atualiza o campo de Aviso previsão chamado, para ser possível enviar a mensagem final
        atualizaSheets_previsao('Não', row, sheet)

        }else if (difdias == 0){
        // Mensagem avisando que o prazo é naquele dia
        enviarEmail_previsao(row, difdias);

        // Função que atualiza o campo de Aviso previsão chamado, para ser possível enviar a mensagem final
        atualizaSheets_previsao('Não', row, sheet)


        }else if (difdias<0){
        // Mensagem avisando que o prazo expirou
        if(row[11]== 'Não'){
        enviarEmail_previsao(row, -1);

        // Função que atualiza o campo de Aviso previsão chamado, para não enviar mais a mensagem
        atualizaSheets_previsao('Sim', row, sheet)

        }else{
          Logger.log('Não é possível mais enviar a mesagem de aviso')
          }

        }
      }
    );
  }
}

function readSheets_previsao(id, page){
  const spreadsheet = SpreadsheetApp.openById(id);
  const sheet = spreadsheet.getSheets()[page];
  const data = sheet.getDataRange().getValues();

  return [data, sheet];
}

function formatSummary_previsao(df){
  // Função para deixar o assunto com apenas um item em vez de 2 caso isso ocorra
  for (i=1;i<df.length;i++){
    if (df[i][10]==""){
      df[i][3] = df[i][3].split(", ")[0]
    }
  }

  return df
}

function processPlanilhaData_previsao(data) {
  const dataTosend = [];

  for (let i = 1; i < data.length; i++) {
    const status = data[i][9];
    if (status !='Concluído' && status != 'Cancelado') {
      const row = data[i].map((cell, index) => index === 5 ? cell.split(", ") : cell);
      dataTosend.push(row);
    } 
  }
  return dataTosend
}

function getDataJira_previsao(row) {
  const headers = {
    "Authorization": "Basic " + Utilities.base64Encode(JIRA_USERNAME + ':' + JIRA_TOKEN),
    "Content-Type": "application/json"
  };

  const url = JIRA_URL_BASE + row[0];
  const options = {
    'method': 'get',
    'headers': headers,
    'muteHttpExceptions': true
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const dataJson = JSON.parse(response.getContentText());
    const dados = dataJson.fields.customfield_12943
    Logger.log(`data ->: ${dados}`);
    return dados;

  } catch (error) {
    Logger.log(`[ERROR] An error occurred: ${error.toString()}`);
    return null;
  }
}

function calculoData_previsao(dataPrevistaString) {
  // Calcula a diferença da data atual com a prevista
  // Retorna a quantidade de dias de diferença

  var partesDataPrevista = dataPrevistaString.split('-');
  var dataPrevista = new Date(partesDataPrevista[0], partesDataPrevista[1] - 1, partesDataPrevista[2]);

  // Obtenha a data atual
  var dataAtual = new Date();

  // Remova a parte da hora para comparação apenas da data
  dataPrevista.setHours(0, 0, 0, 0);
  dataAtual.setHours(0, 0, 0, 0);

  // Calcule a diferença em milissegundos
  var diferencaEmMilissegundos = dataPrevista.getTime() - dataAtual.getTime();

  // Converta a diferença de milissegundos para dias
  var umDiaEmMilissegundos = 24 * 60 * 60 * 1000;
  var diferencaEmDias = Math.round(diferencaEmMilissegundos / umDiaEmMilissegundos);

  return diferencaEmDias;
}


function atualizaSheets_previsao(atualizacao, row, sheet){
// Função para atualizar o campo de previsão com de sim ou de não

  const range = sheet.getDataRange();
  let values = range.getValues();

  for (let i = 1; i < values.length; i++) {
    if (values[i][0] === row[0] || values[i][1]===row[1]) {
      try{
        row[11] = atualizacao
      }
      catch{
        Logger.log('Itens de área já no formato string')
      }
        values[i]= row
    }
  }
  range.setValues(values);
}

function montarMensagem_previsao(dados,diferencaHoras) {
  // Construa a mensagem usando os dados da linha e a diferença em dias
  if (diferencaHoras == 1){
    var mensagem = `<p>A solicitação sobre <strong>${dados[3]}</strong>  está com previsão de conslusão para amanhã.</p>1`;

    var assunto = `Balcão de Atendimento - Alerta de chamado com apenas 1 dia para a conclusão - ${dados[0]}`;
  }
  else if (diferencaHoras == 0){
    var mensagem = `<p>A solicitação sobre <strong>${dados[3]}</strong> está com previsão de conslusão para hoje. Por favor Verificar.</p>`;

    var assunto = `Balcão de Atendimento - Previsão de entrega do chamado é hoje - ${dados[0]}`;
  }
  else if (diferencaHoras == -1){
    var mensagem = `<p>A solicitação sobre <strong>${dados[3]}</strong> passou da data prevista para entrega. Por favor verificar o chamado..</p>
`;

    var assunto = `Balcão de Atendimento - Chamado passou da previsão de entrega, por favor verificar - ${dados[0]}`;
  }
  return [mensagem, assunto];
}

function getEmail_previsao(row){
// Função para conseguir o e-mail da pessoa que é a responsável pelo chamado
  const data = readSheets(SPREADSHEET_ID, 1)[0]
  for(i=1;i<data.length;i++){
    if(data[i][0]=== row[10]){
      return data[i][2]
    }
  }
}

function enviarEmail_previsao(dados, dias) {
  const layout = montarMensagem_previsao(dados,dias)
  const mensagem = layout[0]
  const assunto = layout[1]
  const destinatario = getEmail_previsao(dados)

  MailApp.sendEmail({
    to: destinatario,
    subject: assunto,
    htmlBody: mensagem
  });
}
