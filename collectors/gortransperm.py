# This module collects iformation about moving the buses. It is using the bustime.ru API

import http.client
import logging
import json
from urllib.parse import urlencode
import hashlib
import os
import time
from datetime import date
from pymongo import MongoClient, GEO2D


API_HOST = "www.map.gortransperm.ru"
API_PATH = "/json/"
API_REQUEST_RATE = 60  # Per minute
CACHE_TIME = 600  # In seconds
CACHE_DIR = "cache/"
CACHE_EXT = ".cache"

HTTP_CLIENT_IDLE = 1000  # In msec
HTTP_MAX_ERRORS = 5

DATE_FORMAT = "%d.%m.%Y"

ROUTES_IDS = ("01", "02", "03", "802", "807")
ROUTES_IDS = ("01", )
COORDS_ACCURACY = 6 # Number digits after dot




def __get_cache_filename(path_str):
    """It create cache filename from path_str"""
    hash_object = hashlib.md5(path_str.encode())
    filename = CACHE_DIR + hash_object.hexdigest() + CACHE_EXT
    return filename


def __load_cache(path_str: str = ""):
    """It check file with cashed data and load data from file."""
    if CACHE_TIME <= 0:
        return False
    data = False
    filename = __get_cache_filename(path_str)
    logging.debug('Data for string {0} loading from {1}'.format(path_str, filename))
    if CACHE_TIME > 0:
        try:
            expired_time = os.path.getmtime(filename) + CACHE_TIME
            if time.time() > expired_time:
                logging.info(
                    'The cache has expiried {0}'.format(time.strftime("%Y-%m-%d %H-%M", time.gmtime(expired_time))))
                return False
            else:
                with open(filename, 'r') as fp:
                    data = json.load(fp)
        except FileNotFoundError:
            logging.info("File {0} not found. Cache not existing".format(filename))
        except:
            logging.error("File {0} not found. Cache not existing")
            return False
    return data

def __save_cache(input_data: dict, path_str: str = ""):
    filename = __get_cache_filename(path_str)
    with open(filename, 'w') as fp:
        json.dump(input_data, fp)
    return True



def __go_request(path_need_data):
    # Go Request
    conn = http.client.HTTPConnection(API_HOST, timeout=15)
    conn.request("GET", path_need_data)
    response_str = False
    try:
        response = conn.getresponse().read()
        logging.info("Request send!")
        response_str = response.decode('utf-8')
    except http.client.HTTPException:
        logging.warning("Problem with request {0}".format(http.client.error()))
        response_str = False
    finally:
        conn.close()
    return response_str

def __get_data(type_data: str = '/ping', get_parametrs: dict = False):
    """
    This function get data from api with api rules and return data list.
    """
    if not hasattr(__get_data, 'doit_time'):  # Parameter for limit request rate
        __get_data.doit_time = time.time()
    out_data = False
    path_need_data = API_PATH + type_data
    if get_parametrs:
        parametrs_list = list(get_parametrs.items())
        # We need sorting parameters list for cache names
        parametrs_list.sort()
        path_need_data += '?' + urlencode(parametrs_list)
    if CACHE_TIME > 0:
        out_data = __load_cache(path_need_data)
        if out_data:
            return out_data
    # Sleep if needed
    now_time = time.time()
    if now_time < __get_data.doit_time:
        sleep_time = __get_data.doit_time - now_time
        logging.debug('Request IDLE time is {0}'.format(sleep_time))
        time.sleep(sleep_time)
    __get_data.doit_time += HTTP_CLIENT_IDLE / 1000
    # Go Request
    request_str = False
    while not request_str:
        request_str = __go_request(path_need_data)
        if type(request_str) == int:
            request_str = False
            continue
        elif type(request_str) == str:
            logging.info('Size of received data {0} bytes'.format(len(request_str)))
        else:
            logging.error("Unknown error data receive")
            return 0
    try:
        out_data = json.loads(request_str)
    except json.decoder.JSONDecodeError:
        print(request_str)
        logging.error('JSON decode is failed with content {0}'.format(request_str))
        return 0
    if CACHE_TIME > 0:
        __save_cache(out_data, path_need_data)
    return out_data


def coord_to_int(dig_string:str, ndigits=COORDS_ACCURACY):
    num_list = dig_string.split(".")
    output_num = int(num_list[0]) * pow(10, ndigits) + int(num_list[1][0:ndigits])
    return output_num

def coord_from_int(number:int, ndigits=COORDS_ACCURACY):
    output_str = "{0}.{1}".format(number // pow(10, ndigits), number % pow(10, ndigits))
    return output_str


def load_routes_list(for_date=date.today()):
    # http://www.map.gortransperm.ru/json/route-types-tree/30.10.2020/
    data = __get_data('route-types-tree/{0}/'.format(for_date.strftime(DATE_FORMAT)))
    return data


def load_route_data(route_id: str = '02', for_date=date.today()):
    # http://www.map.gortransperm.ru/json/full-route/30.10.2020/02
    data = __get_data('full-route/{0}/{1}'.format(for_date.strftime(DATE_FORMAT), route_id))
    return data


def load_bus_data(bus_id: str = '804', timestamp: int = round(time.time())):
    # http://www.map.gortransperm.ru/json/get-moving-autos/-804-?_=1604081243508
    # http://www.map.gortransperm.ru/json/get-moving-autos/-807-?_=1604081243514
    data = __get_data('get-moving-autos/-{0}-'.format(bus_id), {"_": timestamp})
    return data

def pull_route_info(route_id :str = "02", for_date=date.today()):
    data = load_routes_list(for_date=for_date)
    return_dict = False
    for routes in data:
        for route in routes['children']:
            if route['routeId'] == route_id:
                return_dict = {'id': route['routeId'],
                               'route_number': route['routeNumber'],
                               'title': route['title'],
                               'type': routes['routeTypeId'],
                               'type_title': routes['title'],
                               }
                continue
        if return_dict:
            continue
    return return_dict

def pull_route_geometry(route_id: str = '02', direction: str = 'fwd'):
    """
    :param route_id:
    :param direction: fwd | bkwd
    :return: dicts with way paints
    """
    data = load_route_data(route_id=route_id)
    if direction == 'fwd':
        route_draft = data['fwdTrackGeom'].split("(")
    else:
        route_draft = data['bkwdTrackGeom'].split("(")
    route_dict_ways = []
    for item in route_draft:
        if len(item) < 18:
            continue
        item = item.replace(')', '')
        way_list = []
        for point in item.split(", "):
            if len(point) < 3:
                continue
            coords = point.split(" ")
            lat = coord_to_int(coords[0])
            lon = coord_to_int(coords[1])
            way_list.append({"lat": lat, "lon": lon})
        route_dict_ways.append(way_list)
    return route_dict_ways

def detect_path_square(paths_list: list = False):
    """
    Defines the extreme northeast and southwest points of the path segment
    Attention! For simplicity, it is calculated only for the northern hemisphere and east longitude.
    # TODO: Make for the whole geosphere
    :param point_list: List with path geometry
    :return: list with two items:
     0 - extrime SW points
     1- extrime NE points
    """
    squares = []
    for point_list in paths_list:
        path_square = [{'lat': 90000000, 'lon': 180000000}, {'lat': 0, 'lon': 0}]
        for point in point_list:
            for coordinate_type in ['lat', 'lon']:
                if point[coordinate_type] < path_square[0][coordinate_type]:\
                    path_square[0][coordinate_type] = point[coordinate_type]
                if point[coordinate_type] > path_square[1][coordinate_type]:
                    path_square[1][coordinate_type] = point[coordinate_type]
        squares.append({'start_lat': point_list,
                        'start_lon': point_list,
                        'end_lat': point_list,
                        'end_lon': point_list,
                            path_square})
    return path_square


def pull_route_stations(route_id: str = '02', direction : str = 'fwd'):
    stoppoints_list = []
    data = load_route_data(route_id=route_id)
    if direction == 'fwd':
        stoppings_draft = data['fwdStoppoints']
    else:
        stoppings_draft = data['bkwdStoppoints']
    for station in stoppings_draft:
        location = station['location'].replace("POINT (", "").replace(")", "")
        lat, lon = location.split(" ")
        if 'note' in station:
            station_note = station['note']
        else:
            station_note = ""
        temp_dict = {'station_id': station['stoppointId'],
                     'station_name': station['stoppointName'],
                     'lat': coord_to_int(lat),
                     'lot': coord_to_int(lon),
                     'station_note': station_note,
                     }
        stoppoints_list.append(temp_dict)
    return stoppoints_list


def main_logic():
    client = MongoClient()
    db = client.ctrans
    routes = db.routes
    stations = db.stations
    path = db.paths
    for route in ROUTES_IDS:
        # Parse busstops data
        route_data['stations_fwd'] = pull_route_stations(route_id=route, direction="fwd")
        route_data['stations_bkwd'] = pull_route_stations(route_id=route, direction="bkwd")
        # Parse routers data
        route_data = pull_route_info(route_id=route)
        if not route_data:
            continue
        route_data['geometry_fwd'] = pull_route_geometry(route_id=route, direction="fwd")
        route_data['geometry_bkwd'] = pull_route_geometry(route_id=route, direction="bkwd")

        route_data['path_squares_fwd'] = detect_path_square([route_data['geometry_fwd'][0], route_data['geometry_fwd'][1]])
    #     routes.insert_one(route_data)
    return 0


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    exit(main_logic())
