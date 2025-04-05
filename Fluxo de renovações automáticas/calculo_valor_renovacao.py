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


def obter_acumulado_12_meses(codigo_serie, data_inicial, data_final):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados"
    params = {
        'formato': 'json',
        'dataInicial': data_inicial,
        'dataFinal': data_final
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        try:
            data_serie = response.json()

            for entry in data_serie:
                entry['valor'] = float(entry['valor'].replace(',', '.'))
            
            def calcular_acumulado_12_meses(data):
                resultado = []
                for i in range(len(data)):
                    if i >= 11:
                        acumulado = 1
                        for j in range(i - 11, i + 1):
                            acumulado *= (1 + data[j]['valor'] / 100)
                        acumulado = (acumulado - 1) * 100
                        resultado.append({
                            'data': data[i]['data'],
                            'evolucao_mensal': data[i]['valor'],
                            'acumulado_12_meses': round(acumulado, 2)
                        })
                    else:
                        resultado.append({
                            'data': data[i]['data'],
                            'evolucao_mensal': data[i]['valor'],
                            'acumulado_12_meses': None
                        })
                return resultado
            
            return calcular_acumulado_12_meses(data_serie)
        
        except ValueError as e:
            return f"Erro ao processar a resposta: {e}"
    else:
        return f"Erro na requisição: {response.status_code}"


def gerar_datas_serie():
    data_atual = datetime.now()
    mes_final = data_atual.month - 1
    ano_final = data_atual.year
    
    if mes_final == 0:
        mes_final = 12
        ano_final -= 1
    
    mes_inicio = mes_final
    ano_inicio = ano_final - 1

    data_inicio = f"30/{mes_inicio}/{ano_inicio}"
    data_fim = f"01/{mes_final}/{ano_final}"
    
    return data_inicio, data_fim


def realiza_calculo(indice, narr):
    valor_final = narr * (indice / 100)
    print(valor_final)
    return valor_final


def main(event):
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    objectId = event.get('object', {}).get('objectId')
    api_client = HubSpot(access_token=ACCESS_TOKEN)

    data_inicio, data_fim = gerar_datas_serie()
    valor_original = float(event["inputFields"]['Mrr_total'])
    print(f'Valor original do cliente área = {valor_original}')
    
    try:
        tipo_reajuste = str(event["inputFields"]['indice_reajuste'])
    except:
        print('Apresentou erro ao tentar buscar o indice')
        tipo_reajuste = ""
    
    print(tipo_reajuste)

    if tipo_reajuste == 'IGPM' and valor_original > 0.0:
        tentativas = 0
        max_tentativas = 3
        resultado_igpm = None

        while tentativas < max_tentativas:
            try:
                resultado_igpm = obter_acumulado_12_meses(189, data_inicio, data_fim)[-1]

                if isinstance(resultado_igpm, dict) and 'acumulado_12_meses' in resultado_igpm:
                    print('Resultado de IGPM', resultado_igpm['acumulado_12_meses'])
                    break

                raise TypeError("O valor retornado não é um dicionário válido com a chave 'acumulado_12_meses'.")

            except (TypeError, IndexError, KeyError) as e:
                tentativas += 1
                print(f"Tentativa {tentativas} falhou: {e}")

                if tentativas < max_tentativas:
                    print("Tentando novamente...")
                    time.sleep(2)

        if resultado_igpm is None or not (isinstance(resultado_igpm, dict) and 'acumulado_12_meses' in resultado_igpm):
            print("Erro: Não foi possível obter 'resultado_igpm' com a chave 'acumulado_12_meses' após 3 tentativas.")
            return

        resultado_igpm['data'] = datetime.strptime(resultado_igpm['data'], "%d/%m/%Y")
        print('Data extraída IGP-M:', resultado_igpm['data'])

        valor_com_reajuste = realiza_calculo(resultado_igpm['acumulado_12_meses'], valor_original)
        indice_final_reajuste = resultado_igpm['acumulado_12_meses']

    elif tipo_reajuste == 'IPCA' and valor_original > 0.0:
        tentativas = 0
        max_tentativas = 3
        resultado_ipca = None

        while tentativas < max_tentativas:
            try:
                resultado_ipca = obter_acumulado_12_meses(433, data_inicio, data_fim)[-1]

                if isinstance(resultado_ipca, dict) and 'acumulado_12_meses' in resultado_ipca:
                    print('Resultado de IPCA', resultado_ipca['acumulado_12_meses'])
                    break

                raise TypeError("O valor retornado não é um dicionário válido com a chave 'acumulado_12_meses'.")

            except (TypeError, IndexError, KeyError) as e:
                tentativas += 1
                print(f"Tentativa {tentativas} falhou: {e}")

                if tentativas < max_tentativas:
                    print("Tentando novamente...")
                    time.sleep(2)

        if resultado_ipca is None or not (isinstance(resultado_ipca, dict) and 'acumulado_12_meses' in resultado_ipca):
            print("Erro: Não foi possível obter 'resultado_ipca' com a chave 'acumulado_12_meses' após 3 tentativas.")
            return

        resultado_ipca['data'] = datetime.strptime(resultado_ipca['data'], "%d/%m/%Y")
        print('Data extraída IPCA:', resultado_ipca['data'])

        valor_com_reajuste = realiza_calculo(resultado_ipca['acumulado_12_meses'], valor_original)
        indice_final_reajuste = resultado_ipca['acumulado_12_meses']

    else:
        print('Nenhum tipo de reajuste indicado, mantendo o valor original!')
        valor_com_reajuste = valor_original
        indice_final_reajuste = 0

    return {
        "outputFields": {
            "return_valor_com_reajuste": valor_com_reajuste,
            "indice_do_reajuste": indice_final_reajuste,
            "forma_reajustada": tipo_reajuste
        }
    }
