import unittest
from abc import ABC

from funnytools.abstract_parallel import AbstractParallel
from funnytools.parallel import Parallel


class AbstractParallelTest(AbstractParallel, ABC):
    def create_task(self):
        return list(range(100))

    def process_task(self, task, **kwargs):
        print(task)


class MyTestCase(unittest.TestCase):

    def test_abstract_parallel(self):
        parallel = AbstractParallelTest()
        parallel()
        self.assertEqual(True, True)  # add assertion here

    def test_parallel(self):
        def process(task, **kwargs):
            print(task)
            return {'task': 'task' + str(task)}

        settings = dict(tasks=list(range(100)), collect=['task'], process=process)
        parallel = Parallel(**settings)
        result = parallel()
        self.assertTrue('task' in result and len(result['task']) == 100)  # add assertion here


if __name__ == '__main__':
    unittest.main()
