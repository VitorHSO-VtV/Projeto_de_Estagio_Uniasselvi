import requests
import pandas as pd
from datetime import timedelta, datetime

# Função para obter a duração da viagem entre dois locais
def get_travel_time(origin, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        'origin': origin,
        'destination': destination,
        'key': "AIzaSyAiz3yZErbSg6BIfKfve8YmskYu46ekeTs",  # Substitua pela sua chave de API
        'mode': 'driving'
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK':
                # Extrai a duração da viagem em segundos
                duration_value = data['routes'][0]['legs'][0]['duration']['value']
                duration_in_hours = duration_value / 3600  # Converte segundos para horas
                print(f"\033[32mDuração da viagem entre {origin} e {destination}: {duration_in_hours:.2f} horas.\033[0m")
                return duration_in_hours
            else:
                print(f"\033[33mAviso: API retornou status {data['status']} para a solicitação de {origin} a {destination}.\033[0m")
        else:
            print(f"\033[31mErro na requisição para {origin} a {destination}. Código de status: {response.status_code}.\033[0m")
    
    except requests.exceptions.RequestException as e:
        print(f"\033[31mErro na requisição: {e}\033[0m")

    return None

# Função para criar rotas otimizadas para múltiplos dias
def make_best_routes(grouped_clients, starting_point):
    routes = {}

    # Obter as datas para os próximos três dias
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime("%m/%d/%Y") for i in range(-1, 2)]

    # Criar rotas para cada dia
    for delivery_date in dates:
        print(f"\033[34mCriando rota para o dia: {delivery_date}\033[0m")  # Azul para indicar a criação da rota
        route = []
        unvisited_clients = []
        visited_orders = set()  # Conjunto para armazenar os números de pedido já visitados

        # Extrair clientes da data específica
        if delivery_date in grouped_clients:
            for city, districts in grouped_clients[delivery_date].items():
                for district, clients in districts.items():
                    unvisited_clients.extend(clients)  # Adiciona todos os clientes à lista

        # Se não houver clientes para esse dia, ignore a criação da rota
        if not unvisited_clients:
            print(f"\033[33mNão há clientes para o dia {delivery_date}. Ignorando a criação de rota.\033[0m")
            continue  # Ignora a criação da rota para este dia

        # Início da rota
        current_location = starting_point
        total_travel_time = timedelta(0)

        # Adiciona o ponto de partida como o primeiro endereço na rota
        route.append({
            "endereco": starting_point,
            "cliente": "Ponto de Partida",
            "pedido": "Início",
            "tempo_do_anterior_para_o_atual": 0,
            "tempo_total_acumulado": 0,
            "data": delivery_date
        })

        # Loop para encontrar o cliente mais próximo em cada passo
        while unvisited_clients:
            nearest_client = None
            shortest_time = float('inf')

            # Procurar cliente mais próximo
            for client in unvisited_clients:
                try:
                    order_number = client.get('N° de pedido', 'Desconhecido')

                    # Verifica se o pedido já foi visitado
                    if order_number in visited_orders:
                        print(f"\033[32mAviso: O pedido nº {order_number} já foi visitado.\033[0m")
                        continue  # Ignora o cliente se o pedido já foi visitado

                    if 'endereco' in client and pd.notna(client['endereco']):
                        client_address = client['endereco']
                        
                        # Verifica se o endereço é inconsistente
                        if not client_address or client_address == 'NONE':
                            print(f"\033[31mErro: Pedido nº {order_number} - Endereço inconsistente ou ausente.\033[0m")
                            continue  # Ignora o cliente com endereço inconsistente

                        print(f"\033[34mCalculando tempo de viagem de {current_location} para {client_address}...\033[0m")  # Azul para a fase de cálculo
                        travel_time = get_travel_time(current_location, client_address)

                        if travel_time is None:
                            continue

                        # Cliente mais próximo até agora
                        if travel_time < shortest_time:
                            nearest_client = client
                            shortest_time = travel_time

                except Exception as e:
                    print(f"\033[31mErro ao processar cliente: {e}\033[0m")  # Vermelho para erro
                    continue

            if nearest_client:
                # Atualizar rota com o cliente e tempos
                total_travel_time += timedelta(hours=shortest_time)

                route.append({
                    "endereco": nearest_client['endereco'],
                    "cliente": nearest_client.get('Cliente', 'Desconhecido'),
                    "pedido": nearest_client.get('N° de pedido', 'Desconhecido'),
                    "tempo_do_anterior_para_o_atual": shortest_time,
                    "tempo_total_acumulado": total_travel_time.total_seconds() / 3600,
                    "data": delivery_date,
                    "numero_casa": nearest_client.get('N° Casa/Ap', 'N/A'),
                    "entrega_retirada": nearest_client.get('Entrega / Retirada', 'N/A'),
                    "modelo_sofa": nearest_client.get('Modelo Sofá', 'N/A'),
                    "tipo_montador": nearest_client.get('Tipo Montador', 'N/A'),
                    "tipo_caminhao": nearest_client.get('Tipo caminhão', 'N/A'),
                    "local": nearest_client.get('Local', 'N/A'),
                    "restricao_local": nearest_client.get('Restrições local', 'N/A'),
                    "restricao_horario": nearest_client.get('restrições Horário', 'N/A'),
                    "status": "Pendente"  # Status inicial
                })

                # Marcar o pedido como visitado
                visited_orders.add(nearest_client.get('N° de pedido', 'Desconhecido'))

                # Atualizar variáveis
                unvisited_clients.remove(nearest_client)
                current_location = nearest_client['endereco']

            else:
                print("\033[33mNenhum cliente acessível encontrado. Finalizando a busca.\033[0m")
                break

        # Adiciona o retorno ao ponto de partida
        return_time = get_travel_time(current_location, starting_point)
        if return_time is not None:
            total_travel_time += timedelta(hours=return_time)
            route.append({
                "endereco": starting_point,
                "cliente": "Ponto de Partida",
                "pedido": "Retorno",
                "tempo_do_anterior_para_o_atual": return_time,
                "tempo_total_acumulado": total_travel_time.total_seconds() / 3600,
                "data": delivery_date
            })

        routes[delivery_date] = route
        print(f"\033[32mRota criada para o dia {delivery_date} com sucesso.\033[0m")

    return routes