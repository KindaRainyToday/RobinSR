import time


def cur_timestamp_ms() -> int:
    return int(time.time() * 1000)


def cur_timestamp_secs() -> int:
    return int(time.time())
