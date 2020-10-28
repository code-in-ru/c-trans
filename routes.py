class Route:
    def __init__(self, number, **kwargs):
        self.number = number
        self.vehilces = dict(kwargs)

    def __str__(self):
        print(f'Маршрут {self.number}')


class Vehicle:
    def __init__(self, model, max_volume):
        self.model = model
        self.max_volume = max_volume
        self.volume = 0 #  текущая заполненность (как собирать?)

    def __str__(self):
        print(f'Модель {self.model}')





