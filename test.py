# just use for test python run with jenkins

import time


def get_test_time():
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return now_time


if __name__ == '__main__':
    print(get_test_time())
