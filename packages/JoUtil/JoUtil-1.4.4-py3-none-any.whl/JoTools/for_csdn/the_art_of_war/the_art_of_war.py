#!D:\Anaconda\envs\python36_all
# -*- coding: utf-8  -*-
# -*- author: jokker -*-

import random
import time
import os

class TheArtOfWar(object):
    """孙子兵法"""

    def __init__(self):
        # 文件地址
        self._txt_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), r'./data/the_art_of_war.txt')
        self.fixed_interval_time = 3                            # 固定的间隔时间
        self.line_list = []                                     # 读取到的每一行组成的列表
        self._show_style = 0                                    # 显示的样式
        self.is_random = False                                  # 是不是随机显示内容
        self.is_auto = True                                     # 是不是在展示完一行后自动在间隔时间之后展示另外一行

    def show_lines(self):
        """打印每一行"""

        with open(self._txt_path, 'r', encoding='utf-8') as txt_file:
            self.line_list = ''.join(txt_file.readlines()).split('。')

        index = 0
        line_count = len(self.line_list)
        while True:
            # 是否自定
            if not self.is_auto:
                _ = input("")
            # 打印哪一行
            if self.is_random:
                index = random.randint(0, line_count-1)
            else:
                index = 0 if index >= line_count else index+1
            # 设定打印样式
            print(self.line_list[index])
            print("-"*100)

            # 睡眠时间
            time.sleep(self.fixed_interval_time)


if __name__ == "__main__":


    a = TheArtOfWar()
    a.fixed_interval_time = 0.2
    a.is_random = False
    a.is_auto = False
    a.show_lines()
