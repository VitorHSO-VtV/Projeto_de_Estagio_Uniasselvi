import requests
import pandas as pd
from datetime import timedelta, datetime
from geopy.distance import geodesic

def get_coordinates_nominatim(address):
    url = f"https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'addressdetails': 1
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
            else:
                print(f"Endereço não encontrado: {address}")
                return None
        else:
            print(f"Erro na solicitação para {address}: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar Nominatim: {e}")
        return None

def get_route_osrm(start_coords, end_coords):
    url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
    params = {"overview": "simplified"}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "routes" in data and data["routes"]:
                duration = data['routes'][0]['duration'] / 60  # em minutos
                distance = data['routes'][0]['distance'] / 1000  # em quilômetros
                return duration, distance
            else:
                print("Nenhuma rota encontrada.")
                return None, None
        else:
            print(f"Erro na solicitação de rota: {response.status_code}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar OSRM: {e}")
        return None, None

def get_travel_time_and_distance(origin, destination):
    coords_origin = get_coordinates_nominatim(origin)
    coords_destination = get_coordinates_nominatim(destination)

    if coords_origin and coords_destination:
        duration, distance = get_route_osrm(coords_origin, coords_destination)
        if duration is not None and distance is not None:
            print(f"\033[32mViagem entre {origin} e {destination}: {duration:.2f} minutos, {distance:.2f} km.\033[0m")
            return duration, distance
        else:
            print("Não foi possível calcular a rota.")
            return None, None
    else:
        print("Coordenadas não encontradas para os endereços fornecidos.")
        return None, None

def make_best_routes(grouped_clients, starting_point, truck_volume, tolerance_time = 240, limit_time = 240, benefit_coefficient = 1):
    routes = {}
    client_not_served = {}  # Dicionário para armazenar os clientes não atendidos

    # Obter as datas para os próximos três dias
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(3)]

    def organize_route_for_session(session_time, unvisited_clients, current_location, accumulated_time, accumulated_volume, last_best_cost_benefit):
        route = []
        session_time_limit = session_time  # Tempo limite em minutos
        accumulated_travel_distance = 0  # Distância acumulada (reiniciada em cada sessão)
        
        # Reiniciar last_best_cost_benefit em cada turno
        last_best_cost_benefit = 0  # Reinicia ao começar uma nova sessão

        while unvisited_clients:
            nearest_client = None
            best_cost_benefit = float('-inf')  # Para encontrar o melhor custo-benefício
            shortest_time = float('inf')  # Inicialize com um valor alto
            travel_time = make_time = travel_distance = 0

            for client in unvisited_clients:
                try:
                    order_number = client.get('N° de pedido', 'Desconhecido')
                    client_volume = float(client.get('Volume M\u00b3', 0)) * 0.01  # Volume em m³
                    if accumulated_volume + client_volume > truck_volume:
                        continue  # Pule se exceder o volume do caminhão

                    if 'endereco' in client and pd.notna(client['endereco']):
                        client_address = client['endereco']
                        if not client_address or client_address == 'NONE':
                            print(f"\033[31mErro: Pedido nº {order_number} - Endereço inconsistente ou ausente.\033[0m")
                            continue

                        # Obtenha o tempo de montagem, tempo e distância de viagem
                        make_time = float(client.get('Tempo de montagem/entrega', 0))
                        travel_time, travel_distance = get_travel_time_and_distance(current_location, client_address)
                        if travel_time is None or travel_distance is None:
                            continue

                        # Atualizar a distância acumulada
                        next_distance = accumulated_travel_distance + travel_distance

                        # Calcular tempo total e custo-benefício (número de clientes / distância acumulada)
                        total_client_time = travel_time + make_time
                        cost_benefit = (next_distance if next_distance > 0 else 1) / (len(route) + 1)

                        # Escolha o cliente com maior custo-benefício ou menor tempo total
                        if total_client_time < shortest_time:
                            nearest_client = client
                            best_cost_benefit = cost_benefit
                            shortest_time = total_client_time
                            shortest_make_time = make_time
                            shortest_travel_time = travel_time
                            shortest_travel_distance = travel_distance
                            nearest_client_volume = client_volume       
                except Exception as e:
                    print(f"\033[31mErro ao processar cliente: {e}\033[0m")

            # Condição para adicionar o cliente à rota
            if nearest_client and (
                (accumulated_time + shortest_travel_time + shortest_make_time) <= session_time_limit or
                (best_cost_benefit <= last_best_cost_benefit + benefit_coefficient and (accumulated_time + shortest_travel_time + shortest_make_time) <= session_time_limit + tolerance_time)
            ):
                # Atualize a lógica para adicionar o cliente
                accumulated_time += shortest_travel_time + shortest_make_time
                accumulated_volume += nearest_client_volume
                accumulated_travel_distance += shortest_travel_distance  # Atualização correta da distância acumulada

                route.append({
                    **nearest_client,
                    "distancia_acumulada": accumulated_travel_distance,  # Usando a variável correta
                    "custo_beneficio": best_cost_benefit,
                    "tempo_de_viagem": shortest_travel_time,
                    "distancia_de_viagem_km": shortest_travel_distance,
                    "tempo_de_montagem": shortest_make_time,
                    "tempo_total_cliente": shortest_travel_time + shortest_make_time,
                    "tempo_total_acumulado": accumulated_time,
                    "volume_acumulado": accumulated_volume,
                    "status": "Pendente",
                    "posicao_entrega": len(route) + 1
                })
                
                # Atualize a variável last_best_cost_benefit para o cliente atual
                last_best_cost_benefit = best_cost_benefit

                unvisited_clients.remove(nearest_client)
                current_location = nearest_client['endereco']
            else:
                break

        return route, unvisited_clients, current_location, accumulated_time, accumulated_volume, last_best_cost_benefit

    # Criar rotas para cada dia
    for delivery_date in dates:
        unvisited_clients = []
        accumulated_time = 0  # Inicializa o tempo acumulado no início de cada dia
        accumulated_volume = 0  # Inicializa o volume acumulado no início do dia

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
            session_time = limit_time  # 4 horas em minutos
            print(f"\033[34mIniciando sessão da manhã para {delivery_date}.\033[0m")
            route_morning, unvisited_clients, last_location, accumulated_time, accumulated_volume, last_best_cost_benefit = organize_route_for_session(
                session_time, unvisited_clients, starting_point, accumulated_time, accumulated_volume, 0  # Reiniciando o valor em cada turno
            )
            travel_time_return, travel_distance_return = get_travel_time_and_distance(last_location, starting_point)
            route_morning.append({
                "endereco": starting_point,
                "cliente": "Ponto de Partida",
                "pedido": "Retorno",
                "tempo_de_viagem": travel_time_return,
                "distancia_de_viagem_km": travel_distance_return,
                "tempo_de_montagem": 0,  # Sem tempo de montagem no retorno
                "tempo_total_cliente": travel_time_return,
                "tempo_total_acumulado": accumulated_time + travel_time_return,
                "volume_acumulado": accumulated_volume,
                "status": "Retorno ao ponto de partida",
                "posicao_entrega": len(route_morning) + 1
            })
            daily_route["manhã"].extend(route_morning)

            # Tarde: 13:30 - 17:00
            session_time = limit_time  # 4 horas em minutos
            accumulated_time = 0  # Zera o tempo acumulado ao iniciar a tarde
            print(f"\033[34mIniciando sessão da tarde para {delivery_date}.\033[0m")
            route_afternoon, unvisited_clients, last_location, accumulated_time, accumulated_volume, last_best_cost_benefit = organize_route_for_session(
                session_time, unvisited_clients, starting_point, accumulated_time, accumulated_volume, 0  # Reiniciando o valor em cada turno
            )
            travel_time_return, travel_distance_return = get_travel_time_and_distance(last_location, starting_point)
            route_afternoon.append({
                "endereco": starting_point,
                "cliente": "Ponto de Partida",
                "pedido": "Retorno",
                "tempo_de_viagem": travel_time_return,
                "distancia_de_viagem_km": travel_distance_return,
                "tempo_de_montagem": 0,  # Sem tempo de montagem no retorno
                "tempo_total_cliente": travel_time_return,
                "tempo_total_acumulado": accumulated_time + travel_time_return,
                "volume_acumulado": accumulated_volume,
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
            city = client.get('localidade', 'Desconhecida')
            district = client.get('bairro', 'Desconhecido')
            client_not_served.setdefault(delivery_date, {}).setdefault(city, {}).setdefault(district, []).append(client)

    return routes, client_not_served
    
def exceptions(route, client_not_served, special_clients, truck_volume):
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
                    current_volume = sum(client.get('volume', 0) for client in deliveries)  # Volume já usado

                    for special_client in special_deliveries:
                        try:
                            make_time = float(special_client.get('Tempo de montagem/entrega', 0))
                            travel_time = (
                                get_travel_time(deliveries[-1]['endereco'], special_client['endereco'])
                                if deliveries else 0
                            )
                            total_client_time = make_time + travel_time
                            client_volume = special_client.get('volume', 0)

                            # Remove clientes normais se não houver tempo ou espaço suficiente
                            while (total_client_time > remaining_time or current_volume + client_volume > truck_volume) and deliveries:
                                normal_client = deliveries.pop(0)  # Remove o primeiro cliente normal
                                if normal_client.get("tipo_cliente", "normal") == "normal":
                                    add_to_client_not_served(client_not_served, normal_client, date)
                                    total_time_spent -= normal_client.get("tempo_total_cliente", 0)
                                    remaining_time += normal_client.get("tempo_total_cliente", 0)
                                    current_volume -= normal_client.get('volume', 0)

                            # Adiciona o cliente especial, se houver tempo e espaço
                            if total_client_time <= remaining_time and current_volume + client_volume <= truck_volume:
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
                                current_volume += client_volume
                            else:
                                # Caso o cliente especial também não caiba
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