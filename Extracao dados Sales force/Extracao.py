import os
import requests
import re
from simple_salesforce import Salesforce
import pandas as pd

# Limite de caracteres para os nomes das pastas e arquivos (ajustável)
MAX_FILENAME_LENGTH = 50  # Diminuímos para 50 para garantir que o caminho total não ultrapasse o limite

# Lista para armazenar erros de diretório ou arquivos
erro_list = []

# Função para sanitizar nomes de pastas e arquivos e truncar se necessário
def sanitize_filename(name, max_length=MAX_FILENAME_LENGTH):
    """Sanitiza e trunca o nome do arquivo/pasta se ele for muito longo"""
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    sanitized = re.sub(r'[^\w .]', '_', sanitized)
    sanitized = re.sub(r'\s+', ' ', sanitized)
    sanitized = sanitized.strip()
    return sanitized[:max_length]  # Truncar se exceder o limite

# Definir o caminho base mais curto
base_dir = os.path.abspath('C:/downloads')  # Caminho base mais próximo da raiz
os.makedirs(base_dir, exist_ok=True)

username = "teste@email.com"
password = "xxxx"
security_token = "yyyy"


sf = Salesforce(username=username, password=password, security_token=security_token)

# Consulta SOQL para obter todas as oportunidades e suas contas relacionadas
query_opportunities = """
    SELECT Id, Name, Account.Name
    FROM Opportunity
"""

# Execute a consulta das oportunidades
result_opportunities = sf.query_all(query_opportunities)

# Preparar uma lista para armazenar os dados das oportunidades
data_opportunities = []
for record in result_opportunities['records']:
    data_opportunities.append({
        "Oportunidade_Id": record['Id'],
        "Oportunidade": record['Name'],
        "Empresa": record['Account']['Name'] if record['Account'] else "Empresa_Desconhecida"
    })

# Converter as oportunidades em um DataFrame (opcional para visualizar)
df_opportunities = pd.DataFrame(data_opportunities)

# Iterar sobre cada oportunidade e buscar os documentos
for _, oportunidade in df_opportunities.iterrows():
    oportunidade_id = oportunidade['Oportunidade_Id']
    oportunidade_nome = oportunidade['Oportunidade']
    empresa_nome = oportunidade['Empresa']

    # Sanitizar e truncar nomes para evitar problemas com caracteres inválidos e caminhos longos
    safe_empresa_nome = sanitize_filename(empresa_nome)
    safe_oportunidade_nome = sanitize_filename(oportunidade_nome)

    # Consulta SOQL para obter os ContentDocumentLinks relacionados à oportunidade
    query_content_document_link = f"""
        SELECT ContentDocumentId
        FROM ContentDocumentLink
        WHERE LinkedEntityId = '{oportunidade_id}'
    """

    # Execute a consulta para obter os ContentDocumentLinks
    result_content_document_link = sf.query_all(query_content_document_link)

    # Se houver documentos, proceder com o download
    if result_content_document_link['totalSize'] > 0:
        content_document_ids = [record['ContentDocumentId'] for record in result_content_document_link['records']]

        # Buscar detalhes dos ContentDocuments e baixar os arquivos
        for content_document_id in content_document_ids:
            query_content_version = f"""
                SELECT Id, Title, VersionData, FileExtension
                FROM ContentVersion
                WHERE ContentDocumentId = '{content_document_id}'
                ORDER BY VersionNumber DESC
                LIMIT 1
            """

            # Execute a consulta para obter a versão mais recente do ContentDocument
            result_content_version = sf.query_all(query_content_version)

            if result_content_version['totalSize'] > 0:
                content_version = result_content_version['records'][0]
                version_id = content_version['Id']
                file_name = f"{content_version['Title']}.{content_version['FileExtension']}"

                # Truncar o nome do arquivo se exceder o limite
                file_name = sanitize_filename(file_name, max_length=MAX_FILENAME_LENGTH)

                # Construir a URL para download do arquivo
                download_url = f"https://{sf.sf_instance}/services/data/v{sf.sf_version}/sobjects/ContentVersion/{version_id}/VersionData"

                # Criar as pastas da empresa e da oportunidade
                empresa_dir = os.path.join(base_dir, safe_empresa_nome)
                oportunidade_dir = os.path.join(empresa_dir, f"{safe_oportunidade_nome}_{oportunidade_id}")

                try:
                    os.makedirs(oportunidade_dir, exist_ok=True)

                    # Caminho completo para o arquivo
                    file_path = os.path.join(oportunidade_dir, file_name)

                    print(f"Baixando arquivo: {file_name} para a pasta {oportunidade_dir}")

                    # Fazer a requisição para baixar o arquivo
                    headers = {
                        'Authorization': f"Bearer {sf.session_id}"
                    }

                    response = requests.get(download_url, headers=headers)

                    if response.status_code == 200:
                        # Salvar o arquivo localmente
                        with open(file_path, 'wb') as file:
                            file.write(response.content)
                        print(f"Arquivo salvo com sucesso em: {file_path}")
                    else:
                        print(f"Erro ao baixar o arquivo. Status Code: {response.status_code}")
                        erro_list.append({
                            "Empresa": safe_empresa_nome,
                            "Oportunidade": safe_oportunidade_nome,
                            "Arquivo": file_name,
                            "Erro": f"Erro ao baixar o arquivo. Status Code: {response.status_code}"
                        })

                except Exception as e:
                    print(f"Erro ao criar diretório ou salvar o arquivo: {e}")
                    erro_list.append({
                        "Empresa": safe_empresa_nome,
                        "Oportunidade": safe_oportunidade_nome,
                        "Arquivo": file_name,
                        "Erro": str(e)
                    })
    else:
        print(f"Nenhum documento encontrado para a oportunidade: {oportunidade_nome} (ID: {oportunidade_id})")

# Exibir os erros ao final do processo
if erro_list:
    print("\nOcorreram erros nos seguintes casos:")
    for erro in erro_list:
        print(f"Empresa: {erro['Empresa']}, Oportunidade: {erro['Oportunidade']}, Arquivo: {erro['Arquivo']}, Erro: {erro['Erro']}")
else:
    print("\nTodos os arquivos foram baixados com sucesso.")
