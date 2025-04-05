# 🤖 Integrações e Automatizações

Este repositório reúne diversas integrações e automações desenvolvidas para conectar plataformas como **HubSpot**, **Jira**, **Salesforce** e serviços públicos como a **API do Banco Central**, focando na automatização de tarefas operacionais e redução de retrabalho.

---

## 📁 Estrutura do Repositório

```
├── Balcao de atendimento
├── Calculo de indices de IGPM e IPCA + Inserção no CRM
├── Extracao dados Sales force
├── Fluxo_data_renovacao
├── Integrações HubSpot Jira
```

Cada pasta contém:
- Scripts prontos para automação de processos.
- `instrucoes.md` explicando o propósito e como usar.
- `requirements.txt` com dependências da pasta.

---

## 🚀 Tecnologias e Ferramentas Utilizadas

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HubSpot](https://img.shields.io/badge/HubSpot-FF7A59?style=for-the-badge&logo=hubspot&logoColor=white)
![Jira](https://img.shields.io/badge/Jira-0052CC?style=for-the-badge&logo=jira&logoColor=white)
![Google Apps Script](https://img.shields.io/badge/Google%20Apps%20Script-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Salesforce](https://img.shields.io/badge/Salesforce-00A1E0?style=for-the-badge&logo=salesforce&logoColor=white)
![Banco Central](https://img.shields.io/badge/API%20BCB-D9B600?style=for-the-badge)

---

## 🧠 O que você encontrará

| Pasta | Descrição |
|-------|-----------|
| **Balcao de atendimento** | Scripts que integram Google Sheets com Jira para controle de chamados. |
| **Cálculo de índices + CRM** | Consulta IGPM/IPCA e atualiza valores no HubSpot com base na inflação. |
| **Extração dados Salesforce** | Automatiza download de arquivos relacionados a oportunidades do Salesforce. |
| **Fluxo_data_renovacao** | Busca a data de renovação mais antiga de clientes vinculados no HubSpot. |
| **Integrações HubSpot Jira** | Criação automatizada de issues no Jira com dados vindos do HubSpot. |

---

## 🛠️ Como usar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/seurepositorio.git
   ```

2. Navegue até a pasta desejada:
   ```bash
   cd Balcao de atendimento
   ```

3. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Siga as instruções do `instrucoes.md` de cada pasta.

---

## 🔐 Aviso de Segurança

Este projeto **não inclui tokens, senhas ou credenciais reais**. Todos os valores sensíveis foram removidos ou substituídos por `os.getenv()` para uso seguro com variáveis de ambiente.

---

## ✨ Autor

Projeto organizado por **Gustavo Belini** com foco em integrações entre plataformas SaaS e automações corporativas.