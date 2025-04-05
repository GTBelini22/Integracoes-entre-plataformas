# 📅 Data de Renovação - HubSpot

Este script foi desenvolvido para buscar e comparar datas de renovação de contratos associados a um grupo econômico no HubSpot. Ele identifica a **data mais antiga** entre os clientes áreas vinculados e retorna essa informação de forma formatada.

---

## 📁 Arquivo incluído

| Arquivo              | Descrição                                                                 |
|----------------------|---------------------------------------------------------------------------|
| `data_renovacao.py`  | Script que identifica a data de renovação mais antiga entre os clientes associados a um grupo econômico no HubSpot. |

---

## ⚙️ Pré-requisitos

- Conta HubSpot com acesso à API e permissões para leitura de objetos personalizados e associações.
- Token de acesso salvo como variável de ambiente: `ACCESS_TOKEN`
- Biblioteca `hubspot-api-client` instalada.
- Python 3.7 ou superior.

---

## 🔧 Personalizações necessárias

- **IDs de objetos personalizados HubSpot**:  
  No script, a URL de associação usa IDs específicos:
  ```python
  https://api.hubapi.com/crm/v3/associations/2-34070289/2-2451195/batch/read
  ```
  Esses números representam os objetos personalizados no HubSpot.  
  👉 Substitua pelos IDs do seu ambiente.

- **Propriedades utilizadas**:
  O script busca as seguintes propriedades no cliente área:
  - `"data_renovacao"` → deve ser uma data no formato `YYYY-MM-DD`.

---

## 🔁 Funcionamento

1. Recebe um evento com o ID do grupo econômico.
2. Busca os clientes associados a esse grupo.
3. Para cada cliente, extrai a data de renovação.
4. Compara as datas e retorna a mais antiga no formato `DD/MM/YYYY`.

---

## 📌 Sugestões de uso

- Ideal para fluxos de automação ou alertas sobre prazos de renovação.
- Pode ser usado como **Custom Code Action** dentro do HubSpot Workflows.

---

## 🚫 Aviso de uso

> **Este código é um exemplo genérico. As estruturas e campos devem ser adaptados conforme seu ambiente HubSpot.**