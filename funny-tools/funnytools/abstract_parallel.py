import abc

from .parallel import Parallel

__version__ = '1.0.0'
"""
v1.0.0: 1. 记录失败任务并且添加失败重试机制
        2. 添加是否阻塞线程开关
        3. 允许动态更新内部参数
"""


class AbstractParallel(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_task(self): pass

    @abc.abstractmethod
    def process_task(self, task, **kwargs): pass

    def __init__(self, *args, **kwargs):
        self.parallel = None
        self.para_args = args
        self.para_kwargs = kwargs

    def __call__(self, *args, **kwargs):
        if self.parallel is not None:
            return
        settings = dict(tasks=self.create_task(), process=self.process_task, *self.para_args, **self.para_kwargs)
        self.parallel = Parallel(**settings)
        return self.parallel(**kwargs)
