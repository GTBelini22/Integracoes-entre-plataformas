# 📂 Extração de Dados Salesforce

Este módulo automatiza a extração de documentos vinculados a oportunidades no Salesforce, organizando os arquivos por empresa e oportunidade em pastas locais. É ideal para arquivamento, backup ou análises posteriores.

---

## 📁 Arquivos incluídos

| Arquivo              | Descrição                                                                 |
|----------------------|---------------------------------------------------------------------------|
| `Extracao.py`        | Script principal que se conecta ao Salesforce, busca oportunidades e baixa arquivos relacionados. |
| `Busca dos fields.ipynb` | Notebook auxiliar para explorar e listar os campos disponíveis em objetos do Salesforce. |
| `objects_list.ipynb` | Notebook para listar todos os objetos e suas propriedades no Salesforce. |

---

## ⚙️ Pré-requisitos

- Conta no Salesforce com permissão para acessar objetos e arquivos.
- Credenciais de autenticação válidas: `username`, `password`, `security_token`.
- Biblioteca `simple-salesforce` instalada.
- Biblioteca `pandas` e `requests` para manipulação de dados e requisições.
- Python 3.7+

---

## 🛠️ Personalizações necessárias

- Substitua as credenciais no script:
  ```python
  username = "seu_email@email.com"
  password = "sua_senha"
  security_token = "seu_token"
  ```
- O caminho base para salvamento dos arquivos pode ser ajustado:
  ```python
  base_dir = os.path.abspath('./downloads')
  ```

---

## 🔁 Funcionamento

1. Busca todas as **Oportunidades** e suas respectivas **Contas** no Salesforce.
2. Para cada oportunidade, busca os arquivos anexados via `ContentDocumentLink`.
3. Baixa os arquivos usando o endpoint de `ContentVersion`.
4. Organiza os documentos em pastas no formato:
   ```
   ./downloads/Nome_Empresa/Nome_Oportunidade_ID/arquivo.ext
   ```

---

## 🚫 Aviso de uso

> **Este projeto é um exemplo genérico. Certifique-se de adaptar as queries e campos de acordo com a estrutura do seu ambiente Salesforce.**

---

## 💡 Dica

Recomenda-se usar um ambiente virtual Python com `requirements.txt` para instalar as dependências corretamente.