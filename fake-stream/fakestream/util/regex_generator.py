import itertools as it
import time

from faker import Faker
from xeger import Xeger

LAUNCH_TIME = time.time()

fake = Faker("zh_CN")

ANY_HEAD = '::'
FAKER_HEAD = 'Faker::'
XEGER_HEAD = 'Xeger::'


def xeger_generate(reg_str, limit=10):
    if not limit:
        limit = 10
    x = Xeger(limit=limit)
    x._alphabets['whitespace'] = ' '  # 重定义空白字符为空格
    x._cases['any'] = lambda x: '.'  # 重定义任意字符为.
    result = x.xeger(reg_str)
    return result


def generate_sorted_keys(keys):
    new_keys = []
    bits = list(it.product(range(2), repeat=len(keys)))
    for bit in bits:
        find_keys = [keys[i] if b == 0 else '*' for i, b in enumerate(bit)]
        new_keys.append('.'.join(find_keys))
    return new_keys


def regex_generate(regex_params, keys, limit, default_regex=None):
    value = None
    if default_regex:
        value = xeger_generate(default_regex, limit)

    if not regex_params:
        return value

    sorted_keys = generate_sorted_keys(keys)
    for key in sorted_keys:
        if key in regex_params:
            regex_value = regex_params[key]
            if regex_value[:len(FAKER_HEAD)] == FAKER_HEAD:
                value = str(eval(regex_value[len(FAKER_HEAD):]))
            elif regex_value[:len(ANY_HEAD)] == ANY_HEAD:
                value = str(eval(regex_value[len(ANY_HEAD):]))
            else:
                value = xeger_generate(regex_value, limit)
            return value
    return None
