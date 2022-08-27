import os
import os.path as osp

from db_utils import *


def mkdirs(path):
    if not osp.exists(osp.dirname(path)):
        os.makedirs(osp.dirname(path))


def write_txt(path, content):
    mkdirs(path)
    with open(path, 'a+', encoding='utf-8') as fp:
        fp.write(content)


def run(connect_str, tables, time_offset=0, password=None):
    import pymysql
    connection = pymysql.connect(**parse_connect(connect_str, password), cursorclass=pymysql.cursors.DictCursor)
    table_map = {}
    for table in tables:
        table_names = exec_sql(f"show tables like '{table}'", connection, reshape=True)
        for table_name in table_names:
            table_map[table_name] = get_dtypes(exec_sql(f"desc {table_name}", connection, reshape=False))
    try:
        freq = float(input('Please input frequency of generating one fake record data (seconds/record)>?'))
    except ValueError:
        freq = 60 * 5
        logger(f"Use default parameter: {freq}")
    while True:
        for k, v in table_map.items():
            fs = set_dtypes(v, time_offset)
            res = add([fs], k, connection, freq=1)
            # logger(f'exec {res[0]}')
            write_txt(f'logs/{fileftime()}.log', f'[INFO] {strftime()} execute "{res[0]}"\n')
        logger(f'Insert {len(table_map)} records / {freq} seconds.')
        time.sleep(freq)
