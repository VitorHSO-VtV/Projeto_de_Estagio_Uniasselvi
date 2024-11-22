import pandas as pd
import requests
from collections import defaultdict

def group_customers_by_date(sheet_path):
    # Carrega a planilha no DataFrame, forçando todos os dados a serem tratados como string
    print("\033[34mCarregando a planilha...\033[0m")  # Azul para indicar carregamento
    try:
        df = pd.read_excel(sheet_path, dtype=str)
        # Substitui valores ausentes (NaN) por strings vazias
        df.fillna("", inplace=True)
        print("\033[32mPlanilha carregada com sucesso.\033[0m")  # Verde para sucesso
    except Exception as e:
        print(f"\033[31mErro ao carregar a planilha: {e}\033[0m")  # Vermelho para erro
        return {}

    # Agrupa os dados por 'Data de Entrega', mantendo todas as colunas para cada cliente em listas
    print("\033[34mAgrupando os clientes por data de entrega...\033[0m")  # Azul para o agrupamento
    grouped = df.groupby('Data Entrega').apply(lambda x: x.to_dict(orient='records')).to_dict()
    print("\033[32mAgrupamento concluído.\033[0m")  # Verde para sucesso
    
    return grouped

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
                if client.get('N\u00b0 de pedido'):
                    print(f"\033[33mAviso: Cliente {client.get('N\u00b0 de pedido')} sem CEP, ignorando...\033[0m")  # Amarelo para aviso
                continue  # Ignora clientes sem cep
            
            address_info = get_address_info(cep)

            if address_info:
                city = address_info.get('localidade')
                neighborhood = address_info.get('bairro')
                
                # Formata o endereço completo
                numero_casa = client.get("N° Casa/Ap", "")

                address_info = {
                                    "logradouro": address_info.get('logradouro'),
                                    "bairro": neighborhood,
                                    "localidade": city,
                                    "uf": address_info.get('uf'),
                                    "cep": cep,
                                    "numero_casa": numero_casa
                                }

                client['endereco'] = build_complete_address(address_info)
                
                # Adiciona os dados do cliente, incluindo informações do endereço
                client_with_address = {**client, **address_info}

                # Faz a organização da planilha por cidade e bairro
                grouped_data[date][city][neighborhood].append(client_with_address)

    return dict(grouped_data)

def group_all(sheet):
    grouped_sheet = group_customers_by_date(sheet)
    grouped_sheet = group_customers_by_cep(grouped_sheet)
    print("\033[32mPlanilha agrupada com sucesso.\033[0m")  # Verde para sucesso
    special_clients, grouped_sheet = separate_clients(grouped_sheet)
    return special_clients, grouped_sheet

def sheet_to_dict(file_path):
    # Ler a planilha
    df = pd.read_excel(file_path)  # Para arquivos .xlsx

    # Converter para dicionário (cada linha será um dicionário)
    data_dict = df.to_dict(orient='records')

    return data_dict

def separate_clients(data):
    # Dictionaries for special and normal clients
    special_clients = {}
    normal_clients = {}
    
    # Iterate over the dates in the dictionary
    for date, cities in data.items():
        for city, neighborhoods in cities.items():
            for neighborhood, orders in neighborhoods.items():
                # Filter the orders
                for order in orders:
                    # Check the client type
                    client_type = order.get("Tipo Cliente / ESPECIAL/NORMAL", "").upper()

                    # Separate based on client type
                    if client_type == "ESPECIAL":
                        if date not in special_clients:
                            special_clients[date] = {}
                        if city not in special_clients[date]:
                            special_clients[date][city] = {}
                        if neighborhood not in special_clients[date][city]:
                            special_clients[date][city][neighborhood] = []

                        special_clients[date][city][neighborhood].append(order)
                    else:
                        if date not in normal_clients:
                            normal_clients[date] = {}
                        if city not in normal_clients[date]:
                            normal_clients[date][city] = {}
                        if neighborhood not in normal_clients[date][city]:
                            normal_clients[date][city][neighborhood] = []

                        normal_clients[date][city][neighborhood].append(order)

    return special_clients, normal_clients

def build_complete_address(address_info):
    # Lista para acumular as partes do endereço que existem
    address_parts = []

    # Adiciona cada parte do endereço se ela existir
    if address_info.get('logradouro'):
        address_parts.append(f"{address_info.get('logradouro')}")
    if address_info.get('numero_casa'):
        address_parts.append(f"{address_info.get('numero_casa')}")
    if address_info.get('bairro'):
        address_parts.append(f"{address_info.get('bairro')}")
    if address_info.get('localidade'):
        address_parts.append(f"{address_info.get('localidade')}")
    if address_info.get('uf'):
        address_parts.append(f"{address_info.get('uf')}")
    if address_info.get('cep'):
        address_parts.append(f"{address_info.get('cep')}")

    # Junta as partes do endereço com separadores apropriados
    return ", ".join(address_parts)