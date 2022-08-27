import datetime
import getpass
import random
import time
from datetime import datetime
from enum import Enum

import regex as re


class CharType(Enum):
    NUMBER = 1
    UPPER = 2
    LOWER = 3
    WORD = 4
    ALL = 5
    FIXED = 6


class DataType(Enum):
    INTEGER = 1
    FLOAT = 2
    TIMESTAMP = 3
    STRING = 4
    NONE = 5
    FIXED = 6


class BaseType(Enum):
    NUMBER = 1
    STRING = 2


def strftime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


def strftime2(time_offset=0):
    ts = time.time() + time_offset
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')


def fileftime():
    return datetime.now().strftime('%Y-%m-%d')


def logger(msg):
    print(f'[INFO] {strftime()}', msg)


def add(records, table_name, connect, freq=10000):
    logs = []
    with connect.cursor() as cursor:
        for i, record in enumerate(records):
            if not record:
                continue
            attrs = []
            values = []
            for k, v in record.items():
                attrs.append(k)
                if isinstance(v, datetime):
                    v = str(v)
                values.append(v)
            attrs = str(attrs)[1:-1].replace("'", "`")
            values = str(values)[1:-1]
            sql = f'INSERT INTO `{table_name}` ({attrs}) VALUES ({values})'
            logs.append(sql)
            try:
                result = cursor.execute(sql)
                if (i + 1) % freq == 0 or (i + 1) == len(records):
                    connect.commit()
            except Exception as e:
                logger(e.args)
                connect.rollback()
    return logs


def exec_sql(sql, connect, reshape=False):
    with connect.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
        if reshape:
            result = [[v for k, v in r.items()] for r in result]
            for i, r in enumerate(result):
                if len(r) == 1:
                    result[i] = r[0]
            return result
        return result


def parse_connect(string, password=None):
    user, host, port, database = re.findall(r'(\w+)@([\d|\.]+):(\d+)/(\w+)', string)[0]
    if password is None:
        password = getpass.getpass(f'Connecting to {string} ..., please input password>?')
    return dict(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
    )


def str2num(string, loc=False):
    it = re.finditer(r'(\d+)', string)
    match = None
    for m in it:
        match = m
    if match is None:
        return None
    if loc:
        return match.span(1)
    return int(match.group(1))


def random_char(category=CharType.NUMBER):
    if category == CharType.NUMBER:
        d = '0123456789'
    elif category == CharType.UPPER:
        d = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    elif category == CharType.LOWER:
        d = 'abcdefghijklmnopqrstuvwxyz'
    elif category == CharType.WORD:
        d = '-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
    elif category == CharType.FIXED:
        d = '6'
    else:
        d = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
    return d[random.randint(0, len(d) - 1)]


def random_data(data_type=DataType.STRING, size=0, time_offset=0, fix_val='6'):
    if data_type == DataType.INTEGER:
        x = ''.join([random_char(CharType.NUMBER) for i in range(max(size - 2, 1))])
        return int(x)
    elif data_type == DataType.FLOAT:
        if not isinstance(size, (list, tuple)):
            size = [size]
        x = ''.join([random_char(CharType.NUMBER) for i in range(size[0])])
        y = ''.join([random_char(CharType.NUMBER) for i in range(size[1])]) if len(size) > 1 else ''
        return float(f'{x}.{y}')
    elif data_type == DataType.TIMESTAMP:
        return strftime2(time_offset)
    elif data_type == DataType.STRING:
        return ''.join([random_char(CharType.WORD) for i in range(size)])
    elif data_type == DataType.FIXED:
        if fix_val is None or len(fix_val) == 0:
            fix_val = '6'
        fixed_str = fix_val * (size // len(fix_val) + 1)
        return fixed_str[:size]
    return 'null'


def get_dtype(v):
    length = str2num(v['Type'])
    if length is None:
        length = 0
    if v['Type'].lower().find('int') != -1:
        base_type, dtype = BaseType.NUMBER, DataType.INTEGER
    elif v['Type'].lower().find('long') != -1:
        base_type, dtype = BaseType.NUMBER, DataType.INTEGER
    elif v['Field'].lower() == 'uuid':
        base_type, dtype = BaseType.STRING, DataType.STRING
    elif v['Type'].lower().find('char') != -1:
        base_type, dtype = BaseType.STRING, DataType.FIXED
    elif v['Type'].lower().find('time') != -1:
        base_type, dtype, length = BaseType.STRING, DataType.TIMESTAMP, 29
    elif v['Type'].lower().find('text') != -1:
        base_type, dtype, length = BaseType.STRING, DataType.FIXED, 255
        logger(f"Warning! <text> type is too long default 255!")
    else:
        base_type, dtype = BaseType.STRING, DataType.NONE
        logger(f"Warning! Unseen type {v['Type']} default null!")
    v['dtype'] = dtype
    v['length'] = length
    v['base_type'] = base_type
    return v


def get_dtypes(table):
    for i, v in enumerate(table):
        table[i] = get_dtype(v)
    return table


def set_dtypes(table, time_offset=0, fix_val='6'):
    d = {}
    for i, v in enumerate(table):
        if v['Extra'].lower() == 'auto_increment':
            continue
        d[v['Field']] = random_data(v['dtype'], v['length'], time_offset, fix_val=fix_val)
    return d
