
# 📊 Cálculo de Índices (IGPM/IPCA) e Inserção no CRM (HubSpot)

Este módulo contém dois scripts integrados com o HubSpot que permitem calcular a inflação acumulada (IGPM ou IPCA) nos últimos 12 meses e aplicar esse percentual como reajuste nos itens de linha de negócios no CRM.

---

## 📁 Arquivos incluídos

| Arquivo                        | Descrição                                                                 |
|-------------------------------|---------------------------------------------------------------------------|
| `codigo_calcula_indice.py`    | Calcula a inflação acumulada com base no índice IPCA ou IGPM e retorna os valores ajustados para o negócio. |
| `itens_de_linha_ajustados.py` | Aplica o percentual de reajuste calculado nos itens de linha dos dois negócios mais recentes do cliente no HubSpot. |

---

## ⚙️ Pré-requisitos

- Conta HubSpot com permissões de leitura e escrita para objetos de negócio (deals) e itens de linha (line_items).
- Token de acesso do HubSpot salvo em variável de ambiente: `ACCESS_TOKEN`.
- Biblioteca oficial `hubspot-api-client` instalada.
- Conexão com a API do Banco Central do Brasil (para séries temporais de inflação).

---

## 🔧 Personalizações necessárias

- Os nomes dos campos utilizados nos objetos do HubSpot (como `tipo_de_venda`, `valor_upsell`, `amount`, etc.) devem ser adaptados conforme a sua configuração.
- As etapas dos negócios válidas devem ser ajustadas na variável `etapas_validas`.
- Os tipos de venda considerados válidos para reajuste estão definidos na variável `tipos_validos` e podem ser modificados.

---

## 🔁 Funcionamento geral

### `codigo_calcula_indice.py`
1. Obtém o índice acumulado dos últimos 12 meses (IGPM ou IPCA) via API do Banco Central.
2. Calcula o novo valor com base no percentual.
3. Retorna os dados processados via `outputFields`.

### `itens_de_linha_ajustados.py`
1. Busca os negócios associados ao cliente.
2. Filtra os dois mais recentes com base em tipo de venda e etapa.
3. Obtém os itens de linha desses negócios.
4. Aplica o percentual de reajuste.
5. Cria novos itens de linha ajustados e os associa a um novo negócio.

---

## 📌 Sugestões de uso

- Ideal para automatizações de **renovação com reajuste**.
- Pode ser integrado a Workflows do HubSpot usando Webhooks ou Custom Code Actions.
- Pode ser agendado via funções externas (ex: Zapier, scripts Python, etc.).

---

## 🚫 Aviso de uso

> **Este script é um exemplo genérico. Todos os campos e nomes de propriedade devem ser validados com a estrutura atual do seu CRM antes de uso em produção.**
