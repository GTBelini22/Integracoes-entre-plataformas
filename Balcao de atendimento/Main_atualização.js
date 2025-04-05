// Declarando as variáveis
const SPREADSHEET_ID = 'XXX';
const SPREADSHEET_ID2 = 'XXX';
const JIRA_URL_BASE = 'https://XXX.atlassian.net/rest/api/3/issue/';
const JIRA_USERNAME = 'XXX@exemplo.com';
const JIRA_TOKEN = 'Jira token';
const keyRegex = /"key":"(teste-\d+)"/;


function LeituraPlanilha() {
  const dflistdata = readSheets(SPREADSHEET_ID, 0)
  const sheet = dflistdata[1]
  let data = formatSummary(dflistdata[0])// Formatando o campo de assunto
  data = updateAssignee(data)
  
  const processData = processPlanilhaData(data);
  const dataToInclude = processData[0]
  const dataToUpdate = processData[1];

  if (dataToInclude.length > 0) {
    // Inserindo as informações dos itens novos
    dataToInclude.forEach(row => {
      row[0] = createIssueInJira(row);
      row[10] = "Quarentena";
      atualizarStatusPlanilha(row, sheet);
    });
  }

  if (dataToUpdate.length > 0) {
    // Atualizando informações com dados do Jira
    dataToUpdate.forEach(row => {
      const updatedRow = getDataJira(row);
      if (updatedRow !== null){
        atualizarStatusPlanilha(updatedRow, sheet);
      }
      else{
        Logger.log("Busca retornando vazio! Issue foi excluida")
      }
    });
  }
}

function readSheets(id, page){
  const spreadsheet = SpreadsheetApp.openById(id);
  const sheet = spreadsheet.getSheets()[page];
  const data = sheet.getDataRange().getValues();

 // Ler a coluna 2 como texto
  const textColumn = sheet.getRange(1, 2, sheet.getLastRow(), 1).getDisplayValues();
  // Substituir a coluna 2 nos dados originais
  for (let i = 0; i < data.length; i++) {
    data[i][1] = textColumn[i][0];
  }
  
  return [data, sheet];
}

function updateAssignee(dfData){
  // Realiza um procv nas planilhas para encontrar quando o assunto corresponde ao responsável
  const dfDataSla = readSheets(SPREADSHEET_ID2, 0)[0]

  for(i=1;i<dfData.length; i++){
    if(dfData[i][11]=== ""){
      for(x=1; x<dfDataSla.length; x++){
        if(dfDataSla[x][0] === dfData[i][3] || dfData[i][3] ==="teste balcão"){
          dfData[i][11] = dfDataSla[x][1]
          dfData[i][8] = dfDataSla[x][2]
           Logger.log(`Valores de DFData8: ${dfData[i][8]}`);
        }
      }
    }
  }
  return dfData
}

function formatSummary(df){
  // Função para deixar o assunto com apenas um item em vez de 2 caso isso ocorra
  for (i=1;i<df.length;i++){
    if (df[i][11]==""){
      df[i][3] = df[i][3].split(", ")[0]
    }
  }

  return df
}

function processPlanilhaData(data) {
  const dataToInclude = [];
  const dataToUpdate = [];
  for (let i = 1; i < data.length; i++) {
    const status = data[i][10];
    if (status === 'Incluir') {
      const row = data[i].map((cell, index) => index === 5 ? cell.split(", ") : cell);
      dataToInclude.push(row);
    } else if (status !== 'Incluir' && status !== "Concluído") {
      const row = data[i].map((cell, index) => index === 5 ? cell.split(", ") : cell);
      dataToUpdate.push(row);
    }
  }
  return [dataToInclude, dataToUpdate];
}

function createIssueInJira(row) {
  const headers = {
    "Authorization": "Basic " + Utilities.base64Encode(JIRA_USERNAME + ':' + JIRA_TOKEN),
    "Content-Type": "application/json"
  };

  const url = 'https://XXXX-jira.atlassian.net/rest/api/3/issue'; // URL base para criar issue
  const payload = createPayload(row);
  const options = {
    'method': 'post',
    'headers': headers,
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    Logger.log(`[INFO] Response status code: ${response.getResponseCode()}`);
    Logger.log(`[INFO] Response content: ${response.getContentText()}`);
    const resposta = (response.getContentText()).match(keyRegex)
    return resposta[1]
  } 
    catch (error) {
    Logger.log(`[ERROR] An error occurred: ${error.toString()}`);
  }
}

function createPayload(row) {
  const areasFormatadas = row[5].map(area => ({ "value": area.trim() }));
  const id = getJiraId(row[11])
  return {
    "fields": {
      "project": {
        "key": "OPS"
      },
        "issuetype": {
        "id": "10100"
      },
      "summary": row[3], 
      "assignee": {
        "accountId": id
      },
      "description": {
        "type": "doc",
        "version": 1,
        "content": [
          {
            "type": "paragraph",
            "content": [
              {
                "text": row[4],
                "type": "text"
              }
            ]
          }
        ]
      },
      "reporter": {
        "accountId": "XXXX"
      },
      "priority": {
        "id": "3"
      },
      "customfield_12787": areasFormatadas,
      "customfield_12785": {
        "value": row[8]
      },
      "customfield_12983": { //Oferta
        "value": row[6]
      },
      "customfield_12939": row[2]
    }
  };
}

function atualizarStatusPlanilha(data, sheet) {
  const range = sheet.getDataRange();
  let values = range.getValues();

  // Ler a coluna 2 como texto
  const textColumn = sheet.getRange(1, 2, sheet.getLastRow(), 1).getDisplayValues();
  // Substituir a coluna 2 nos dados originais
  for (let i = 0; i < values.length; i++) {
    values[i][1] = textColumn[i][0];
  }

  for (let i = 1; i < values.length; i++) {
    if (values[i][0] === data[0] || values[i][1]===data[1]) {
      try{
        data[5] = data[5].join(', ');
      }
      catch{
        Logger.log('Itens de área já no formato string')
      }
        values[i]= data
    }
  }
  range.setValues(values);
}

function getJiraId(personAssignee){
  // Apenas pega o ID da pessoa responsável
  const data = readSheets(SPREADSHEET_ID, 1)[0]
  for(i=1;i<data.length;i++){
    if(data[i][0]=== personAssignee){
      return data[i][1]
    }
  }
}

function getDataJira(row) {
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
    row[9] = dataJson.fields.priority.name;
    row[10] = dataJson.fields.status.name;
    row[11] = dataJson.fields.assignee ? dataJson.fields.assignee.displayName : "Sem Responsável";
    return row;
  } catch (error) {
    Logger.log(`[ERROR] An error occurred: ${error.toString()}`);
    return null;
  }
}

function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Atualizações Jira')
    .addItem('Atualizar Issues', 'LeituraPlanilha')
    .addToUi();
}
