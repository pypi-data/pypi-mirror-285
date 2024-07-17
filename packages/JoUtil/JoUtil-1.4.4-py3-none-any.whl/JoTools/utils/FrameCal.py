# -*- coding: utf-8  -*-
# -*- author: jokker -*-


# todo 建立一个定长列表数组，实时计算帧率，可以设置定长数组的大小


import time



class FrameCal():

    def __init__(self, length):
        self.length = length
        self.time_list = []

    def tag(self):
        if len(self.time_list) == self.length:
            self.time_list.pop(0)
        self.time_list.append(time.time())

    def get_frame(self):
        if len(self.time_list) <= 1:
            return -1
        else:
            start = self.time_list[0]
            end = self.time_list[-1]
            if start == end:
                return -1
            else:
                return (len(self.time_list) -1)/(time.time() - self.time_list[0])


if __name__ == "__main__":

    a = FrameCal(100)

    for i in range(10000):
        time.sleep(0.2)
        a.tag()
        print(a.get_frame())







































