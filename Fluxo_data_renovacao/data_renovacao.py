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
    url = "https://api.hubapi.com/crm/v3/associations/2-34070289/2-2451195/batch/read"
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


# Função para comparar as datas de renovação e retornar a mais antiga
def find_oldest_date(dates_list):
    if not dates_list:
        return None

    # Encontra a data mais antiga (pode ser no futuro ou passado)
    oldest_date = min(dates_list)
    return oldest_date


def main(event):
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    objectId = event.get('object', {}).get('objectId')
    api_client = HubSpot(access_token=ACCESS_TOKEN)

    # Parâmetros que queremos obter dos clientes áreas
    cliente_area_parameters = ["hs_object_id", "data_renovacao"]

    # Obter o nome do grupo econômico do evento
    nome_do_grupo_econ_mico = event["inputFields"]["nome_do_grupo_econ_mico"]

    attempt = 0  # Contador de tentativas
    max_attempts = 3  # Número máximo de tentativas
    data_escolhida_formatada = None  # Inicializar a variável da data escolhida

    while attempt < max_attempts:
        attempt += 1
        print(f'Tentativa {attempt} de {max_attempts}...')

        # Buscar associações entre grupo econômico e clientes áreas
        response = get_associations_grupo_eco_cliente_area(ACCESS_TOKEN, objectId)

        # Lista para armazenar os IDs dos clientes áreas
        if response and len(response) > 0 and 'to' in response[0]:
            listas_id_clientes_area = [i['id'] for i in response[0]['to']]
        else:
            listas_id_clientes_area = []

        if not listas_id_clientes_area:
            print(f'Nenhum cliente área encontrado na tentativa {attempt}')
            continue  # Tenta novamente se não encontrar clientes

        # Obter as informações de cada cliente área usando o ID
        response_cliente_area = list(map(lambda id_cliente: get_object_hubspot_by_id(api_client, "2-2451195", id_cliente, cliente_area_parameters), listas_id_clientes_area))

        listas_Datas = []
        # Iterar sobre os dados dos clientes áreas e extrair as datas de renovação
        for cliente_area in response_cliente_area:
            data_renovacao_nao_tratada = cliente_area.properties.get('data_renovacao')
            print(data_renovacao_nao_tratada)
            if data_renovacao_nao_tratada != None:
                listas_Datas.append(datetime.strptime(data_renovacao_nao_tratada, "%Y-%m-%d"))

        if not listas_Datas:
            print("A lista de datas está vazia, colocando a data como -")
            data_escolhida = '-'
            break

        # Comparar as datas e encontrar a data mais antiga (conforme sua descrição)
        data_escolhida = find_oldest_date(listas_Datas)

        # Se uma data válida for encontrada, converte para o formato "DD/MM/YYYY" e sai do loop
        if data_escolhida:
            data_escolhida_formatada = data_escolhida.strftime("%d/%m/%Y")
            print(f'Data encontrada: {data_escolhida_formatada}')
            break  # Sai do loop, pois encontramos a data
        else:
            print(f'Nenhuma data válida encontrada na tentativa {attempt}')
            time.sleep(2)  # Pausa entre as tentativas

    # Se após 3 tentativas não houver data válida, exibe uma mensagem
    if not data_escolhida_formatada:
        print('Nenhuma data válida encontrada após 3 tentativas.')

    # Retornar as saídas no formato JSON (somente strings ou tipos serializáveis)
    return {
        "outputFields": {
            "return_nome_do_grupo_econ_mico": nome_do_grupo_econ_mico,
            "data_renovacao_escolhida": data_escolhida_formatada,
          	"tentativas": attempt
        }
    }
