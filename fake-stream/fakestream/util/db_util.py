import datetime
import getpass
from datetime import datetime

import pymysql
import regex as re

from .regex_generator import regex_generate


def add(records, table_name, connect, freq=10000):
    ret, logs = False, []
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
                ret = True
            except Exception as e:
                logs.append(e.args)
                connect.rollback()
    return ret, logs


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
    user, host, port, database = re.findall(r'([-|\w]+)@([\d|-|\.|\w]+):(\d+)/([-|\w]+)', string)[0]
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


def reg_word(string):
    it = re.finditer(r'(\w+)', string)
    for m in it:
        match = m
        return match.group(0)
    return string


def update_table(table, regex_params, **kwargs):
    return table


def fill_table(table, regex_params, host, dbname, tbl_name, default_regex=None, **kwargs):
    d = {}
    for i, v in enumerate(table):
        name, value = v['Field'], None
        if v['Extra'].lower() == 'auto_increment':
            continue
        elif v['Null'] == 'YES':
            value = None
        elif v['Null'] == 'NO':
            value = v['Default']
        else:
            value = ''
        type_length = str2num(v['Type'])
        keys = [v['Field'], tbl_name, dbname, str(host).replace('.', '-'), reg_word(v['Type'])]
        regex_value = regex_generate(regex_params, keys, type_length, default_regex=default_regex)
        if regex_value:
            value = regex_value
        if type_length:
            value = str(value)[:type_length]
        d[name] = value
    return d


def connect(connect_str, password=None):
    try:
        return pymysql.connect(**parse_connect(connect_str, password),
                               cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        return None
