import hashlib
import json
import os.path
import threading
import time

from progress.bar import ShadyBar

__version__ = '1.0.0'
"""
v1.0.0: 1. 记录失败任务并且添加失败重试机制
"""


class Parallel(object):
    """
        使用多线程去完成多任务资源的处理
        参数：
            tasks：任务资源
            process：处理过程函数
            collect：需要收集的数据
            workers_num：线程数量
            with_thread_lock：是否对线程加锁
            process_params：处理过程参数
            print_process：打印进度频率
            go_on：是否继续上次失败的任务
            max_fail_times：最大失败重试次数
        返回：
            返回results [dict]
    """

    def __init__(self, tasks, process, collect=None, workers_num=1, with_thread_lock=True, process_params=None,
                 print_process=True, go_on=False, max_fail_times=3):
        self.init_tasks = tasks
        self.task_size = len(tasks)
        self.process = process
        self.collect = [] if collect is None else collect
        self.workers_num = workers_num
        self.with_thread_lock = with_thread_lock
        self.process_params = {} if process_params is None else process_params
        self.print_process = print_process
        self.thread_lock = threading.Lock() if self.with_thread_lock else None
        self.results = {k: [] for k in self.collect}
        self.failed_tasks = {}
        self.failed_tasks_path = '.parallel.failed_tasks.json'
        if go_on and os.path.exists(self.failed_tasks_path) and os.path.isfile(self.failed_tasks_path):
            with open(self.failed_tasks_path) as fp:
                failed_tasks = json.load(fp)
                self.init_tasks = [v['object'] for k, v in failed_tasks.items()]
        self.max_fail_times = max(1, max_fail_times)
        self.bar = ShadyBar('Processing', max=self.task_size, suffix='%(percent).1f%% [%(elapsed_td)s / %(eta_td)s]')

    def do_work(self):
        while len(self.init_tasks) > 0:
            # 取一个任务
            if self.with_thread_lock:
                with self.thread_lock:
                    if len(self.init_tasks) > 0:
                        if isinstance(self.init_tasks, dict):
                            task = self.init_tasks.popitem()
                        else:
                            task = self.init_tasks.pop()
                    else:
                        break
            else:
                if len(self.init_tasks) > 0:
                    if isinstance(self.init_tasks, dict):
                        task = self.init_tasks.popitem()
                    else:
                        task = self.init_tasks.pop()
                else:
                    break
            try:
                result = self.process(task, lock=self.thread_lock, __results__=self.results, **self.process_params)
                if self.with_thread_lock:
                    with self.thread_lock:
                        if isinstance(result, dict):
                            for k, v in result.items():
                                if isinstance(v, list):
                                    self.results[k].extend(v)
                                else:
                                    self.results[k].append(v)
                else:
                    if isinstance(result, dict):
                        for k, v in result.items():
                            if isinstance(v, list):
                                self.results[k].extend(v)
                            else:
                                self.results[k].append(v)
            except Exception as e:
                sha1_key = hashlib.sha1(str(task).encode('utf-8')).hexdigest()
                if sha1_key in self.failed_tasks:
                    self.failed_tasks[sha1_key]['count'] += 1
                else:
                    self.failed_tasks[sha1_key] = dict(object=task, count=1)
                if self.failed_tasks[sha1_key]['count'] < self.max_fail_times:
                    if isinstance(self.init_tasks, dict):
                        self.init_tasks[task[0]] = task[1]
                    elif isinstance(self.init_tasks, list):
                        self.init_tasks.append(task)
                    else:
                        self.init_tasks.add(task)
                    continue
            if self.print_process:
                self.bar.next()
        self.bar.finish()

    def __call__(self, print_info=True, **kwargs):
        threads = [threading.Thread(target=self.do_work, name=f"{self.__class__.__name__}-Thread-{i}")
                   for i in range(self.workers_num)]
        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        end = time.time()
        if print_info:
            print(f'[*] Success: {self.task_size - len(self.failed_tasks)}, Failure: {len(self.failed_tasks)}')
            print(f'[*] Elapsed time: {end - start} s')
        if len(self.failed_tasks) != 0:
            with open(self.failed_tasks_path, 'w') as fp:
                json.dump(self.failed_tasks, fp)
        return self.results
