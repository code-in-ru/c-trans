import math

something = ()  # координаты точек


def calculate_distance(*args):  # вычисляем длину маршрута по координатам его точек
    ad = 0
    for coords in args:
        lat1, lon1 = list(map(math.radians, coords[0]))
        lat2, lon2 = list(map(math.radians, coords[1]))
        cl1, cl2, sl1, sl2 = math.cos(lat1), math.cos(lat2), math.sin(lat1), math.sin(lat2)
        delta = lon2 - lon1
        cdelta, sdelta = math.cos(delta), math.sin(delta)
        y = math.sqrt(((cl2 * sdelta) ** 2) + ((cl1 * sl2 - sl1 * cl2 * cdelta) ** 2))
        x = sl1 * sl2 + cl1 * cl2 * cdelta
        ad += math.atan2(y, x)
    return float(ad)


'''Рассчет оптимальной пассажировместимости в определенный период времени, где:
    average_passenger_distance - средняя протяженность маршрута пассажира
    irregular_coef - коэф-т нерегулярности потока
    full_distance_time - время оборота маршрута
    passenger_per_hour - пассажиров в час
    one_kilo_cost - себестоимость одного километра проезда по маршруту
    one_hour_cost - себестоимость одного часа работы маршрута
    distance - расстояние маршрута туда-обратно (расчитывается в функции calculate_distance)'''
def optimal_passenger_capacity(average_passenger_distance, irregular_coef,
                                        full_distance_time, passenger_per_hour, one_kilo_cost, one_hour_cost,
                               distance=calculate_distance(something)):
    optimal = irregular_coef / (distance / average_passenger_distance) * \
              math.sqrt(
                  passenger_per_hour * 1.25 * (distance * one_kilo_cost + one_hour_cost * full_distance_time) /
                  12130)
    return optimal


'''Рассчет стоимости руб/пас в час на определенном маршруте, где:
    average_passenger_distance - средняя протяженность маршрута пассажира
    irregular_coef - коэф-т нерегулярности потока
    full_distance_time - время оборота маршрута
    passenger_per_hour - пассажиров в час
    one_kilo_cost - себестоимость одного километра проезда по маршруту
    transport_capacity - вместимость транспортного средства
    losses_for_waiting - потеря пассажира за ожидание транспорта в час
    distance - расстояние маршрута туда-обратно (расчитывается в функции calculate_distance)'''
def passenger_per_hour_cost(full_distance_time, one_kilo_cost, transport_capacity, losses_for_waiting,
                             irregular_coef, average_passenger_distance, passenger_per_hour,
                             distance=calculate_distance(something)):
    result = distance / full_distance_time * (
        one_kilo_cost / transport_capacity + (losses_for_waiting * transport_capacity *
                                              (distance / 2 / average_passenger_distance) /
                                              irregular_coef * 1.5625 * average_passenger_distance * passenger_per_hour)
    )
    return result


def transport_quantity(passenger_per_hour, irregular_coef, full_distance_time, distance, average_passenger_distance,
                       one_kilo_cost, one_hour_cost):
    return passenger_per_hour * 1.25 * irregular_coef * full_distance_time / (2 *
                            optimal_passenger_capacity(average_passenger_distance, irregular_coef, full_distance_time,
                                                  passenger_per_hour, one_kilo_cost, one_hour_cost,
                                                  distance=calculate_distance(something)) * (distance / 2
                                                                                         / average_passenger_distance))


def time_interval(full_distance_time, passenger_per_hour, irregular_coef, distance, average_passenger_distance):
    return full_distance_time / transport_quantity(passenger_per_hour, irregular_coef, full_distance_time, distance,
                                                   average_passenger_distance)

