import requests
import json
import os
from hubspot import HubSpot
from hubspot.crm.objects import ApiException
from datetime import datetime
import time


# Função para buscar um objeto no HubSpot pelo ID
def get_object_hubspot_by_id(api_client, object_type: str, object_id: str, properties: list = None):
    if not properties:
        # Caso não sejam especificadas propriedades, busca todas
        res = api_client.crm.properties.core_api.get_all(object_type)
        properties = [value.name for value in res.results]
    
    try:
        # Tenta buscar o objeto pelo ID
        api_response = api_client.crm.objects.basic_api.get_by_id(object_type=object_type, object_id=object_id, properties=properties, archived=False)
        return api_response
    except ApiException as e:
        print(f"Exception when calling basic_api->get_by_id: {e}")
        return None


# Função para buscar as associações entre grupo econômico e clientes áreas
def get_associations_grupo_eco_cliente_area(hubspot_access_token, objectId):
    url = "https://api.hubapi.com/crm/v3/associations/0-XXX/2-XXXX/batch/read"
    payload = json.dumps({
        "inputs": [{"id": str(objectId)}]
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {hubspot_access_token}'
    }

    try:
        # Requisição para buscar associações entre grupo econômico e cliente área
        response_cliente_area = requests.post(url, headers=headers, data=payload)
        # Converte a resposta para JSON
        json_response_cliente_area = response_cliente_area.json().get('results', [])
        return json_response_cliente_area
    except Exception as e:
        print(f'[INFO] Fail getting associations between deal and cliente area: {e}')
        raise



def main(event):
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    objectId = event.get('object', {}).get('objectId')
    api_client = HubSpot(access_token=ACCESS_TOKEN)

    # Parâmetros que queremos obter dos clientes áreas
    cliente_area_parameters = ["external_id", "tenant_name", "ps_cs_client_XXX"]

    # Buscar associações entre negócios e clientes áreas
    response = get_associations_grupo_eco_cliente_area(ACCESS_TOKEN, objectId)

    # Lista para armazenar os IDs dos clientes áreas
    if response and len(response) > 0 and 'to' in response[0]:
        listas_id_clientes_area = [i['id'] for i in response[0]['to']]
    else:
        listas_id_clientes_area = []

    if not listas_id_clientes_area:
        print(f'Nenhum cliente área encontrado na tentativa {attempt}')

    # Obter as informações de cada cliente área usando o ID
    response_cliente_area = list(map(lambda id_cliente: get_object_hubspot_by_id(api_client, "2-XXX", id_cliente, cliente_area_parameters), listas_id_clientes_area))
    external_id = response_cliente_area[0].properties['external_id']
    print(external_id)
    cliente = response_cliente_area[0].properties['ps_cs_cliente_XXX']
    print(cliente)
    tenant_name = response_cliente_area[0].properties['tenant_name']
    print(tenant_name)


    # Retornar as saídas no formato JSON (somente strings ou tipos serializáveis)
    return {
        "outputFields": {
          	"external_id": external_id,
          	"cliente_area": cliente,
          	"tenant_name": tenant_name
        }
    }
