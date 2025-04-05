import requests
import os
import json
import unicodedata
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
import ast
import re


# Função para buscar itens de linha associados a um negócio
def get_line_items_from_deal(hubspot_access_token, deal_id):
    """
    Busca os itens de linha associados a um negócio (deal) no HubSpot.
    """
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


# Função para buscar detalhes de um item de linha
def get_line_item_details(hubspot_access_token, line_item_id):
    """
    Busca detalhes de um item de linha pelo ID, incluindo propriedades relevantes.
    """
    url = f"https://api.hubapi.com/crm/v3/objects/line_items/{line_item_id}?properties=name,quantity,hs_product_id"
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


# Função para calcular a data limite
def calculate_delivery_date(days_toXXd=5):
    """
    Converte o timestamp de fechamento para uma data e adiciona um número de dias.
    """
    current_date = datetime.now()  # Obtém a data e hora atuais
    new_date = current_date + timedelta(days=days_toXXd)
    return new_date.strftime("%d/%m/%Y")


def calcula_usuarios(lista_itens):
    """
    Função para calcular o número de usuários dependendo do tipo de item de linha.
    """
    usuarios_resultado = {
        "usuarios_GG": 0,
        "usuarios_10": 0,
        "usuarios_12": 0
    }

    for i in lista_itens:
        id_hubspot = lista_itens[i]['hs_product_id']
        quantidade = int(lista_itens[i].get('quantity', 1))  # Usar quantidade para multiplicar usuários, se aplicável
        print("Quantidade: ", quantidade)

        # GTM B2B2C
        if id_hubspot == '12344XX':
            usuarios_resultado["usuarios_GG"] += 2 * quantidade
            usuarios_resultado["usuarios_10"] += 5 * quantidade
        elif id_hubspot == '12344':
            usuarios_resultado["usuarios_GG"] += 2 * quantidade
            usuarios_resultado["usuarios_10"] += 5 * quantidade
        elif id_hubspot == '12344XXX':
            usuarios_resultado["usuarios_GG"] += 4 * quantidade
            usuarios_resultado["usuarios_10"] += 10 * quantidade
        elif id_hubspot == '12344XXX':
            usuarios_resultado["usuarios_GG"] += 6 * quantidade
            usuarios_resultado["usuarios_10"] += 20 * quantidade
        elif id_hubspot == '12344XXXXX':
            usuarios_resultado["usuarios_GG"] += 6 * quantidade
            usuarios_resultado["usuarios_10"] += 20 * quantidade

        # GTM B2B
        elif id_hubspot == '12344XXXX':
            usuarios_resultado["usuarios_GG"] += 10 * quantidade
            usuarios_resultado["usuarios_12"] += 20 * quantidade
        elif id_hubspot == '12344XXXX':
            usuarios_resultado["usuarios_GG"] += 10 * quantidade
            usuarios_resultado["usuarios_12"] += 20 * quantidade
        elif id_hubspot == '12344XXX':
            usuarios_resultado["usuarios_GG"] += 3 * quantidade
            usuarios_resultado["usuarios_12"] += 5 * quantidade

        # Usuários Adicionais - GTM B2B2C
        elif id_hubspot == '12344XXX':
            usuarios_resultado["usuarios_GG"] += quantidade  # Adiciona exatamente o número de unidades como usuários GTM
        elif id_hubspot == '12344XXX':
            usuarios_resultado["usuarios_10"] += quantidade  # Adiciona exatamente o número de unidades como usuários Visualizador

        # Usuários Adicionais - GTM B2B
        elif id_hubspot == '12344XXX':
            usuarios_resultado["usuarios_GG"] += 3 * quantidade  # Cada unidade representa 3 usuários GTM
        elif id_hubspot == '1234412344XXX':
            usuarios_resultado["usuarios_12"] += 5 * quantidade  # Cada unidade representa 5 usuários Lead Explorer

        # Caso o item não corresponda a nenhuma regra
        else:
            print(f"Item não reconhecido: {id_hubspot}. Nenhuma atribuição feita.")

    return usuarios_resultado

# Função para linkar duas issues no Jira
def link_issues(basic_token, issue_1, issue_2):
    url = "https://empresa.atlassian.net/rest/api/3/issueLink"
    payload = {
        "type": {"name": "Relacionada"},
        "inwardIssue": {"key": issue_1},
        "outwardIssue": {"key": issue_2}
    }
    headers = {
        "Authorization": f"Basic {basic_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    status_message = f"Link creation status: {response.status_code}, {response.text}"
    print(f'[PROJ_yyO] {status_message}')
    return status_message


def create_issue_in_project(summary_PROJ_XX, description_PROJ_XX, app_PROJ_xx ,tenant_PROJ_XX, caso_de_uso_PROJ_XX,
                            summary_PROJ_yy,description_PROJ_yy, app_PROJ_yy, 
                            data_limite_para_entrega, mrr_valor_referencial,external_id, external_id_vitally , cliente_area, url_plataforma, responsavel_negocio,
                            BASIC_TOKEN_JIRA ,n_usuarios_de_producao_total =0, n_usuarios_de_consumo_total =0,
                            team = None):
    """
    Cria uma issue no Jira para um projeto específico e retorna a chave da issue criada.

    Args:
        summary (str): Resumo da issue.
        description (str): Descrição da issue.
        project_key (str): Chave do projeto no Jira.
        issue_type_name (str): Nome do tipo de issue (e.g., Task, Bug).
        additional_fields (dict, optional): Campos adicionais personalizados. Padrão é None.

    Returns:
        str: Chave da issue criada (ex.: "PROJ-101").
    """
    # Configuração da autenticação e headers
    # JIRA_EMAIL = "usuario@empresa.com"
    # JIRA_API_TOKEN = "XXXX"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # No momento deixar como zero, sem definição
    n_casos_uso =0
    print("cliente área - Valor ->>>", cliente_area)

    payloadXX = {
        "fields": {
            "project": {"key": "PROJXX"},
            "summary": summary_PROJXX,
            "description": description_PROJXX,
            "issuetype": {"name": "Solicitação de Instância"},
            "priority": {"name": "Média"},
            "reporter": {"accountId": "XXX"},
            "customfield_XXX": {"value": app_PROJXX},
            "customfield_XXX": n_usuarios_de_producao_total,              
            "customfield_XXX": n_usuarios_de_consumo_total,               
            "customfield_XXX": n_casos_uso,                               
            "customfield_XXX": url_plataforma,  #
            "customfield_XXX": {"value": "XXXX"},                          
            "customfield_XXX":  cliente_area,                                                     
            "customfield_XXX":  data_limite_para_entrega,                 
            "customfield_XXX":  mrr_valor_referencial,                       
            "customfield_XXX":  caso_de_uso_PROJ_XX,                          
            "customfield_XXX":  tenant_PROJ_XX,                                
            "customfield_12972":  responsavel_negocio,
            "customfield_XXX": {"id": external_id_vitally}                                        
        }
    } 

    payload_yy = {
        "fields": {
            "project": {"key": "PROJ_yy"},
            "summary": summary_PROJ_yy,
            "description": description_PROJ_yy,
            "issuetype": {"name": "Task"},
            "priority": {"name": "Média"},
            "reporter": {"accountId": "XXXX"},
            "customfield_XXX": team,
            "customfield_XXX": {"value": app_PROJ_yy},
            "customfield_XXX": {"value": "ValorGenérico"},
            "customfield_XXX" : cliente_area,       #Cliente área
            "customfield_XXX" : external_id
          	# "customfield_XXX": {"id": external_id}#External ID
        }
    }
        
    # Criar issues no Jira e enviar mensagens ao Slack
    jira_responses = [
       	create_jira_task(BASIC_TOKEN_JIRA, payload_XX),
        create_jira_task(BASIC_TOKEN_JIRA, payload_yy)
    ]
    
    print("Status code PROJ_XX ", jira_responses[0].status_code)
    print("Status code PROJ_yy ", jira_responses[1].status_code)

    # Converter a string em um dicionário
    data_dictXX = ast.literal_eval(jira_responses[0].text)
    data_dict_yy = ast.literal_eval(jira_responses[1].text)

    #Validação do Sucesso da criação dos tickets 
    if jira_responses[0].status_code >=200 and jira_responses[0].status_code< 300: sucesso_PROJ_XX= True
    else: sucesso_PROJ_XX= False

    if jira_responses[1].status_code >=200 and jira_responses[0].status_code< 300: sucesso_PROJ_XXYY= True
    else: sucesso_PROJ_XXYY= False


    if sucesso_PROJ_XX: ticket_XX = data_dict_xx['key']
    else: ticket_XX =False

    if sucesso_PROJ_XX: ticket_PROJ_XX = data_dict_yy['key']
    else: ticket_PROJ_XX =False

    print("Sucesso XX:-->>", sucesso_XXX)
    print("Sucesso  YYY:-->>", sucesso_YYY)

    print("resposta Jira XXX:-->>", ticket_XXX)
    print("resposta Jira YYY:-->>", ticket_YYY)


    return [sucesso_PROJ_XX, sucesso_PROJ_XX, ticketXX, ticket_PROJ_yy]


# Função para criar uma tarefa no Jira
def create_jira_task(JIRA_API_TOKEN, payload):
    url = "https://empresa.atlassian.net/rest/api/2/issue"
    headers = {
        'Authorization': f'Basic {JIRA_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200 and response.status_code != 201:
        print(f'[ERROR] Jira task creation failed: {response.status_code} - {response.text}')
    else:
        print(f'[PROJ_yyO] Jira task creation status: {response.status_code} - {response.json()}')
    return response


def get_oferta_name(cliente, cliente_oferta):
    """
    Retorna o nome da oferta esperado pelo Jira com base no cliente fornecido.

    Args:
        cliente (str): Nome do cliente recebido da aplicação.

    Returns:
        str: Nome da oferta para o Jira, ou None se não for encontrado.
    """
    oferta_name = cliente_oferta.get(cliente)
    if not oferta_name:
        print(f"Cliente '{cliente}' não encontrado no mapeamento.")
        return None
    return oferta_name


def formatar_itens_linhas(itens):
    """
    Formata os nomes dos itens de linha em uma lista legível.

    Args:
        itens (dict): Dicionário contendo os itens de linha.

    Returns:
        str: String formatada com os nomes dos itens.
    """
    # Verifica se 'itens' é um dicionário
    if not isinstance(itens, dict):
        raise TypeError(f"Esperado um dicionário de itens, mas foi recebido: {type(itens)}")

    # Filtra e formata os itens com a chave 'name'
    itens_formatados = []
    for key, value in itens.items():
        if isinstance(value, dict) and 'name' in value:
            itens_formatados.append(f"  - {value['name']}")
        else:
            print(f"Aviso: item ignorado (não é um dicionário válido ou falta a chave 'name'): {value}")

    return "\n" + "\n".join(itens_formatados)


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


# Função para linkar duas issues no Jira
def link_issues(basic_token, issue_1, issue_2):
    url = "https://empresa.atlassian.net/rest/api/3/issueLink"
    payload = {
        "type": {"name": "Relacionada"},
        "inwardIssue": {"key": issue_1},
        "outwardIssue": {"key": issue_2}
    }
    headers = {
        "Authorization": f"Basic {basic_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    status_message = f"Link creation status: {response.status_code}, {response.text}"
    print(f'[PROJ_yyO] {status_message}')
    return status_message

# Função principal
def main(event):
    """
    Função principal para buscar os itens de linha associados a um negócio
    e criar issues no Jira para PROJXX e PROJ_yy com as yyormações relevantes.
    """
    ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
    BASIC_TOKEN_JIRA = os.getenv("BASIC_TOKEN_JIRA")
    deal_id = event.get("object", {}).get("objectId")

    yy_team = "XXX"  # Valor para Team/Equipe


    # Usando a função utilitária para extrair valores
    input_fields = event.get("inputFields", {})

    nome_empresa = safe_get(input_fields, 'nome_empresa')
    mrr = safe_get(input_fields, 'mrr')
    casos_de_uso = safe_get(input_fields, 'casos_de_uso')
    nome_da_empresa__plataforma_ = safe_get(input_fields, 'nome_da_empresa__plataforma_')
    data_fechamento = safe_get(input_fields, 'data_fechamento', default=0, convert_func=int)
    app = safe_get(input_fields, 'app')
    cliente_area = safe_get(input_fields, 'cliente_area')
    external_id = safe_get(input_fields, 'external_id')
    external_id_jira = safe_get(input_fields, 'external_id_jira')
    tenant_name = safe_get(input_fields, 'tenant_name')
    owner_name = safe_get(input_fields, 'owner_name')
    descricao_do_projeto = safe_get(input_fields, 'descricao_do_projeto')

    if nome_da_empresa__plataforma_ == None: nome_da_empresa__plataforma_ = 'Nome nao yyormado'

    # Remover caracteres especiais e ajustar o formato
    # Normalizar a string para decompor caracteres acentuados
    nome_normalizado = unicodedata.normalize('NFD', nome_da_empresa__plataforma_)
    # Remover os acentos mantendo apenas caracteres ASCII
    nome_sem_acentos = ''.join(c for c in nome_normalizado if unicodedata.category(c) != 'Mn')

    nome_limpo = re.sub(r'[^a-zA-Z0-9\s]', '', nome_sem_acentos)  # Remove caracteres especiais
    nome_formatado = nome_limpo.replace(' ', '').lower()  # Substitui espaços por '-' e converte para minúsculas

    # Criar a URL
    url_plataforma = f"https://{nome_formatado}.dominio.com"

    print(url_plataforma)

    # Exemplo de como os valores serão tratados
    print("Nome Empresa:", nome_empresa)
    print("MRR:", mrr)
    print("Casos de uso:", casos_de_uso)
    print("Nome da empresa (plataforma):", nome_da_empresa__plataforma_)
    print("Data Fechamento:", data_fechamento)
    print("App:", app)
    print("Cliente:", cliente_area)
    print("External ID:", external_id)
    print("ID External ID:", external_id_jira)
    print("Tenant Name:", tenant_name)
    print('URL da platadorma: ',url_plataforma )
    print('Owner do negócio: ',owner_name)
    print('Descrição do Projeto: ', descricao_do_projeto)

    # Calcular a data limite de entrega
    data_limite_entrega = calculate_delivery_date()
    print("Data Limite para a Entrega (atual + 5 dias):", data_limite_entrega)
    
    # Converter para o formato yyyy-MM-dd
    data_limite_entrega = datetime.strptime(data_limite_entrega, "%d/%m/%Y").strftime("%Y-%m-%d")

    if not deal_id:
        return {"outputFields": {"error": "No deal ID provided."}}

    # Buscar os IDs dos itens de linha associados ao negócio
    line_item_ids = get_line_items_from_deal(ACCESS_TOKEN, deal_id)

    if not line_item_ids:
        return {"outputFields": {"deal_id": deal_id, "line_items": {}}}
    

    # Construir dicionário com os detalhes dos itens de linha
    line_items_details = {}
    for idx, line_item_id in enumerate(line_item_ids):
        details = get_line_item_details(ACCESS_TOKEN, line_item_id)
        if details:
            line_items_details[idx] = {
                "name": details.get("properties", {}).get("name"),
                "quantity": details.get("properties", {}).get("quantity", 1),
                "hs_product_id": details.get("properties", {}).get("hs_product_id")
            }   


    n_usuarios = calcula_usuarios(line_items_details)
    line_items_details = formatar_itens_linhas(line_items_details)


    # Criar payload para PROJXX
    ad_description = f"""
    Solicitamos criação da plataforma para o cliente: {nome_empresa}.
    Data limite para entrega: {data_limite_entrega}.
    MRR: {mrr}.
    Casos de uso: {casos_de_uso}.
    Descrição do Projeto: {descricao_do_projeto}
    Cliente área : {cliente_area}
    Nome da empresa (Plataforma): {nome_da_empresa__plataforma_}.
    Itens de Linha : {line_items_details}.
    Usuários calculados: {json.dumps(n_usuarios, indent=4)}.
    URL da plataforma: {url_plataforma}
    """

    # Criar payload para PROJ_yy
    yy_description = f"""
    Solicitamos a criação de acesso SSO para o cliente: {nome_empresa}.
    Data limite para entrega: {data_limite_entrega}.
    MRR: {mrr}.
    Casos de uso: {casos_de_uso}.
    Nome da empresa (Plataforma): {nome_da_empresa__plataforma_}.
    Itens de Linha: {line_items_details}.
    Usuários calculados: {json.dumps(n_usuarios, indent=4)}.
    """

    cliente_oferta_auxiliar = {
        "escola": "esc",
        "predio": "pr",
    }

    cliente_oferta_padraoXXXXx = {
        "escola": "esc",
        "predio": "pr",
    }



    n_usuarios_consumo = n_usuarios['usuarios_10'] + n_usuarios['usuarios_12']	
    if (data_limite_entrega!= None and mrr != None and casos_de_uso!=None and url_plataforma !=None) and (n_usuarios_consumo>0 or n_usuarios['usuarios_GG'] >0) or  app == 'pr':
        campos_preenchidos = True
        ad_oferta = get_oferta_name(app, cliente_oferta_padrao)
        yy_oferta = get_oferta_name(app, cliente_oferta_auxiliar)

        # Criação dos assuntos
        ad_summary = f"Criação - {nome_empresa}"
        yy_summary = f"Lançamento - {nome_empresa}"
        yy_esteira = "XXX"  # Valor para Esteira de Desenvolvimento


        resposta_criacao = create_issue_in_project(summary_PROJXX= ad_summary, description_PROJXX= ad_description, app_PROJXX= ad_oferta, tenant_PROJXX= tenant_name, caso_de_uso_PROJXX= casos_de_uso,
                                summary_PROJ_yy= yy_summary, description_PROJ_yy= yy_description, app_PROJ_yy= yy_oferta, 
                                data_limite_para_entrega= data_limite_entrega, mrr_valor_referencial= mrr, external_id= external_id, external_id_vitally= external_id_jira, cliente_area= cliente_area, responsavel_negocio= owner_name,
                                BASIC_TOKEN_JIRA= BASIC_TOKEN_JIRA,n_usuarios_de_producao_total= n_usuarios['usuarios_GG'] ,n_usuarios_de_consumo_total=n_usuarios_consumo,
                                team=yy_team, url_plataforma= url_plataforma)
        
        successXX = resposta_criacao[0]
        success_yy = resposta_criacao[1]
        id_ticketXX = resposta_criacao[2]
        id_ticket_PROJ_yy = resposta_criacao[3]

        link_status = link_issues(BASIC_TOKEN_JIRA, id_ticketXX, id_ticket_PROJ_yy)

        print(link_status)
    else:
        print("Não foi criado as issues por conta da falta de campos preenchidos ------")
        campos_preenchidos = False
        successXX = False
        success_yy = False
        id_ticketXX = ''
        id_ticket_PROJ_yy = ''


    # Retorno final
    return {
        "outputFields": {
            "data_limite_entrega": data_limite_entrega,
            "mrr": mrr,
            "nome_empresa": nome_empresa,
            "line_items": line_items_details,
          	"n_usuarios": n_usuarios,
            "successXX": successXX,
            "success_yy": success_yy,
            "id_ticketXX": id_ticketXX,
            "id_ticket_yy": id_ticket_PROJ_yy,
            'campos_preenchidos': campos_preenchidos
        }
    }
