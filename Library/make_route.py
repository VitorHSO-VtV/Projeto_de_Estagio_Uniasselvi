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

        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK':
                # Extrai a duração da viagem em segundos
                duration_value = data['routes'][0]['legs'][0]['duration']['value'] / 60
                duration_in_hours = duration_value / 60  # Converte segundos para minutos
                print(
                    f"\033[32mDuração da viagem entre {origin} e {destination}: {duration_in_hours:.2f} minutos.\033[0m")
                return duration_value
            else:
                print(
                    f"\033[33mAviso: API retornou status {data['status']} para a solicitação de {origin} a {destination}.\033[0m")
        else:
            print(
                f"\033[31mErro na requisição para {origin} a {destination}. Código de status: {response.status_code}.\033[0m")

    except requests.exceptions.RequestException as e:
        print(f"\033[31mErro na requisição: {e}\033[0m")

    return None



# Função para criar rotas otimizadas para múltiplos dias
def make_best_routes(grouped_clients, starting_point):
    routes = {}
    remaining_clients = []  # Para armazenar clientes não visitados ao final

    # Obter as datas para os próximos três dias
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(3)]

    # Função auxiliar para organizar entregas por sessão
    def organize_route_for_session(session_time, unvisited_clients, current_location, accumulated_time):
        route = []
        total_travel_time = 0
        session_time_limit = session_time # Tempo limite em minutos

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
                except Exception as e:
                    print(f"\033[31mErro ao processar cliente: {e}\033[0m")

            if nearest_client and (accumulated_time + total_client_time) <= session_time_limit:
                total_travel_time += shortest_time
                tempo_total_cliente = travel_time + make_time  # Soma de viagem + montagem

                # Atualiza o tempo total acumulado
                accumulated_time += tempo_total_cliente

                route.append({
                    "endereco": nearest_client['endereco'],
                    "cliente": nearest_client.get('Cliente', 'Desconhecido'),
                    "pedido": nearest_client.get('N° de pedido', 'Desconhecido'),
                    "tempo_de_viagem": travel_time,
                    "tempo_de_montagem": make_time,
                    "tempo_total_cliente": tempo_total_cliente,  # Correção do tempo total do cliente
                    "tempo_total_acumulado": accumulated_time,  # Atualizando o tempo total acumulado
                    "status": "Pendente"
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
                "status": "Retorno ao ponto de partida"
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
                "status": "Retorno ao ponto de partida"
            })
            daily_route["tarde"].extend(route_afternoon)

            routes[delivery_date] = daily_route

        except Exception as e:
            print(f"\033[31mErro ao criar rota para o dia {delivery_date}: {e}\033[0m")

    # Salva os clientes restantes em um arquivo JSON
    remaining_clients.extend(unvisited_clients)
    if remaining_clients:
        with open("clientes_nao_atendidos.json", "w") as f:
            json.dump(remaining_clients, f, ensure_ascii=False, indent=4)
        print("\033[32mClientes não atendidos foram salvos no arquivo 'clientes_nao_atendidos.json'.\033[0m")

    return routes