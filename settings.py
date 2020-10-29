import requests
import routes


CITY = input()  # Вводим город
routes_set = requests.get(f'http://maxi-karta.ru/{CITY}/transport/query/routes').json()

routes_ids = []
for route in routes_set['routes']:
    routes_ids.append(route['route_id'])

for route_id in routes_ids:
    data_set = requests.get(f'http://maxi-karta.ru/miass/transport/query/stations?route_id={route_id}').json()
    for station in data_set['stations']:
        direction = station['direction']
        coords = (station['lat'], station['lon'])
        name = station['name']
        station_id = station['station_id']
        routes.STATION_LIST.append(routes.Station(route_id, (), name, coords, direction))  # Заполняем список остановок
