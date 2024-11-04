import requests

def get_distance_and_duration(api_key, origin, destination):
    # URL da Directions API
    url = "https://maps.googleapis.com/maps/api/directions/json"
    
    # Parâmetros da requisição
    params = {
        'origin': origin,
        'destination': destination,
        'key': api_key,
        'mode': 'driving'  # Modo de transporte: 'driving' para carro
    }
    
    # Faz a requisição à API
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if data['status'] == 'OK':
            # Extrai a distância e o tempo de viagem
            distance_text = data['routes'][0]['legs'][0]['distance']['text']
            distance_value = data['routes'][0]['legs'][0]['distance']['value']  # em metros
            
            # Extrai o tempo de viagem
            duration_text = data['routes'][0]['legs'][0]['duration']['text']
            duration_value = data['routes'][0]['legs'][0]['duration']['value']  # em segundos
            
            # Converte a distância para quilômetros
            distance_km = distance_value / 1000
            
            return distance_km, distance_text, duration_text, duration_value
        else:
            return None, None, None, data['status']
    else:
        return None, None, None, f"Error: {response.status_code}"