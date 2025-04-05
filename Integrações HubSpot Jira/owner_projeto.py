import requests
import os
import json
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
import ast

def get_owner_name(owner_id, access_token):
    """
    Obtém o nome do proprietário no HubSpot a partir do ID do proprietário.

    :param owner_id: ID do proprietário (hubspot_owner_id).
    :param access_token: Token de acesso da API HubSpot.
    :return: Nome completo do proprietário ou mensagem de erro.
    """
    url = f'https://api.hubapi.com/owners/v2/owners/{owner_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            owner_data = response.json()
            first_name = owner_data.get('firstName', 'Unknown')
            last_name = owner_data.get('lastName', 'Unknown')
            return f"{first_name} {last_name}"
        else:
            return f"Erro: Não foi possível obter os detalhes do proprietário. Status code: {response.status_code}"
    except Exception as e:
        return f"Erro ao realizar a requisição: {e}"
      
def safe_get(input_dict, key, default=None, convert_func=None):
    """
    Função segura para acessar valores em um dicionário.
    
    Args:
        input_dict (dict): O dicionário de onde obter os valores.
        key (str): A chave do valor que você deseja acessar.
        default: Valor padrão a retornar se a chave não existir ou se ocorrer um erro.
        convert_func (function): Função opcional para converter o valor (ex: int).
        
    Returns:
        O valor associado à chave ou o valor padrão.
    """
    try:
        value = input_dict.get(key, default)
        if convert_func:
            return convert_func(value)
        return value
    except (TypeError, ValueError):
        return default

def main(event):
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    
    # Usando a função utilitária para extrair valores
    input_fields = event.get("inputFields", {})

    hubspot_owner_id = safe_get(input_fields, 'hubspot_owner_id')


    # Obtendo o nome do proprietário
    owner_name = get_owner_name(hubspot_owner_id, ACCESS_TOKEN)
    print(f"Nome do proprietário: {owner_name}")


    # Retornar as saídas no formato JSON (somente strings ou tipos serializáveis)
    return {
        "outputFields": {
          	"owner_name": owner_name
        }
    }