import math


def calculate_distance(coord1, coord2):  # вычисляем расстояние между точками на карте по их координатам
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
    def __init__(self, number, *args):
        self.number = number  # номер маршрута
        self.vehilces = args  # список ТС на маршруте

    def __str__(self):
        return f'Маршрут {self.number}'


class Vehicle:
    def __init__(self, ttype, model, max_volume):
        self.ttype = ttype  # тип ТС
        self.model = model  # модель ТС
        self.max_volume = max_volume  # максимальная вместимость ТС

    def get_volume(self):
        return 0  # текущая вместимость ТС

    def get_coords(self):
        return 0, 0  # текущие координаты ТС

    def get_speed(self):
        return 60  # текущая скорость ТС

    def __str__(self):
        return f'Модель {self.model}'


class Station(Route):
    def __init__(self, number, vehicles, name, coords):
        super().__init__(number, vehicles)
        self.name = name  # название остановки
        self.coords = coords  # координаты остановки

    def __str__(self):
        return f'{self.name}'


class PassengerRoute:
    def __init__(self, start_point=(0, 0), end_point=(3, 3)):
        self.start_point = start_point  # начало пути пассажира
        self.end_point = end_point  # конец пути пассажира
        dist_start_dict = dict(
            zip(STATION_LIST, [calculate_distance(start_point, station.coords) for station in STATION_LIST]))
        dist_start_dict = dict(sorted(dist_start_dict.items(), key=lambda x: x[1]))
        self.start_station = list(dist_start_dict)[0]  # ближайшая остановка отправления
        dist_end_dict = dict(
            zip(STATION_LIST, [calculate_distance(end_point, station.coords) for station in STATION_LIST]))
        dist_end_dict = dict(sorted(dist_end_dict.items(), key=lambda x: x[1]))
        self.end_station = list(dist_end_dict)[0]  # ближайшая остановка прибытия
        trans_distance = dict(
            zip(TRANSPORT_LIST,
                [calculate_distance(self.start_station.coords, transport.get_coords()) for transport in
                 TRANSPORT_LIST]))
        self.nearest_transport = list(dict(sorted(trans_distance.items(), key=lambda x: x[1])))[
            0]  # ближайший транспорт

    def time_to_arrive(self):
        transport_distanation = calculate_distance(self.nearest_transport.get_coords(),
                                  self.start_station.coords)  # расстояние до ближайшего транспорта
        return transport_distanation / self.nearest_transport.get_speed()  # время прибытия транспорта


trolleybus = Vehicle('тролейбус', 'ТГ-120', 40)
TRANSPORT_LIST.append(trolleybus)
third = Route('3', (trolleybus,))
automobile_palace = Station('3', (trolleybus,), 'Дворец автомобилестроителей', (55.059447, 60.107223))
fersman_street = Station('3', (trolleybus,), 'Улица Ферсмана', (55.055740, 60.108038))
STATION_LIST.append(automobile_palace)
STATION_LIST.append(fersman_street)

me = PassengerRoute((55.060716, 60.111664), (55.054837, 60.108087))
print(me.start_station)
print(me.end_station)
print(me.time_to_arrive())
