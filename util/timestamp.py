import time

time.time()


def get_current_time():
    t = time.time()
    return int(round(t * 1000))
