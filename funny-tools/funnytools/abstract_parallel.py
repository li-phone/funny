import abc

from .parallel import Parallel

__version__ = '1.0.0'
"""
v1.0.0: 1. 记录失败任务并且添加失败重试机制
"""


class AbstractParallel(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_task(self): pass

    @abc.abstractmethod
    def process_task(self, task, **kwargs): pass

    def __init__(self, **kwargs):
        self.parallel = None
        self.parallel_params = kwargs

    def __call__(self, *args, **kwargs):
        settings = dict(tasks=self.create_task(), process=self.process_task, **self.parallel_params)
        self.parallel = Parallel(**settings)
        return self.parallel()
