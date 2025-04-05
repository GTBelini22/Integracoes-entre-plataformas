function EnvioMensagens() {
  const dflistdata = readSheets_mensagens(SPREADSHEET_ID, 0)
  let data = formatSummary_mensagens(dflistdata[0])// Formatando o campo de assunto


  const dataToSend = processPlanilhaData_mensagens(data);


  if (dataToSend.length > 0) {
    // Verificando no Jira se foi dado uma estimativa de tempo para o usuário

    dataToSend.forEach(row => {
      const previsaoChamado = getDataJira_mensagens(row);
      var tempoAberto = calculoHoras_mensagens(row)

      if (previsaoChamado == null){

        if (tempoAberto== 4 ){
          // Mensagem de 4 horas de espera
        enviarEmail_mensagens(row, 4);

        }else if (tempoAberto == 8){
          // Mensagem para uma espera de 8, quase acabando
        enviarEmail_mensagens(row, 8);

        }else if (tempoAberto == 10){
          // Mensagem para o tempo igual a 10 horas,já estourado
        enviarEmail_mensagens(row, 10);
        }
      }
      else{
        Logger.log("Não realizando nenhum envio de horas, o chamado está dentro do prazo")
      }
    }
    );
  }
}

function readSheets_mensagens(id, page){
  const spreadsheet = SpreadsheetApp.openById(id);
  const sheet = spreadsheet.getSheets()[page];
  const data = sheet.getDataRange().getValues();

  return [data, sheet];
}

function formatSummary_mensagens(df){
  // Função para deixar o assunto com apenas um item em vez de 2 caso isso ocorra
  for (i=1;i<df.length;i++){
    if (df[i][10]==""){
      df[i][3] = df[i][3].split(", ")[0]
    }
  }

  return df
}

function processPlanilhaData_mensagens(data) {
  const dataTosend = [];

  for (let i = 1; i < data.length; i++) {
    const status = data[i][9];
    if (status === 'Quarentena') {
      const row = data[i].map((cell, index) => index === 5 ? cell.split(", ") : cell);
      dataTosend.push(row);
    } 
  }
  return dataTosend
}


function getDataJira_mensagens(row) {
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

function calculoHoras_mensagens(row) {
  var dataString = row[1];
  var dataInicial = new Date(dataString);
 
  // Obtenha a data e hora atuais
  var dataAtual = new Date();

   if (dataAtual.getHours()>18 && dataAtual.getHours()<9 ){
    Logger.log("Executando em horário fora do trabalho")
    return 0
  }

  // Horário de início e fim do expediente (9h às 18h)
  var horaInicio = 9;
  var horaFim = 18;

  // Função para verificar se um horário está dentro do expediente
  function isHorarioUtil(date) {
    var day = date.getDay();
    var hour = date.getHours();
    return day >= 1 && day <= 5 && hour >= horaInicio && hour < horaFim;
  }

  // Função para avançar para o próximo horário útil
  function avancarParaProximoHorarioUtil(date) {
    var day = date.getDay();
    var hour = date.getHours();

    if (hour >= horaFim) {
      // Se a hora for depois do expediente, vá para o início do próximo dia útil
      date.setDate(date.getDate() + (day == 5 ? 3 : 1)); // Pular fim de semana se necessário
      date.setHours(horaInicio, 0, 0, 0);
    } else if (hour < horaInicio) {
      // Se a hora for antes do expediente, vá para o início do expediente
      date.setHours(horaInicio, 0, 0, 0);
    }

    return date;
  }

  // Inicialize a contagem de horas úteis
  var horasUteis = 0;

  // Ajuste a data inicial para o próximo horário útil se necessário
  dataInicial = avancarParaProximoHorarioUtil(dataInicial);

  // Percorra os horários entre as duas datas
  while (dataInicial < dataAtual) {
    if (isHorarioUtil(dataInicial)) {
      // Avance uma hora e incremente a contagem de horas úteis
      dataInicial.setHours(dataInicial.getHours() + 1);
      horasUteis++;
    } else {
      // Avance para o próximo horário útil
      dataInicial = avancarParaProximoHorarioUtil(dataInicial);
    }
  }

  return horasUteis;
}


function montarMensagem(assunto,diferencaHoras) {
  // Construa a mensagem usando os dados da linha e a diferença de horas
  if (diferencaHoras == 4){
    var mensagem = `<p>A solicitação sobre <strong>${assunto}</strong> está sem previsão de conslusão há 4 horas. Por gentileza, verifique o chamado, calcule a data necessária e preencha no local apropriado para que o solicitante seja informado.</p>

    <p>Obrigado!
    Growth Ops</p>`;

  }
  else if (diferencaHoras == 8){
    var mensagem = `<p>A solicitação sobre <strong>${assunto}</strong> está sem previsão de conslusão há 8 horas. Por gentileza, verifique o chamado, calcule a data necessária e preencha no local apropriado para que o solicitante seja informado.</p>

    <p>Obrigado!
    Growth Ops</p>`;
  }
  else if (diferencaHoras == 10){
    var mensagem = `<p>A solicitação sobre <strong>${assunto}</strong> passou o prazo de 9 horas. Por gentileza, verifique o chamado, calcule a data necessária e preencha no local apropriado para que o solicitante seja informado.</p>

    <p>Obrigado!
    Growth Ops</p>`;
  }
  return mensagem;
}

function getEmail(row){
// Função para conseguir o e-mail da pessoa que é a responsável pelo chamado
  const data = readSheets(SPREADSHEET_ID, 1)[0]
  for(i=1;i<data.length;i++){
    if(data[i][0]=== row[10]){
      return data[i][2]
    }
  }
}

function enviarEmail_mensagens(dados, horas) {
  const mensagem = montarMensagem(dados[3],horas)
  var assunto = `Balcão de Atendimento - Alerta de chamado sem previsão de conclusão - ${dados[0]}`;
  const destinatario = getEmail(dados)

  MailApp.sendEmail({
    to: destinatario,
    subject: assunto,
    htmlBody: mensagem
  });
}
