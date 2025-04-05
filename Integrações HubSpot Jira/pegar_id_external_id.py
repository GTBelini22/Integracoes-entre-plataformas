import requests
from requests.auth import HTTPBasicAuth
import json

def main(event):
  # Use entradas para obter dados de qualquer ação em seu fluxo de trabalho e use-os em seu código em vez de usar a API da HubSpot.
  external_id = event["inputFields"]["external_id"]

  
  # Substitua pelo ID ou chave do projeto que você deseja consultar
  PROJECT_KEY = "Teste"  # Exemplo de chave do projeto
  BASE_URL = "https://XXXX.atlassian.net"
  JIRA_EMAIL = "XXX@email.com"
  JIRA_API_TOKEN = "XXXX"
  NOME_CLIENTE_FIELD_ID = "customfield_XXXX"


  # Autenticação e Headers
  auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
  headers = {"Accept": "application/json"}

  # Passo 1: Obter os campos do projeto
  url_issue_types = f"{BASE_URL}/rest/api/3/project/{PROJECT_KEY}/statuses"
  response = requests.get(url_issue_types, headers=headers, auth=auth)

  if response.status_code == 200:
      issue_types = response.json()

      
      for issue_type in issue_types:
          issue_type_id = issue_type['id']
          url_fields = f"{BASE_URL}/rest/api/3/issue/createmeta?projectKeys={PROJECT_KEY}&issuetypeIds={issue_type_id}&expand=projects.issuetypes.fields"
          response_fields = requests.get(url_fields, headers=headers, auth=auth)

          if response_fields.status_code == 200:
              fields_data = response_fields.json()

              # Filtrar apenas os dados do campo 'nome_Cliente'
              for project in fields_data.get("projects", []):
                  for issuetype in project.get("issuetypes", []):
                      fields = issuetype.get("fields", {})
                      if NOME_CLIENTE_FIELD_ID in fields:
                          nome_cliente_data = fields[NOME_CLIENTE_FIELD_ID]
                          
                          # Tentar extrair os valores possíveis dentro do campo
                          allowed_values = nome_cliente_data.get("allowedValues", [])
                          for item in allowed_values:
                              if item.get("value") == external_id:
                                  print(f"O ID de '{external_id}' é {item['aid']}")
                                  break
          else:
              print(f"Falha ao obter fields para o tipo de issue {issue_type['name']}.")
  else:
      print(f"Falha ao obter tipos de issue do projeto '{PROJECT_KEY}'. Status Code: {response.status_code}")
      print("Erro:", response.text)

  print("ID do External ID - ", item['id'])

  
  return {
    "outputFields": {
      "id_external_ID_Jira": item['id']
    }
  }