# Documentação do balcão de atendimento


![Google Apps Script](https://img.shields.io/badge/Google%20Apps%20Script-4285F4?logo=google%20apps%20script&logoColor=white)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-34A853?logo=google%20sheets&logoColor=white)
![Jira](https://img.shields.io/badge/Jira-0052CC?logo=jira&logoColor=white)
![REST API](https://img.shields.io/badge/REST%20API-02569B?logo=rest&logoColor=white)

## Descrição Geral

Estes scrips automatizam a criação, atualização e envio de alertas de Issues no Jira a partir dos dados presentes em uma planilha do Google Sheets. Ele lê os dados da planilha, cria novas Issues no Jira usando a API do Jira e atualiza a planilha com as informações obtidas do Jira. Também é responsável por criar alertas via e-mail os agentes dos chamados.


Também está presente neste repositório uma apresentação de como funciona o processo por completo.

## Estrutura do Código

Essa automação está separada em 3 códigos com funções distintas. A Seguir a função de cada código e as suas características.

### Main_atualização

Esse código é o responsável por ler a planilha e verificar se existe algum chamado que precisa ser criado dentro do Jira verificando se o status ainda está como Incluir. Além disso, ele faz a atualização dos chamados que já foram criados, ou seja, caso houver alguma alteração no chamado com o Status, prioridade ou Responsável, o código irá atualizar a planilha.

Assim, processo é executado a cada 5 minutos via a Trigger do Google Script.

### Envio das mensagens

Esse código é o responsável por enviar ao agente, que está como responsável por um chamado, um aviso de quando o prazo de 9 Horas úteis para a primeira previsão de conclusão está chegando. Em resumo, foi alinhado que a partir da criação de um chamado o agente tem 9 Horas úteis para dar uma estimativa de conclusão daquele chamado.

Dessa forma, esse processo executa a cada hora e envia um e-mail para o agente responsável quando faltar 4 Horas, 8 Horas ou quando acabar o prazo. Isso somente se não for dado um prazo, caso contrário esses avisos não ocorrerão.

### Aviso data Previsao

Esse código é o responsável por enviar ao agente, que está como responsável por um chamado, um aviso de quando a data de previsão de conclusão estiver chegando. Assim, será enviado um e-mail 1 dia antes da data colocada no chamado, no dia da entrega e um dia após a data prevista, isso se o chamado não for colocado como concluído ou Cancelado.

Com isso, esse processo roda todo inicio de dia as 8H e vai fazer essa verificação.


## Algumas das Funções

### `LeituraPlanilha`

Esta função principal coordena a leitura da planilha, a formatação dos dados, a criação de novas Issues e a atualização das Issues existentes. Ela obtém os dados da planilha, formata o campo de assunto, atualiza os responsáveis e processa os dados para identificar quais Issues precisam ser criadas ou atualizadas.

### `readSheets`

Lê os dados de uma planilha específica, incluindo o conteúdo das células e os valores exibidos, para garantir que a formatação de texto seja preservada. Retorna os dados da planilha e o objeto da própria planilha.

### `updateAssignee`

Atualiza os responsáveis pelas Issues com base em outra planilha que mapeia assuntos aos responsáveis. Esta função verifica se o campo de responsável está vazio e, em caso afirmativo, preenche-o com base na correspondência de assunto.

### `formatSummary`

Formata o campo de resumo das Issues para garantir consistência, eliminando duplicidades e mantendo apenas o primeiro item do campo, caso ele contenha múltiplos valores separados por vírgula.

### `processPlanilhaData`

Processa os dados da planilha para identificar quais Issues precisam ser criadas (com status "Incluir") e quais precisam ser atualizadas (status diferente de "Incluir" e "Concluído"). Separa os dados em dois conjuntos: um para inclusão e outro para atualização.

### `createIssueInJira`

Cria uma nova Issue no Jira usando a API do Jira. Esta função monta o payload necessário com os dados da Issue, incluindo projeto, tipo de Issue, resumo, responsável, descrição, prioridade e campos customizados. Envia uma requisição POST à API do Jira e retorna o ID da Issue criada.

### `createPayload`

Constrói o payload JSON necessário para a criação de uma Issue no Jira. Inclui informações detalhadas como o projeto, tipo de Issue, resumo, responsável, descrição, prioridade e campos customizados.

### `atualizarStatusPlanilha`

Atualiza o status das Issues na planilha com base nas informações obtidas do Jira. Esta função busca a Issue na planilha pelo ID ou pelo valor do campo e atualiza os dados da linha correspondente com as informações atuais.

### `getJiraId`

Obtém o ID do responsável pela Issue no Jira a partir de uma planilha auxiliar que mapeia nomes de responsáveis aos seus IDs do Jira.

### `getDataJira`

Obtém as informações de uma Issue existente no Jira, incluindo prioridade, status e responsável. Faz uma requisição GET à API do Jira e atualiza a linha correspondente na planilha com as informações obtidas.

### `onOpen`

Adiciona um menu personalizado na interface do Google Sheets para permitir a execução manual da função `LeituraPlanilha`. Esse menu é adicionado ao abrir a planilha, facilitando a atualização das Issues pelo usuário.