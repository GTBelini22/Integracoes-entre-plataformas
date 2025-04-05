import requests
import json
import os
from datetime import datetime
from hubspot import HubSpot
from hubspot.crm.objects import ApiException


def get_associations_negocios_cliente_area(hubspot_access_token, objectId):
    """
    Retorna os IDs dos negócios (deals) associados a um cliente área no HubSpot.

    Essa função realiza uma requisição batch à API de associações do HubSpot para buscar todos os negócios
    relacionados a um objeto do tipo "cliente área".

    Args:
        hubspot_access_token (str): Token de autenticação OAuth para a API do HubSpot.
        objectId (str): ID do objeto de cliente área.

    Returns:
        list: Lista de strings contendo os IDs dos negócios associados.

    Raises:
        requests.exceptions.RequestException: Caso a requisição à API falhe.
    """
    url = "https://api.hubapi.com/crm/v3/associations/2-XXXXX/0-XXXXXX/batch/read"
    payload = json.dumps({
        "inputs": [{"id": str(objectId)}]
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {hubspot_access_token}'
    }

    try:
        response_cliente_area = requests.post(url, headers=headers, data=payload)
        response_cliente_area.raise_for_status()
        json_response_cliente_area = response_cliente_area.json().get('results', [])

        business_ids = []
        for association in json_response_cliente_area:
            if 'to' in association:
                business_ids.extend([item['id'] for item in association['to']])

        return business_ids

    except requests.exceptions.RequestException as e:
        print(f'[ERRO] Falha ao obter associações: {e}')
        return []


def get_deals_by_ids(hubspot_access_token, deal_ids):
    """
    Aplica um reajuste percentual sobre os valores dos itens de linha.

    A função itera sobre os itens agrupados por negócio e recalcula o valor de cada item aplicando
    um percentual de reajuste definido.

    Args:
        line_items (dict): Dicionário no formato {deal_id: [itens]}, onde cada item é um dict com chave 'amount'.
        adjustment_percentage (float): Percentual a ser aplicado como reajuste (ex: 10 para 10%).

    Returns:
        dict: Dicionário com a mesma estrutura de entrada, incluindo o novo campo 'new_amount' em cada item.
    """
    url = "https://api.hubapi.com/crm/v3/objects/deals/batch/read"
    headers = {
        'Authorization': f'Bearer {hubspot_access_token}',
        'Content-Type': 'application/json'
    }

    # stage - etapa do negócio - adicionar
    selected_properties = [
        "data_inicio_vigencia",
        "valor_upsell",
        "tipo_de_venda",
        "amount",
        "closedate",
        "createdate",
        "hs_lastmodifieddate",
        "hs_object_id",
        "dealstage"
    ]

    payload = json.dumps({
        "properties": selected_properties,
        "inputs": [{"id": deal_id} for deal_id in deal_ids]
    })

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        deals = response.json().get("results", [])

        # Organiza os dados no formato de dicionário de listas
        deals_data = {"negocios": []}

        for deal in deals:
            negocio = {
                "id": deal["id"],
                "amount": deal["properties"].get("amount"),
                "closedate": deal["properties"].get("closedate"),
                "createdate": deal["properties"].get("createdate"),
                "data_inicio_vigencia": deal["properties"].get("data_inicio_vigencia"),
                "hs_lastmodifieddate": deal["properties"].get("hs_lastmodifieddate"),
                "tipo_de_venda": deal["properties"].get("tipo_de_venda"),
                "valor_upsell": deal["properties"].get("valor_upsell"),
                "dealstage": deal["properties"].get("dealstage")
            }
            deals_data["negocios"].append(negocio)

        return deals_data

    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha ao obter detalhes dos negócios: {e}")
        return {"negocios": []}


def filter_two_recent_valid_deals(deals_data):
    """Filtra os dois negócios mais recentes que atendem aos critérios de tipo de venda e etapa"""
    tipos_validos = {
        "Renovação com Reajuste",
        "Reajuste"
    }
    etapas_validas = {
        "XXXXX",     # código para "Faze Assinada"
        "YYYYYY"      # código para " contrato pos Assinado"
    }

    negocios_filtrados = []

    for negocio in deals_data["negocios"]:
        tipo = negocio.get("tipo_de_venda")
        etapa = negocio.get("dealstage")
        closedate_str = negocio.get("closedate")

        if tipo in tipos_validos and etapa in etapas_validas and closedate_str:
            try:
                closedate = datetime.strptime(closedate_str[:10], "%Y-%m-%d")
                negocio["parsed_closedate"] = closedate
                negocios_filtrados.append(negocio)
            except ValueError:
                print(f"[ERRO] Data inválida para o negócio {negocio['id']}: {closedate_str}")

    # Ordena pela data de fechamento mais recente
    negocios_ordenados = sorted(negocios_filtrados, key=lambda x: x["parsed_closedate"], reverse=True)

    # Retorna apenas os dois mais recentes
    return [n["id"] for n in negocios_ordenados[:2]]


def get_line_items_from_deal(hubspot_access_token, deal_id):
    """Busca os itens de linha associados a um negócio"""
    url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}/associations/line_items"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {hubspot_access_token}'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        associations = response.json().get("results", [])
        return [item["id"] for item in associations]
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch line items for deal {deal_id}: {e}")
        return []


def get_line_item_details(hubspot_access_token, line_item_id):
    """Busca detalhes de um item de linha pelo ID"""
    url = f"https://api.hubapi.com/crm/v3/objects/line_items/{line_item_id}?properties=name,quantity,hs_product_id,amount"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {hubspot_access_token}'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch details for line item {line_item_id}: {e}")
        return None


def apply_price_adjustment(line_items, adjustment_percentage):
    """Aplica um reajuste percentual aos valores dos itens de linha"""
    updated_line_items = {}

    for deal_id, items in line_items.items():
        updated_line_items[deal_id] = []

        for item in items:
            original_amount = float(item.get("amount", 0))  
            new_amount = round(original_amount * (1 + (adjustment_percentage / 100)), 2)
            updated_item = item.copy()
            updated_item["new_amount"] = new_amount
            updated_line_items[deal_id].append(updated_item)

    return updated_line_items


# Função para adicionar os itens de linha ajustados a um novo negócio
def add_line_items_to_deal(hubspot_access_token, deal_id, updated_line_items):
    """Adiciona os itens de linha ajustados ao novo negócio no HubSpot"""
    url = "https://api.hubapi.com/crm/v3/objects/line_items"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {hubspot_access_token}'
    }

    created_items = []

    for deal_id_ref, items in updated_line_items.items():
        for item in items:
            payload = json.dumps({
                "properties": {
                    "name": item["name"],
                    "quantity": item["quantity"],
                    "price": item["new_amount"],
                    "hs_product_id": item["hs_product_id"]
                },
                "associations": [
                    {
                        "to": {"id": deal_id},  # Associa ao novo negócio
                        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 20}]  # Associação padrão de item de linha para negócio
                    }
                ]
            })

            try:
                response = requests.post(url, headers=headers, data=payload)
                response.raise_for_status()
                created_item = response.json()
                created_items.append(created_item)
                print(f"[INFO] Item de linha '{item['name']}' criado e associado ao negócio {deal_id}.")

            except requests.exceptions.RequestException as e:
                print(f"[ERRO] Falha ao criar item de linha '{item['name']}': {e}")

    return created_items

def main(event):
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    objectId = event.get('object', {}).get('objectId')
    ADJUSTMENT_PERCENTAGE = event["inputFields"]["indice_do_reajuste"]
    print(ADJUSTMENT_PERCENTAGE)

    print(f'Buscando negócios associados ao cliente área {objectId}...')

    # 1ª Etapa: Buscar IDs dos negócios associados ao cliente área
    business_ids = get_associations_negocios_cliente_area(ACCESS_TOKEN, objectId)

    if not business_ids:
        print('[INFO] Nenhum negócio associado encontrado.')
        return {"outputFields": {"negocios": [], "deals_closed_last_year": [], "line_items": {}}}

    # 2ª Etapa: Buscar propriedades dos negócios
    deals_data = get_deals_by_ids(ACCESS_TOKEN, business_ids)
    print("Dados dos Deals: ", deals_data)

    # 3ª Etapa: Filtrar os negócios com a seguinte regra:
    """
    Data de fechamento: renovação com data de fechamento mais recente
    Tipo de venda: Renovação com reajuste, Renovação com upsell, Renovação com downsell ou Reajuste
    Etapa do negócio: Proposta Assinada ou Contrato Assinado
    """
    deals_closed_recent = filter_two_recent_valid_deals(deals_data)
    print('Deals que foram filtrados: ', deals_closed_recent)

    # 4ª Etapa: Buscar os itens de linha dos negócios fechados no ano passado
    line_items_details = {}
    for deal_id in deals_closed_recent:
        line_item_ids = get_line_items_from_deal(ACCESS_TOKEN, deal_id)

        line_items_details[deal_id] = []
        for line_item_id in line_item_ids:
            details = get_line_item_details(ACCESS_TOKEN, line_item_id)
            if details:
                line_items_details[deal_id].append({
                    "name": details.get("properties", {}).get("name"),
                    "quantity": details.get("properties", {}).get("quantity", 1),
                    "hs_product_id": details.get("properties", {}).get("hs_product_id"),
                    "amount": details.get("properties", {}).get("amount")
                })

    # 5ª Etapa: Aplicar reajuste nos valores dos itens de linha
    updated_line_items = apply_price_adjustment(line_items_details, ADJUSTMENT_PERCENTAGE)
    print("Atualização dos itens de linha:", updated_line_items)

    # 6ª Etapa: Criar os itens de linha ajustados e adicioná-los ao novo negócio
    created_items = add_line_items_to_deal(hubspot_access_token=ACCESS_TOKEN, deal_id=deals_closed_recent[0] , updated_line_items=updated_line_items)
    print("Criação dos Itens de linha feita!")

    return {
        "outputFields": {
            "negocios": deals_data["negocios"],
            "Id_deals_1_e_2_mais_recente": deals_closed_recent,
            "line_items": updated_line_items
        }
    }