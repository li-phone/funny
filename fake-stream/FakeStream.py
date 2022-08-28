import json
import os
import os.path as osp
from abc import ABC

import pymysql
from funnytools.abstract_parallel import AbstractParallel

from db_utils import *


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
        return None


def write_bin(path, content):
    try:
        mkdirs(path)
        with open(path, 'w', encoding='utf-8') as fp:
            json.dump(content, fp)
    except Exception as e:
        return None


def connect(connect_str, password=None):
    try:
        return pymysql.connect(**parse_connect(connect_str, password),
                               cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        return None


class FakeStreamWorker(AbstractParallel, ABC):
    def __init__(self, logTC, **kwargs):
        super().__init__(**kwargs)
        self.logTC = logTC
        self.workers_num = 1
        self.connection = None
        self.fix_val = None
        self.time_offset = None
        self.speed = None
        self.table_names = None
        self.run_flag = None
        self.table_map = None

    def update_params(self, run_params):
        for k, v in run_params.items():
            self.__setattr__(k, v)

    def create_task(self):
        return list(range(self.workers_num))

    def show_log(self, line):
        logs = self.logTC.GetValue() + f'{line}\n'
        if logs.count('\n') > 3000:
            logs = logs[len(logs) // 2:]
        self.logTC.SetValue(logs)
        self.logTC.ShowPosition(self.logTC.GetLastPosition())

    def process_task(self, task, **kwargs):
        sleep_time = 0
        self.table_map = {}
        while True:
            if self.run_flag is False:
                self.show_log(f'[INFO] {strftime()} Stop success.')
                break
            if sleep_time > 0:
                time.sleep(0.1)
                sleep_time -= 0.1
                sleep_time = min(sleep_time, self.speed)
                continue
            add_cnt = 0
            try:
                if self.connection is not None and len(self.table_map) == 0:
                    for table in self.table_names:
                        table_names = exec_sql(f"show tables like '{table}'", self.connection, reshape=True)
                        for table_name in table_names:
                            self.table_map[table_name] = get_dtypes(
                                exec_sql(f"desc {table_name}", self.connection, reshape=False))
                for k, v in self.table_map.items():
                    fs = set_dtypes(v, self.time_offset, self.fix_val)
                    res = add([fs], k, self.connection, freq=1)
                    add_cnt += 1
                    write_txt(f'logs/{fileftime()}.log', f'[INFO] {strftime()} Execute "{res[0]}"\n')
            except Exception as e:
                self.show_log(f'[INFO] {strftime()} Execute failure!')
            self.show_log(f'[INFO] {strftime()} Insert {add_cnt} records / {self.speed} seconds.')
            if sleep_time <= 0:
                sleep_time = self.speed
