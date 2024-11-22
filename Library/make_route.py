import requests
import pandas as pd
from datetime import timedelta, datetime
import json

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

        # Verifica se a resposta da API foi bem-sucedida
        if response.status_code == 200:
            data = response.json()
            # Verifica se a API retornou uma resposta OK
            if data['status'] == 'OK':
                # Extrai a duração da viagem em segundos e converte para minutos
                duration_value = data['routes'][0]['legs'][0]['duration']['value'] / 60  # duração em minutos
                print(f"\033[32mDuração da viagem entre {origin} e {destination}: {duration_value:.2f} minutos.\033[0m")
                return duration_value
            else:
                # Caso a API retorne um status diferente de OK
                print(f"\033[33mAviso: API retornou status {data['status']} para a solicitação de {origin} a {destination}.\033[0m")
        else:
            # Se a resposta HTTP não for bem-sucedida
            print(f"\033[31mErro na requisição para {origin} a {destination}. Código de status: {response.status_code}.\033[0m")

    except requests.exceptions.RequestException as e:
        # Caso ocorra uma exceção durante a requisição
        print(f"\033[31mErro na requisição para {origin} a {destination}: {e}\033[0m")

    # Retorna None se não houver uma duração válida
    return None

def make_best_routes(grouped_clients, starting_point):
    routes = {}
    client_not_served = {}  # Dicionário para armazenar os clientes não atendidos

    # Obter as datas para os próximos três dias
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(3)]

    # Função auxiliar para organizar entregas por sessão
    def organize_route_for_session(session_time, unvisited_clients, current_location, accumulated_time):
        route = []
        total_travel_time = 0
        session_time_limit = session_time  # Tempo limite em minutos

        while unvisited_clients:
            nearest_client = None
            shortest_time = float('inf')
            travel_time = make_time = 0

            for client in unvisited_clients:
                try:
                    order_number = client.get('N° de pedido', 'Desconhecido')
                    if 'endereco' in client and pd.notna(client['endereco']):
                        client_address = client['endereco']
                        if not client_address or client_address == 'NONE':
                            print(f"\033[31mErro: Pedido nº {order_number} - Endereço inconsistente ou ausente.\033[0m")
                            continue

                        # Obtenha o tempo de montagem e o tempo de viagem
                        make_time = float(client.get('Tempo de montagem/entrega', 0))
                        travel_time = get_travel_time(current_location, client_address)
                        if travel_time is None:
                            continue

                        # Tempo total gasto com o cliente (viagem + montagem)
                        total_client_time = travel_time + make_time

                        if total_client_time < shortest_time:
                            nearest_client = client
                            shortest_time = total_client_time
                            shortest_make_time = make_time
                            shortest_travel_time = travel_time
                except Exception as e:
                    print(f"\033[31mErro ao processar cliente: {e}\033[0m")

            if nearest_client and (accumulated_time + shortest_time) <= session_time_limit:
                # Atualiza o tempo total acumulado
                accumulated_time += shortest_time

                # Adiciona todos os dados do cliente à rota
                route.append({
                    **nearest_client,  # Inclui todos os dados do cliente diretamente
                    "tempo_de_viagem": shortest_travel_time,
                    "tempo_de_montagem": shortest_make_time,
                    "tempo_total_cliente": shortest_time,
                    "tempo_total_acumulado": accumulated_time,
                    "status": "Pendente",
                    "posicao_entrega": len(route) + 1
                })

                unvisited_clients.remove(nearest_client)
                current_location = nearest_client['endereco']
            else:
                break  # Encerra a sessão se o tempo restante for insuficiente

        return route, unvisited_clients, current_location, accumulated_time

    # Criar rotas para cada dia
    for delivery_date in dates:
        unvisited_clients = []
        accumulated_time = 0  # Inicializa o tempo acumulado no início de cada dia
        if delivery_date in grouped_clients:
            for city in grouped_clients[delivery_date]:
                for district in grouped_clients[delivery_date][city]:
                    for client in grouped_clients[delivery_date][city][district]:
                        unvisited_clients.append(client)

        if not unvisited_clients:
            print(f"\033[33mNão há clientes para o dia {delivery_date}. Ignorando a criação de rota.\033[0m")
            continue

        daily_route = {"manhã": [], "tarde": []}  # Dicionário para separar manhã e tarde
        try:
            # Manhã: 8:30 - 12:00
            session_time = 240  # 4 horas em minutos
            print(f"\033[34mIniciando sessão da manhã para {delivery_date}.\033[0m")
            route_morning, unvisited_clients, last_location, accumulated_time = organize_route_for_session(
                session_time, unvisited_clients, starting_point, accumulated_time
            )
            travel_time_return = get_travel_time(last_location, starting_point)
            route_morning.append({
                "endereco": starting_point,
                "cliente": "Ponto de Partida",
                "pedido": "Retorno",
                "tempo_de_viagem": travel_time_return,
                "tempo_de_montagem": 0,  # Sem tempo de montagem no retorno
                "tempo_total_cliente": travel_time_return,
                "tempo_total_acumulado": accumulated_time + travel_time_return,  # Atualizando com tempo de retorno
                "status": "Retorno ao ponto de partida",
                "posicao_entrega": len(route_morning) + 1
            })
            daily_route["manhã"].extend(route_morning)

            # Tarde: 13:30 - 17:00
            session_time = 240  # 4 horas em minutos
            accumulated_time = 0  # Zera o tempo acumulado ao iniciar a tarde
            print(f"\033[34mIniciando sessão da tarde para {delivery_date}.\033[0m")
            route_afternoon, unvisited_clients, last_location, accumulated_time = organize_route_for_session(
                session_time, unvisited_clients, starting_point, accumulated_time
            )
            travel_time_return = get_travel_time(last_location, starting_point)
            route_afternoon.append({
                "endereco": starting_point,
                "cliente": "Ponto de Partida",
                "pedido": "Retorno",
                "tempo_de_viagem": travel_time_return,
                "tempo_de_montagem": 0,  # Sem tempo de montagem no retorno
                "tempo_total_cliente": travel_time_return,
                "tempo_total_acumulado": accumulated_time + travel_time_return,  # Atualizando com tempo de retorno
                "status": "Retorno ao ponto de partida",
                "posicao_entrega": len(route_afternoon) + 1
            })
            daily_route["tarde"].extend(route_afternoon)

            routes[delivery_date] = daily_route

        except Exception as e:
            print(f"\033[31mErro ao criar rota para o dia {delivery_date}: {e}\033[0m")

        # Organize clientes não atendidos no formato solicitado
        for client in unvisited_clients:
            delivery_date = client.get('Data Entrega', 'Desconhecido')
            city = client.get('localidade', 'Desconhecido')
            district = client.get('bairro', 'Desconhecido')

            if delivery_date not in client_not_served:
                client_not_served[delivery_date] = {}

            if city not in client_not_served[delivery_date]:
                client_not_served[delivery_date][city] = {}

            if district not in client_not_served[delivery_date][city]:
                client_not_served[delivery_date][city][district] = []

            # Adiciona todos os dados do cliente diretamente no dicionário
            client_not_served[delivery_date][city][district].append(client)  # Mantemos o cliente apenas uma vez

    return routes, client_not_served
    
def exceptions(route, client_not_served, special_clients):
    def add_special_clients_to_route(route, special_clients):
        for date, cities in special_clients.items():
            if date not in route:
                route[date] = {}

            for city, districts in cities.items():
                if city not in route[date]:
                    route[date][city] = {}

                for district, special_deliveries in districts.items():
                    if district not in route[date][city]:
                        route[date][city][district] = []

                    deliveries = route[date][city][district]
                    total_time_spent = sum(client.get('tempo_total_cliente', 0) for client in deliveries)
                    remaining_time = 240 - total_time_spent  # Tempo restante no turno atual (4 horas)

                    for special_client in special_deliveries:
                        try:
                            make_time = float(special_client.get('Tempo de montagem/entrega', 0))
                            travel_time = (
                                get_travel_time(deliveries[-1]['endereco'], special_client['endereco'])
                                if deliveries else 0
                            )
                            total_client_time = make_time + travel_time

                            # Remove clientes normais se não houver tempo suficiente
                            while total_client_time > remaining_time and deliveries:
                                normal_client = deliveries.pop(0)  # Remove o primeiro cliente normal
                                if normal_client.get("tipo_cliente", "normal") == "normal":
                                    add_to_client_not_served(client_not_served, normal_client, date)
                                    total_time_spent -= normal_client.get("tempo_total_cliente", 0)
                                    remaining_time += normal_client.get("tempo_total_cliente", 0)

                            # Adiciona o cliente especial, se houver tempo
                            if total_client_time <= remaining_time:
                                deliveries.append({
                                    **special_client,
                                    "tempo_de_viagem": travel_time,
                                    "tempo_de_montagem": make_time,
                                    "tempo_total_cliente": total_client_time,
                                    "tempo_total_acumulado": 240 - remaining_time + total_client_time,
                                    "status": "Pendente",
                                    "posicao_entrega": len(deliveries) + 1
                                })
                                remaining_time -= total_client_time
                            else:
                                # Caso o cliente especial também não caiba no tempo restante
                                add_to_client_not_served(client_not_served, special_client, date)
                        except Exception as e:
                            print(f"Erro ao processar cliente especial: {e}")

    def add_to_client_not_served(client_not_served, client, date):
        city = client.get('localidade', 'Desconhecido')
        district = client.get('bairro', 'Desconhecido')

        if date not in client_not_served:
            client_not_served[date] = {}

        if city not in client_not_served[date]:
            client_not_served[date][city] = {}

        if district not in client_not_served[date][city]:
            client_not_served[date][city][district] = []

        client_not_served[date][city][district].append(client)

    try:
        # Prioriza a inclusão de todos os clientes especiais
        add_special_clients_to_route(route, special_clients)
    except Exception as e:
        print(f"Erro ao adicionar clientes especiais à rota: {e}")

    return route, client_not_served