# -*- coding: utf-8  -*-
# -*- author: jokker -*-

import time


class TimeUtil():

    @staticmethod
    def get_time_str(mk_time=None):
        # TimeUtil.get_time_str(1682318412.296638)
        # TimeUtil.get_time_str()
        if mk_time is None:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        else:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mk_time))

    @staticmethod
    def get_struct_time(time_str, str_format):
        # TimeUtil.get_time("2023-04-24 14:40:12", "%Y-%m-%d %H:%M:%S")
        return time.strptime(time_str, str_format)

    @staticmethod
    def get_mk_time(time_str, str_format):
        # TimeUtil.get_mk_time("2023-04-24 14:40:12", "%Y-%m-%d %H:%M:%S")
        return time.mktime(time.strptime(time_str, str_format))


if __name__ == "__main__":

    print(TimeUtil.get_time_str(1682318412.296638))
    print(TimeUtil.get_time_str())


    print(TimeUtil.get_struct_time("2023-04-24 14:40:12", "%Y-%m-%d %H:%M:%S"))
    print(TimeUtil.get_mk_time("2023-04-24 14:40:12", "%Y-%m-%d %H:%M:%S"))

