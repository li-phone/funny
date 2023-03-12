import json
import os
import os.path as osp
import time
from datetime import datetime
from enum import Enum


class LOGGER(Enum):
    INFO = 1
    WARN = 2
    ERROR = 3

    @staticmethod
    def info(line):
        return f'{strftime()} - {LOGGER.INFO.name} {line}\n'

    @staticmethod
    def warn(line):
        return f'{strftime()} - {LOGGER.WARN.name} {line}\n'

    @staticmethod
    def error(line):
        return f'{strftime()} - {LOGGER.ERROR.name} {line}\n'


def strftime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


def strftime2(time_offset=0):
    ts = time.time() + time_offset
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')


def fileftime():
    return datetime.now().strftime('%Y-%m-%d')


def logger(msg):
    print(f'[INFO] {strftime()}', msg)


def mkdirs(path):
    dirname = osp.dirname(path)
    if len(dirname) != 0 and not osp.exists(dirname):
        os.makedirs(dirname)


def write_txt(path, content):
    mkdirs(path)
    with open(path, 'a+', encoding='utf-8') as fp:
        fp.write(content)


def read_bin(path):
    try:
        with open(path, 'r', encoding='utf-8') as fp:
            return json.load(fp)
    except Exception as e:
        return {}


def write_bin(path, content):
    try:
        mkdirs(path)
        with open(path, 'w', encoding='utf-8') as fp:
            json.dump(content, fp)
    except Exception as e:
        pass
