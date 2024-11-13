import json

# Conta não atendidos
def count_clients_in_nested_routes(routes):
    client_count = {}

    # Iterando sobre cada data
    for date, cities in routes.items():
        for city, districts in cities.items():
            for district, clients in districts.items():
                # Filtrando os clientes com pedido "Retorno"
                clients = [client for client in clients if client.get("pedido") != "Retorno"]
                
                # Contando clientes em cada bairro
                if date not in client_count:
                    client_count[date] = 0
                client_count[date] += len(clients)  # Adiciona a quantidade de clientes no bairro

    return client_count

# Abrir o arquivo JSON e converter em dicionário
with open("Data/clientes_nao_atendidos.json", 'r') as f:
    route = json.load(f)  # Código para não precisar criar a rota toda de novo

# Contar clientes não atendidos em cada data
client_count_nao_atendidos = count_clients_in_nested_routes(route)

# Exibir resultado de clientes não atendidos
print(f'Clientes não atendidos por data: {client_count_nao_atendidos}')

# Conta atendidos
def count_clients_in_session_routes(routes):
    client_count = {}

    # Iterando sobre cada data
    for date, sessions in routes.items():
        for session, clients in sessions.items():
            # Filtrando os clientes com pedido "Retorno"
            clients = [client for client in clients if client.get("pedido") != "Retorno"]

            # Contando clientes em cada sessão (manhã, tarde)
            if date not in client_count:
                client_count[date] = 0
            client_count[date] += len(clients)  # Adiciona a quantidade de clientes na sessão

    return client_count

# Inicializa o total de clientes atendidos
total_client_count = {}

# Itera sobre os caminhões
for truck in range(1, 4):
    # Abrir o arquivo JSON e converter em dicionário
    with open(f"Data/route_truck{truck}.json", 'r') as f:
        route = json.load(f)  # Código para não precisar criar a rota toda de novo

    # Contar clientes atendidos em cada data
    client_count_atendidos = count_clients_in_session_routes(route)

    # Exibir resultado de clientes atendidos para cada caminhão
    print(f'Clientes atendidos no caminhão {truck}: {client_count_atendidos}')

    # Somar os valores de clientes atendidos no total
    for date, count in client_count_atendidos.items():
        if date not in total_client_count:
            total_client_count[date] = 0
        total_client_count[date] += count  # Adiciona a quantidade de clientes atendidos

# Exibir resultado total de clientes atendidos
print(f'Total de clientes atendidos por data: {total_client_count}')

# Somar os clientes não atendidos e atendidos por data
for date in client_count_nao_atendidos:
    if date not in total_client_count:
        total_client_count[date] = 0

# Exibir o total de clientes processados
print(f'Total de clientes processados (atendidos + não atendidos):')
for date in total_client_count:
    total = total_client_count[date] + client_count_nao_atendidos.get(date, 0)
    print(f'{date}: {total}')





    

# Função para ler as strings de um arquivo e armazená-las em uma lista
def read_strings_from_file(filename):
    try:
        with open(filename, 'r') as file:
            # Lê todas as linhas do arquivo e remove espaços em branco extras
            input_strings = [line.strip() for line in file.readlines()]
        return input_strings
    except FileNotFoundError:
        print(f"\033[31mErro: O arquivo '{filename}' não foi encontrado.\033[0m")
        return []

def find_duplicates(filename):
    # Abre o arquivo para leitura
    with open(filename, 'r') as file:
        # Lê todas as linhas do arquivo e limpa espaços extras
        strings = [line.strip() for line in file.readlines()]
        
    seen = {}  # Dicionário para contar as ocorrências
    duplicates = []  # Lista para armazenar as strings duplicadas
    total_strings = len(strings)  # Conta o total de strings

    # Checa duplicatas
    for string in strings:
        if string in seen:
            seen[string] += 1
        else:
            seen[string] = 1

    # Identifica duplicados e os adiciona à lista
    for string, count in seen.items():
        if count > 1:
            duplicates.append((string, count))
    
    # Exibe as duplicatas
    if duplicates:
        print("Strings duplicadas encontradas:")
        for dup in duplicates:
            print(f"'{dup[0]}' apareceu {dup[1]} vezes.")
    else:
        print("Nenhuma duplicata encontrada.")

    # Exibe o número total de strings
    print(f"\nTotal de strings processadas: {total_strings}")

# Chama a função passando o nome do arquivo de entrada
find_duplicates('Test.txt')