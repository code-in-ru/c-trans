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

HTTP_CLIENT_IDLE = 1000  # In msec
HTTP_MAX_ERRORS = 5

DATE_FORMAT = "%d.%m.%Y"

ROUTES_IDS = ("01", "02", "03", "802", "807")
ROUTES_IDS = ("01", )
COORDS_ACCURACY = 6 # Number digits after dot


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
    return out_data

def load_bus_data(bus_id: str = '01', timestamp: int = round(time.time())):
    # http://www.map.gortransperm.ru/json/get-moving-autos/-804-?_=1604081243508
    # http://www.map.gortransperm.ru/json/get-moving-autos/-807-?_=1604081243514
    # 'n': 58.0047916, 'e': 56.1856949,
    data = __get_data('get-moving-autos/-{0}-'.format(bus_id), {"_": timestamp})
    for bus in data['autos']:
        print(bus)
    return data

def main_logic():
    print(load_bus_data(bus_id="01"))
    # {'sw_lon': {$lte: 58004791}, 'ne_lon': {$gte: 58004791}, 'sw_lat': {$lte: 56185694}, 'ne_lat': {$gte: 56185694}}

if __name__ == '__main__':
    exit(main_logic())