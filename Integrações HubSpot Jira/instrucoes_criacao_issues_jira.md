# 🧩 Fluxo de Criação de Issues no Jira

Este módulo automatiza o processo de criação de issues (tarefas) em projetos do Jira, com base em dados provenientes do HubSpot. Ele é ideal para fluxos de onboarding, lançamentos de instâncias e configurações técnicas entre diferentes áreas.

---

## 📁 Arquivos incluídos

| Arquivo                      | Descrição                                                                 |
|------------------------------|---------------------------------------------------------------------------|
| `main_criacao_issues.py`     | Script principal. Calcula dados a partir de um negócio no HubSpot, formata descrições e cria duas issues no Jira. |
| `owner_projeto.py`           | Busca o nome do responsável (owner) de um negócio usando o ID do HubSpot. |
| `pegar_id_external_id.py`    | Consulta no Jira o ID correspondente a um valor do campo `external_id`.  |
| `dados_cliente_area.py`      | Busca dados associados a um cliente área no HubSpot, incluindo tenant, cliente e ID externo. |

---

## ⚙️ Pré-requisitos

- Conta no Jira com permissão para criar issues e consultar campos personalizados.
- Acesso à API do HubSpot com token salvo como variável de ambiente:
  - `HUBSPOT_ACCESS_TOKEN`
- Acesso à API do Jira com as seguintes variáveis de ambiente:
  - `JIRA_EMAIL`
  - `JIRA_API_TOKEN`
  - `JIRA_BASE_URL`

---

## 🔧 Personalizações necessárias

- Substituir `"customfield_XXXXX"` pelos IDs reais dos campos personalizados do seu Jira.
- Adaptar os mapeamentos de produtos e usuários na função `calcula_usuarios()`.
- Definir os nomes dos projetos Jira nos campos `"project": {"key": "XXX"}`.

---

## 🔁 Funcionamento

1. O script principal (`main_criacao_issues.py`) é acionado com dados de um negócio.
2. Ele busca os itens de linha, calcula número de usuários, formata as descrições e cria issues nos projetos de atendimento e infraestrutura.
3. Issues são relacionadas entre si por meio da função `link_issues`.
4. Os arquivos auxiliares extraem dados complementares do HubSpot e Jira.

---

## 💡 Dicas

- Use esse módulo como **ação personalizada** (custom code) em fluxos do HubSpot.
- Ideal para padronizar a criação de tarefas em onboarding ou alterações técnicas.
- As descrições das issues podem ser personalizadas diretamente no corpo do script.

---

## 🚫 Aviso de uso

> **Este projeto é genérico e educativo. Substitua os campos sensíveis por variáveis de ambiente e adapte os nomes personalizados ao seu ambiente de Jira e HubSpot.**