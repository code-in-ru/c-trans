import math

costs_p_km: float = 0  # акм1
costs_p_hour: float = 0  # ач1
zp = 12130


class Transport:
    def __init__(self):
        self.model: str = ''
        self.capacity: int = 0


class Route:
    def __init__(self):
        self.waypoints = []

        self.current_load: float = 0
        self.interval: float  # I

        # зависят от времени
        self.max_hourly_passenger_traffic: int = 0  # Qпч
        self.total_pass_traffic: int = 0  # Qобщ
        self.avg_pass_distance: float = 0  # lср

        self.coef_irregular_pass_traffic = self.max_hourly_passenger_traffic / self.total_pass_traffic  # kнер
        self.time_turnover: int = 0  # t0
        self.distance = self.length_turnover(self.waypoints) / 2  # lm
        self.coef_variable_pass_traffic = self.distance / self.avg_pass_distance  # Мюсм
        self.avg_loses_waiting: float = 0  #


        self.transport = []


    def set_current_load(self, val):
            self.current_load = val


    def set_max_hourly_passenger_traffic(self, val):
            self.max_hourly_passenger_traffic = val


    def length_turnover(self, args):
            '''длина оборота маршрута l0'''


            ad = 0
            for i in range(len(args) - 1):
                lat1, lon1 = map(math.radians, args[i])
                lat2, lon2 = map(math.radians, args[i + 1])
                cl1, cl2, sl1, sl2 = math.cos(lat1), math.cos(lat2), math.sin(lat1), math.sin(lat2)
                delta = lon2 - lon1
                cdelta, sdelta = math.cos(delta), math.sin(delta)
                y = math.sqrt(((cl2 * sdelta) ** 2) + ((cl1 * sl2 - sl1 * cl2 * cdelta) ** 2))
                x = sl1 * sl2 + cl1 * cl2 * cdelta
                ad += math.atan2(y, x)
            return float(ad)


    def passenger_per_hour_cost(self, transport_capacity):
        '''Рассчет стоимости руб/пас в час на определенном маршруте, где:
        average_passenger_distance - средняя протяженность маршрута пассажира
        irregular_coef - коэф-т нерегулярности потока
        full_distance_time - время оборота маршрута
        passenger_per_hour - пассажиров в час
        one_kilo_cost - себестоимость одного километра проезда по маршруту
        transport_capacity - вместимость транспортного средства
        losses_for_waiting - потеря пассажира за ожидание транспорта в час
        distance - расстояние маршрута туда-обратно (расчитывается в функции calculate_distance)'''
        result = self.length_turnover(self.waypoints) / self.time_turnover * (
                costs_p_km / transport_capacity + (self.avg_loses_waiting * transport_capacity *
                                                   self.coef_variable_pass_traffic /
                                                   self.coef_irregular_pass_traffic * 1.5625 * self.avg_pass_distance * self.total_pass_traffic)
        )
        return result


    def total_capacity(self):
        '''общая вместимость ТС на маршруте'''
        return sum(t.capacity for t in self.transport)



    def optimal_passenger_capacity(self):
        '''Рассчет оптимальной пассажировместимости в определенный период времени, где:
        average_passenger_distance - средняя протяженность маршрута пассажира
        irregular_coef - коэф-т нерегулярности потока
        full_distance_time - время оборота маршрута
        passenger_per_hour - пассажиров в час
        one_kilo_cost - себестоимость одного километра проезда по маршруту
        one_hour_cost - себестоимость одного часа работы маршрута
        distance - расстояние маршрута туда-обратно (расчитывается в функции calculate_distance)'''

        optimal = self.coef_irregular_pass_traffic / self.coef_variable_pass_traffic * math.sqrt(
            self.total_pass_traffic * 1.25 * (
                        self.length_turnover(self.waypoints) * costs_p_km + costs_p_hour * self.time_turnover) / zp)
        return optimal


    def transport_quantity(self, optimal_passenger_capacity):
        return self.total_pass_traffic * 1.25 * self.coef_irregular_pass_traffic * self.time_turnover / (
                    2 * optimal_passenger_capacity * self.coef_variable_pass_traffic)


buses = []
routes = []
result_buses = []
for route in routes:
    Qopt = route.optimal_passenger_capacity()
    Cjk = zip((route.passenger_per_hour_cost(bus.capacity) for bus in buses), buses)
    optimal_bus = min(filter(lambda c: c[1].capacity >= Qopt, Cjk), key=lambda c: c[0])[1]
    A = route.transport_quantity(optimal_bus.capacity)
    I = route.time_turnover / A
    result_buses.append((optimal_bus, A, I))

optimal_transport_per_route = dict(
    zip(routes, result_buses))  # оптимальный транспорт на маршруте, его количество и интервал движения
