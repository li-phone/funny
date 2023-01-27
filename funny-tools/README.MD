Funny-Tools
===========
> A funny tools for parallel processing tasks by threading.

Install
-------
Just run `install.sh` script that OK.

```
> sh install.sh
```

Usage
-----

* By inheritance

```
from abc import ABC
from funnytools.abstract_parallel import AbstractParallel

class AbstractParallelTest(AbstractParallel, ABC):
    def create_task(self):
        return list(range(100))

    def process_task(self, task, **kwargs):
        print(task)

# print list from 0 to 99
parallel = AbstractParallelTest()
parallel()
```

* By callback function

```
from funnytools.parallel import Parallel

def process(task, **kwargs):
    print(task)
    return {'task': 'task' + str(task)}

# print list from 0 to 99 and collect this results
settings = dict(tasks=list(range(100)), collect=['task'], process=process)
parallel = Parallel(**settings)
result = parallel()
assert 'task' in result and len(result['task']) == 100
```

Release logs
------------

#### V1.0.0 at 2022/08/28

* With go on last task and max fail try times.
* With progress bar.
