import pandas as pd
import requests
from collections import defaultdict

def group_customers_by_date(planilha_path):
    # Carrega a planilha no DataFrame, forçando todos os dados a serem tratados como string
    print("\033[34mCarregando a planilha...\033[0m")  # Azul para indicar carregamento
    try:
        df = pd.read_excel(planilha_path, dtype=str)
        print("\033[32mPlanilha carregada com sucesso.\033[0m")  # Verde para sucesso
    except Exception as e:
        print(f"\033[31mErro ao carregar a planilha: {e}\033[0m")  # Vermelho para erro
        return {}

    # Agrupa os dados por 'Data de Entrega', mantendo todas as colunas para cada cliente em listas
    print("\033[34mAgrupando os clientes por data de entrega...\033[0m")  # Azul para o agrupamento
    agrupamento = df.groupby('Data Entrega').apply(lambda x: x.to_dict(orient='records')).to_dict()
    print("\033[32mAgrupamento concluído.\033[0m")  # Verde para sucesso
    
    return agrupamento

def get_address_info(cep):
    """Fetch address information based on the provided CEP."""
    try:
        print(f"\033[33mBuscando informações para o CEP: {cep}\033[0m")  # Amarelo para indicar busca
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        response.raise_for_status()  # Levanta um erro se a requisição falhar
        print(f"\033[32mInformações encontradas para o CEP {cep}.\033[0m")  # Verde para sucesso
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"\033[31mErro ao buscar informações do endereço para o CEP {cep}: {e}\033[0m")  # Vermelho para erro
        return None

def group_customers_by_cep(dictionary):
    """Group clients by delivery date, city, and neighborhood, including address info."""
    grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for date, clients in dictionary.items():
        for client in clients:
            # Importa os dados contidos nos cep
            cep = client.get('Cep')
            if not cep:
                print(f"\033[33mAviso: Cliente sem CEP, ignorando...\033[0m")  # Amarelo para aviso
                continue  # Ignora clientes sem cep
            
            address_info = get_address_info(cep)

            if address_info:
                city = address_info.get('localidade')
                neighborhood = address_info.get('bairro')
                
                # Formata o endereço completo
                numero_casa = client.get("N° Casa/Ap", "")
                endereco_completo = f"{address_info.get('logradouro')}, {numero_casa} - {neighborhood}, {city} - {address_info.get('uf')}, {address_info.get('cep')}"
                client['endereco'] = endereco_completo
                
                # Adiciona os dados do cliente, incluindo informações do endereço
                client_with_address = {**client, **address_info}

                # Faz a organização da planilha por cidade e bairro
                grouped_data[date][city][neighborhood].append(client_with_address)

    return dict(grouped_data)

def group_all(sheet):
    grouped_sheet = group_customers_by_date(sheet)
    grouped_sheet = group_customers_by_cep(grouped_sheet)
    print("\033[32mPlanilha agrupada com sucesso.\033[0m")  # Verde para sucesso
    return grouped_sheet