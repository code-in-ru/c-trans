import math

def calculate_distance(coord1, coord2): #  вычисляем расстояние между точками по их координатам
    lat1, lon1 = list(map(math.radians, coord1))
    lat2, lon2 = list(map(math.radians, coord2))
    cl1, cl2, sl1, sl2 = math.cos(lat1), math.cos(lat2), math.sin(lat1), math.sin(lat2)
    delta = lon2 - lon1
    cdelta, sdelta = math.cos(delta), math.sin(delta)
    y = math.sqrt(((cl2 * sdelta) ** 2) + ((cl1 * sl2 - sl1 * cl2 * cdelta) ** 2))
    x = sl1 * sl2 + cl1 * cl2 * cdelta
    ad = math.atan2(y, x)
    return ad * 6372795

STATION_LIST = []
TRANSPORT_LIST = []

class Route:
    def __init__(self, name, stations, *args):
        self.name = name #  номер маршрута
        self.vehilces = args #  кортеж ТС на маршруте
        self.stations = stations #  остановке на маршруте

    def __str__(self):
        print(f'Маршрут {self.name}')


class Vehicle:
    def __init__(self, ttype, model, route, max_volume):
        self.ttype = ttype #  тип ТС
        self.model = model #  модель ТС
        self.route = route #  маршрут ТС (объект класса Route)
        self.max_volume = max_volume #  максимальная вместимость ТС

    def get_volume(self):
        return 0 #  текущая вместимость ТС

    def get_coords(self):
        return 0, 0 #  текущие координаты ТС

    def get_speed(self):
        return 0 #  текущая скорость ТС

    def __str__(self):
        print(f'Модель {self.model}')


class Station:
    def __init__(self, name, coords, *args):
        self.name = name #  название остановки
        self.coords = coords #  координаты остановки
        self.routes = args #  маршруты на остановке (кортеж объектов класса Route)


class PassengerRoute:
    def __init__(self, start_point=(0, 0), end_point=(3, 3)):
        self.start_point = start_point #  начало пути пассажира
        self.end_point = end_point #  конец пути пассажира
        self.start_station = min([calculate_distance(start_point, station.coords) for station in STATION_LIST]) #  ближайшая остановка отправления
        self.end_station = min([calculate_distance(end_point, station.coords) for station in STATION_LIST]) #  ближайшая остановка прибытия

    def time_to_arrive(self):
        return min([calculate_distance(self.start_station, transport.coords) for transport in TRANSPORT_LIST]) #  расстояние до ближайшего автобуса
