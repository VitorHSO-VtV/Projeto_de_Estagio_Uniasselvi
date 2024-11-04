import pandas as pd
import requests
from collections import defaultdict

def group_customers_by_date(planilha_path):
    # Carrega a planilha no DataFrame
    df = pd.read_excel(planilha_path)
    
    # Agrupa os dados por 'Data de Entrega', mantendo todas as colunas para cada cliente em listas
    agrupamento = df.groupby('Data Entrega').apply(lambda x: x.to_dict(orient='records')).to_dict()
    
    return agrupamento

def get_address_info(cep):
    """Fetch address information based on the provided CEP."""
    try:
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        response.raise_for_status()  # Levanta um erro se a requisição falhar
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching address info: {e}")
        return None

def group_customers_by_cep(dictionary):
    """Group clients by delivery date, city, and neighborhood, including address info."""
    grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for date, clients in dictionary.items():
        for client in clients:
            # Importa os dados contidos nos cep
            cep = client.get('Cep')
            address_info = get_address_info(cep)

            if address_info:
                city = address_info.get('localidade')
                neighborhood = address_info.get('bairro')

                # Adiciona os dados do cliente, incluindo informações do endereço
                client_with_address = {**client, **address_info}

                # Faz a organização da planilha por cidade e bairro
                grouped_data[date][city][neighborhood].append(client_with_address)

    return dict(grouped_data)

def group_all(sheet):
    grouped_sheet = group_customers_by_date(sheet)
    grouped_sheet = group_customers_by_cep(grouped_sheet)
    return grouped_sheet