from typing import List


class Route:
    def __init__(self):
        self.id: int
        self.stop_points: List[StopPoint]
        self.waypoints: tuple

        self.current_load: float
        self.interval: float  # I

        # stat
        # self.loses_p_hour_waiting: float  # Cпч
        # self.hourly_passenger_traffic: int  # Qпч
        # self.coef_variable_pass_traffic: float  # Muсм
        # self.coef_shifts_pass_traffic: float  # kнер
        # self.max_hour_pass_traffic: int  #
        # self.total_pass_p_hour: int  #
        # self.avg_pass_distance: float  #
        # self.avw_waiting_time: float  #

        # из презентации по статистике яндекса
        self.year_traffic: tuple
        self.week_traffic: tuple
        self.day_traffic: tuple

        # output:
        self.transport: List[Transport]

    def length_of_turnover(self):
        '''длина оборота на маршруте l0'''
        return  # рассчетное значение по waypoints

    def total_capacity(self):
        '''общая вместимость ТС на маршруте'''
        return sum(t.capacity for t in self.transport)

    def optimal_capacity(self, *args):
        return  # функция Вадима

    def calculate_transport(self):
        '''назначает конкретные ТС и интервал движения на маршруте'''
        self.transport = []
        self.interval = 1


class VehiclesEquipment:
    '''парк ТС'''
    def __init__(self):
        self.name: str
        self.vehicles: List[Transport]
        self.faulty_vehicles: List[Transport]


class Transport:
    '''конктерная модель ТС'''
    def __init__(self):
        self.current_route: Route
        self.model: str
        self.capacity: int
        self.shedule: list  # ?

        self.costs_p_kilometer: float
        self.costs_p_hour: float


class StopPoint:
    '''остановка ? нахер надо'''
    def __init__(self):
        self.id: int
        self.name: str
        self.location: tuple
