
# 🧾 Balcão de Atendimento - Integrações Google Sheets + Jira

Este conjunto de scripts foi criado para automatizar a gestão de chamados de atendimento, integrando planilhas do Google Sheets com a API do Jira. A solução é utilizada para:

- Criar novos tickets no Jira a partir de dados da planilha.
- Atualizar o status dos chamados com base no retorno do Jira.
- Enviar notificações por e-mail aos responsáveis quando prazos estão se aproximando ou foram excedidos.

---

## 📁 Arquivos incluídos

| Arquivo                     | Descrição                                                                 |
|----------------------------|---------------------------------------------------------------------------|
| `Main_atualização.js`      | Lê a planilha principal, cria ou atualiza issues no Jira.                 |
| `Aviso data Previsao.js`   | Envia alertas por e-mail com base na data de previsão de entrega.         |
| `Envio das mensagens.js`   | Envia lembretes se o chamado não tiver prazo estimado e tempo estiver avançando. |

---

## ⚙️ Pré-requisitos

Para usar estes scripts, é necessário:

- Ter uma conta no **Google Workspace** com acesso ao Google Apps Script.
- Ter um projeto no **Jira** configurado.
- Acesso a uma ou mais planilhas no **Google Sheets** contendo os dados dos chamados.
- Informar:
  - `SPREADSHEET_ID` da(s) planilha(s)
  - `JIRA_USERNAME` (e-mail do usuário)
  - `JIRA_TOKEN` (token de autenticação)
  - `JIRA_URL_BASE` (endereço da instância Jira)

---

## 🛠️ Personalizações necessárias

Antes de usar:

- Substitua todos os valores `'XXX'` nos arquivos pelos dados corretos do seu ambiente (IDs, e-mails, tokens etc).
- Certifique-se de que os nomes e índices de colunas nas planilhas estejam de acordo com os utilizados nos scripts.
- Ajuste o campo `"project": { "key": "PROJ" }` para o código real do seu projeto Jira.

---

## ✉️ Envio de e-mails

Os e-mails são enviados automaticamente usando o serviço do Google Apps Script (`MailApp.sendEmail`). As mensagens podem ser personalizadas nas funções `montarMensagem`, `montarMensagem_previsao`, etc.

---

## 📌 Sugestões de uso

- Execute os scripts manualmente ou agende com `gatilhos` do Google Apps Script para rodar automaticamente (por exemplo, a cada 15 minutos).
- Use logs (`Logger.log`) para depuração.
- Você pode adicionar um menu personalizado na planilha com a função `onOpen()`.

---

## 🚫 Aviso de uso

> **Este script é um exemplo genérico e não inclui dados sensíveis. Certifique-se de adaptar tudo ao seu ambiente antes de utilizá-lo em produção.**
