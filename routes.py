import math


class Route:
    def __init__(self, number, turnover_length, turnover_time, average_length, route_length, interval, timeout,
                 passenger_traffic, cost_per_kilo, cost_per_hour, hourly_unevenness=1.25):
        self.number = number
        self.turnover_length = turnover_length
        self.turnover_time = turnover_time
        self.average_lenght = average_length
        self.removability = route_length / self.average_lenght
        self.hourly_unevenness = hourly_unevenness
        self.timeout = timeout
        self.interval = interval
        self.irregularity = 1.51 #  не назначено
        self.passenger_traffic = passenger_traffic
        self.cost_per_kilo = cost_per_kilo
        self.cost_per_hour = cost_per_hour
        self.optimal_capacity = self.irregularity / self.removability * math.sqrt(self.passenger_traffic *
            self.hourly_unevenness * (self.turnover_length * self.cost_per_kilo + self.cost_per_hour *
                                      self.turnover_time) / 152)

    def __str__(self):
        print(f'Маршрут {self.number}')
