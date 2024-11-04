import requests
import pandas as pd
from datetime import datetime, timedelta

# Função para obter a duração da viagem entre dois locais
def get_travel_time(origin, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        'origin': origin,
        'destination': destination,
        'key': "AIzaSyAiz3yZErbSg6BIfKfve8YmskYu46ekeTs",  # Substitua pela sua chave de API
        'mode': 'driving'
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            # Extrai a duração da viagem em segundos
            duration_value = data['routes'][0]['legs'][0]['duration']['value']
            return duration_value / 3600  # Converte segundos para horas
    return None

# Função para calcular a melhor rota pelo tempo de viagem usando a regra do vizinho mais próximo
def make_best_route(grouped_clients, starting_point):
    route = [starting_point]
    unvisited_clients = []

    # Horários de trabalho
    morning_start = datetime.combine(datetime.today(), datetime.strptime('08:00', '%H:%M').time())
    morning_end = datetime.combine(datetime.today(), datetime.strptime('12:00', '%H:%M').time())
    afternoon_start = datetime.combine(datetime.today(), datetime.strptime('13:00', '%H:%M').time())
    afternoon_end = datetime.combine(datetime.today(), datetime.strptime('17:00', '%H:%M').time())

    # Filtro para datas de entrega nos próximos três dias
    today = datetime.now()
    upcoming_dates = [today + timedelta(days=i) for i in range(3)]
    upcoming_dates_str = [date.strftime('%d/%m/%Y') for date in upcoming_dates]

    # Marca clientes com erro
    errored_clients = set()

    # Extrair clientes do dicionário aninhado
    for date, cities in grouped_clients.items():
        try:
            date_formatted = datetime.strptime(date, '%m/%d/%Y').strftime('%d/%m/%Y')
        except ValueError:
            print(f"Data no formato inesperado: {date}. Pulando.")
            continue
        
        if date_formatted in upcoming_dates_str:
            for city, districts in cities.items():
                for district, clients in districts.items():
                    unvisited_clients.extend(clients)  # Adiciona todos os clientes à lista

    current_location = starting_point
    current_time = morning_start  # Início da rota

    while unvisited_clients:
        nearest_client = None
        shortest_time = float('inf')
        
        # Dentro do loop para verificar os clientes
        for client in unvisited_clients:
            if 'endereco' in client and pd.notna(client['endereco']):
                client_address = client['endereco']
                travel_time = get_travel_time(current_location, client_address)  # Tempo de viagem em horas

                if travel_time is None:
                    # Identifica o número do pedido do cliente
                    order_number = client.get('N° de pedido', 'Desconhecido')
                    # Verifica se já registramos um erro para este cliente
                    if order_number not in errored_clients:
                        print(f"Erro ao calcular tempo de viagem para o cliente: {order_number}")
                        errored_clients.add(order_number)  # Adiciona o cliente ao conjunto de erros
                    continue  # Ignora clientes sem tempo de viagem válido

                # Verifica se o cliente tem restrição de horário
                restriction_time = client.get('restriçõe Horário')
                if restriction_time:
                    restriction_hour = datetime.strptime(restriction_time, '%H:%M').time()
                    restriction_datetime = datetime.combine(current_time.date(), restriction_hour)

                    # Estima horário de chegada com base no tempo de viagem
                    estimated_arrival_time = current_time + timedelta(hours=travel_time)
                    
                    # Se o horário estimado de chegada estiver antes ou depois da restrição, ignora o cliente
                    if estimated_arrival_time < restriction_datetime - timedelta(minutes=15) or estimated_arrival_time > restriction_datetime + timedelta(minutes=15):
                        continue  # Pule para o próximo cliente

                # Ajustar para períodos de trabalho
                estimated_arrival_time = current_time + timedelta(hours=travel_time)
                if estimated_arrival_time >= morning_end and estimated_arrival_time < afternoon_start:
                    estimated_arrival_time = afternoon_start  # Reprograma para o próximo período
                elif estimated_arrival_time >= afternoon_end:
                    continue  # Pule se não puder ser entregue no horário comercial

                # Escolher o cliente mais próximo
                if travel_time is not None and travel_time < shortest_time:
                    nearest_client = client
                    shortest_time = travel_time

        if nearest_client:
            route.append(nearest_client)
            unvisited_clients.remove(nearest_client)
            current_location = nearest_client['endereco']
            current_time += timedelta(hours=shortest_time)  # Atualiza o horário atual com o tempo de viagem

            # Respeita a volta para o almoço e final do expediente
            if current_time >= morning_end and current_time < afternoon_start:
                current_time = afternoon_start  # Próxima entrega começa depois do almoço
            elif current_time >= afternoon_end:
                print("Fim do expediente. Voltando para a base.")
                break  # Fim do expediente
        else:
            break  # Finaliza o loop se nenhum cliente restante puder ser visitado
    
    print('Rota criada com sucesso.')
    return route