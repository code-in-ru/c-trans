# This module collects iformation about moving the buses. It is using the bustime.ru API

import http.client
import logging
import json
from urllib.parse import urlencode
import hashlib
import os
import time
from datetime import date


API_HOST = "www.map.gortransperm.ru"
API_PATH = "/json/"
API_REQUEST_RATE = 60  # Per minute
CACHE_TIME = 15  # In seconds
CACHE_DIR = "cache/"
CACHE_EXT = ".cache"

HTTP_CLIENT_IDLE = 1000  # In msec
HTTP_MAX_ERRORS = 5

DATE_FORMAT = "%d.%m.%Y"


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
    print(path_need_data)
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


def load_routes_list(for_date=date.today()):
    # http://www.map.gortransperm.ru/json/route-types-tree/30.10.2020/
    data = __get_data('route-types-tree/{0}/'.format(for_date.strftime(DATE_FORMAT)))
    print(data)

def load_bus_data(bus_id: int = 12970):
    data = __get_data('/bus/', {"bus_id": bus_id})
    print(data)
    data = __get_data('/route_line/', {"bus_id": bus_id})
    print(data)

def pull_metric_data():
    topics = ["""{
    "metric": "catplace",
    "value": 1,
    "_": 1603983781180
    }"""]
    start_socket_client("wss://www.bustime.ru/ajax/metric", topics)
    # start_socket_client("https://www.bustime.ru/ajax/metric", topics)


def main_logic():
    load_routes_list()
    return 0


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    exit(main_logic())
