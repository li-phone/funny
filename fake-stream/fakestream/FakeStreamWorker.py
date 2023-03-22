import time
from abc import ABC

from funnytools.abstract_parallel import AbstractParallel

from util.db_util import *
from util.log_util import LOGGER, fileftime, write_txt


def dump_log(line, log_path=f'logs/{fileftime()}.log'):
    write_txt(log_path, line)


class FakeStreamWorker(AbstractParallel, ABC):
    def __init__(self, log_func, regex_params, batch_size, **kwargs):
        super().__init__(**kwargs)
        self.print_log = log_func
        self.regex_params = regex_params
        self.batch_size = batch_size
        self.host = None
        self.dbname = None
        self.fix_val = None
        self.speed = None
        self.workers_num = 1
        self.table_names = None
        self.connection = None
        self.run_flag = None
        self.table_map = None

    def update_params(self, run_params):
        for k, v in run_params.items():
            self.__setattr__(k, v)

    def create_task(self):
        return list(range(self.workers_num))

    def process_task(self, task, **kwargs):
        sleep_time = 0
        self.table_map = {}
        while True:

            if self.run_flag is False:
                break

            if sleep_time > 0:
                time.sleep(0.1)
                sleep_time -= 0.1
                sleep_time = min(sleep_time, self.speed)
                continue

            success_cnt, failure_cnt = 0, 0
            try:
                if self.connection is not None and len(self.table_map) == 0:
                    for table in self.table_names:
                        table_names = exec_sql(f"show tables like '{table}'", self.connection, reshape=True)
                        for table_name in table_names:
                            self.table_map[table_name] = update_table(
                                exec_sql(f"desc {table_name}", self.connection, reshape=False), self.regex_params)
                for k, v in self.table_map.items():
                    records = []
                    for b in range(self.batch_size):
                        record = fill_table(v, self.regex_params, self.host, self.dbname, k, default_regex=self.fix_val)
                        records.append(record)
                    ret, res = add(records, k, self.connection, freq=len(records))
                    if ret:
                        success_cnt += len(records)
                    else:
                        failure_cnt += len(records)
                    for line in res:
                        self.print_log(LOGGER.info(f'execute sql "{line}"'))
            except Exception as e:
                failure_cnt += self.batch_size
                self.print_log(LOGGER.error(e.args))
                self.print_log(LOGGER.error(f'execute failure!'))

            self.print_log(LOGGER.info(f'insert {success_cnt + failure_cnt} records in {self.speed} seconds'))
            self.print_log(LOGGER.info(f'success {success_cnt}, failure {failure_cnt}'))

            if sleep_time <= 0:
                sleep_time = self.speed
