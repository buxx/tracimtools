# coding: utf-8
import datetime
import time


def str_time_to_timestamp(str_time: str) -> int:
    return time.mktime(
        datetime.datetime.strptime(
            str_time,
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ).timetuple()
    )
