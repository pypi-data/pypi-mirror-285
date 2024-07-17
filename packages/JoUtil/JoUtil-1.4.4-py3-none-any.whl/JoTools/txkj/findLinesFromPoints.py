# -*- coding: utf-8  -*-
# -*- author: jokker -*-


import math
from collections import Counter
import matplotlib.pyplot as plt
import random
import numpy as np
from sklearn.cluster import DBSCAN


"""
* 对于一个点 p ，得到点与其他点之间的角度众数
* 找到与这个点角度众数相差一定范围内的点集 A
* 使用最小二乘法找到点集 A 的直线方程 f(x) ，作为点 p 的描述方程
* 将所有点的描述方程 y = ax +b 中的 a, b 进行聚类，b 需要作压缩（log10(b)）
* 对于每一类，找到类中方程对应的原始点，对这些点用最小二乘法找到描述方程，即为需要的直线方程
"""


class FindLinesFromPoints(object):
    """从点中找到直线"""

    def __init__(self):
        self.points = set()
        self.mode_angle = {}            # 每一个点的众方向
        self.mode_point_equation = {}   # 每一个点的最大可能方向方程
        self.equation_point_num = 5     # 众点集得到方程中点个数阈值
        self.mode_angle_threshold = 2   # 与众方向角度阈值
        self.eps = 1                    # 聚类的参数
        self.min_cluser_num = 3         # 最小的聚类的个数
        self.lines = {}                 # 找到的直线
        self.angle_range_find_mode_angle = 2    # 当寻找众角度时候，采取的卷积范围， 2 代表 [-2,-1,0,1,2] 这五个角度范围
        self.cluser_dict = {}                   # 每一个直线方程聚类的情况

    @staticmethod
    def get_loop_angle(i):
        """范围是 -90 - 90 过界了，就循环"""
        res = (i + 90) % 180 - 90
        return res

    @staticmethod
    def get_angle_diss(angle_1, angle_2):
        """计算两个角度之间的差异"""
        angle_1 = FindLinesFromPoints.get_loop_angle(angle_1)
        angle_2 = FindLinesFromPoints.get_loop_angle(angle_2)

        # 两个角度都转为 0 - 180 的形式
        if angle_1 < 0:
            angle_1 += 180

        if angle_2 < 0:
            angle_2 += 180

        # 计算两个角度的差异，与各自与坐标轴的差异之和哪个比较大
        cha_1 = abs(angle_1 - angle_2)
        cha_2 = 180 - max(angle_1, angle_2) + min(angle_1, angle_2)
        return min(cha_1, cha_2)

    @staticmethod
    def get_angle_from_two_point(point_1, point_2):
        """得到两个点组成的矢量与x轴之间的角"""
        point_vector = (point_1[0] - point_2[0], point_1[1] - point_2[1])
        if point_vector[0] == 0:
            return 90
        elif point_vector[1] == 0:
            return 0
        else:
            return math.degrees(math.atan(point_vector[1] / point_vector[0]))

    @staticmethod
    def find_angle_range(angle_counter:Counter, angle_range=1):
        """找到角度范围，能覆盖传入的绝大多角度"""
        angle_list = []
        for i in range(-90, 91):
            angle_sum = 0
            for j in range(-angle_range, angle_range+1):
                angle_sum += angle_counter[FindLinesFromPoints.get_loop_angle(i+j)]
            angle_list.append(angle_sum)
        return angle_list

    @staticmethod
    def get_gauss_core(length=5, sigma=3):
        """获得一维高斯核函数"""
        mid = int(length / 2)
        result = [(1 / (sigma * np.sqrt(2 * np.pi))) * (1 / (np.exp((i ** 2) / (2 * sigma ** 2)))) for i in
                  range(-mid, mid + 1)]
        # plt.scatter(range(len(result)), result, c='b')
        # plt.show()
        return result

    @staticmethod
    def find_mode_angle(angle_list, angle_range=5):
        """遍历点，的方式来找到众角度"""
        gass_core = FindLinesFromPoints.get_gauss_core(2 * angle_range + 1)
        angle_array = np.zeros((180), np.float)
        for each_angle in angle_list:
            for index, each_offset in enumerate(range(-angle_range, angle_range + 1)):
                each_angle_assign = FindLinesFromPoints.get_loop_angle(int(each_angle) + each_offset) + 90
                angle_array[each_angle_assign] += gass_core[index]

        angle_list = list(angle_array)
        index = angle_list.index(max(angle_list))
        return index - 90

    @staticmethod
    def least_square_method(points):
        """最小二乘法拟合直线"""
        x, y = zip(*points)
        paras = np.polyfit(x, y, deg=1)
        return paras[0], paras[1]

    @staticmethod
    def cluser_saptial_point(points, eps, min_samples= 3):
        """空间点的聚类"""
        res = {}
        point_type = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(points)
        #
        for point_index, each_point in enumerate(points):
            each_type = point_type[point_index]
            if each_type in res:
                res[each_type].append(each_point)
            else:
                res[each_type] = [each_point]
        return res

    @staticmethod
    def draw_line_in_rect(x_max, y_max, a, b):
        """"在一个矩形上画直线"""
        points = []
        if a == 0:
            a =-9.310639696752773e-16

        for each_point in [(0, b), (-b / a, 0), ((y_max - b) / a, y_max), (x_max, a * x_max + b)]:
            if (0 <= each_point[0] <= x_max) and (0 <= each_point[1] <= y_max):
                points.append(each_point)
        if len(points) >= 2:
            x, y = zip(*points)
            plt.plot(x, y, color='red')

    @staticmethod
    def get_rand_color(mode='RGB'):
        """得到随机的颜色"""
        if mode.upper() == 'RGB':
            return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        elif mode.upper() == 'GRAY':
            value_uint8 = random.randint(0, 255)
            return value_uint8, value_uint8, value_uint8

    # --------------------------------------------------------------------
    def do_normalization(self):
        """点数据进行标准化"""
        # todo 将点的 x 轴，标准化到 0-1 ， y 轴做相应的变换
        point_x, point_y = zip(*self.points)
        min_x, max_x = min(point_x), max(point_x)
        ratio = (max_x - min_x)

        new_points = []
        for each_point in self.points:
            each_new_point = (each_point[0]/ratio, each_point[1]/ratio)
            new_points.append(each_new_point)
        self.points = new_points

    def get_mode_equation(self):
        """得到一个点的众方向"""
        for each_point_1 in self.points:
            angle_list = []
            points = self.points.copy()
            # 去掉代表自己的点
            points.remove(each_point_1)
            # -------------------------------- 找到众方向 -------------------------------------
            for each_point_2 in points:
                each_angle = self.get_angle_from_two_point(each_point_1, each_point_2)
                angle_list.append(each_angle)
            # 找到众角度
            mode_angle = self.find_mode_angle(angle_list, self.angle_range_find_mode_angle)
            self.mode_angle[each_point_1] = mode_angle
            # -------------------------------- 找到众点集 -------------------------------------
            # 找到在主方向上的点
            need_points = []
            for each_point_2 in points:
                each_angle = self.get_angle_from_two_point(each_point_1, each_point_2)
                if self.get_angle_diss(each_angle, mode_angle) < self.mode_angle_threshold:
                    need_points.append(each_point_2)
            if len(need_points) < self.equation_point_num:
                print(need_points)
                continue
            else:
                # 得到点的方程
                param_a, param_b = FindLinesFromPoints.least_square_method(need_points)
                self.mode_point_equation[(param_a, param_b)] = each_point_1

    def find_lines_by_cluser(self):
        """使用方程聚类，得到点"""
        points = list(self.mode_point_equation.keys())

        if len(points) == 0:
            return

        res = self.cluser_saptial_point(points, self.eps, min_samples=self.min_cluser_num)
        self.cluser_dict = res
        #
        for class_index, each_class in enumerate(res):
            # 去掉孤点
            if each_class == -1:
                continue
            on_line_points = []
            for each_equation in res[each_class]:
                each_point = self.mode_point_equation[each_equation]
                on_line_points.append(each_point)
            #
            if len(on_line_points) >= self.equation_point_num:
                param_a, param_b = self.least_square_method(on_line_points)
                self.lines[(param_a, param_b)] = on_line_points

    def draw_res(self):
        """画出结果"""

        if len(self.points) < 1:
            return

        point_x, point_y = zip(*self.points)
        plt.scatter(point_x, point_y, c='black')

        for line_index, each_line in enumerate(self.lines):
            # each_color = color[line_index]
            points = self.lines[each_line]
            point_x, point_y = zip(*points)
            # plt.scatter(point_x, point_y, c=each_color)
            self.draw_line_in_rect(max(point_x), max(point_y), each_line[0], each_line[1])
        plt.axis('equal')
        plt.show()

    def draw_cluser(self):
        """画出聚类"""
        # todo 画出每一类的聚类
        points = list(self.mode_point_equation.keys())

        if len(points) == 0:
            return

        for each_class in self.cluser_dict:
            if each_class == -1 or len(self.cluser_dict[each_class]) < self.min_cluser_num:
                continue
            each_color = "bgrcmykw"[random.randint(0, 6)]
            for each_point in self.cluser_dict[each_class]:
                # 随机分配一个颜色
                plt.scatter(each_point[0], each_point[1], c=each_color)
        plt.show()

    def compose_parameter(self, func):
        """对参数进行压缩"""
        new_mode_point_equation = {}
        for each in self.mode_point_equation:
            each_new = func(each)
            new_mode_point_equation[each_new] = self.mode_point_equation[each]
        self.mode_point_equation = new_mode_point_equation

    def test(self):
        """一些点的测试"""
        a = FindLinesFromPoints()
        a.eps = 0.3
        a.mode_angle_threshold = 4
        a.equation_point_num = 3
        a.min_cluser_num = 3
        a.angle_range_find_mode_angle = 4
        a.points = {
            (1, 1.01), (2, 2.04), (3, 3.1), (4, 4.04), (5, 5), (6, 6), (7, 7.5), (8, 8.2),
            (1, 9), (2, 8), (3, 7), (4, 6), (5, 5), (6, 4), (7, 3), (8, 2), (9, 1),
            (1, 5.5), (2, 5.5), (3, 5.5), (4, 5.5), (5, 5.5), (6, 5.5),
            (1, 1.5), (2, 3), (3, 4.5), (4, 6), (5, 7.5), (6, 9), (7, 10.5), (8, 12),
            (8, 8.8), (5, 3.1), (5, 9),
        }

        # a.points = {
        #     (485, 241),
        #     (534, 303),
        #     (518, 279),
        #     }

        # a.do_normalization()
        a.get_mode_equation()
        # a.compose_parameter(compose_by_log)
        a.find_lines_by_cluser()
        a.draw_cluser()
        a.draw_res()

    def do_process(self):
        """主要流程"""
        # 得到每个点的众数方程
        self.get_mode_equation()
        # 聚类得到线
        self.find_lines_by_cluser()
        # 画出结果
        self.draw_cluser()
        self.draw_res()


def compose_by_log(each):
    """使用 log 函数进行压缩"""
    if each[1] > 0:
        each_new = (each[0], math.log10(each[1]))
    else:
        each_new = (each[0], -math.log10(abs(each[1])))
    return each_new


if __name__ == "__main__":

    # fixme 解决每一个点只能出现在一类中的问题，一个点可以出现在多条直线中

    a = FindLinesFromPoints()
    a.eps = 0.3
    a.mode_angle_threshold = 2
    a.equation_point_num = 4
    a.min_cluser_num = 4
    a.angle_range_find_mode_angle = 2
    a.points = {
        (1, 1.01), (2, 2.04), (3, 3.1), (4, 4.04), (5, 5), (6, 6), (7, 7.5), (8, 8.2),
        (1, 9), (2, 8), (3, 7), (4, 6), (5, 5), (6, 4), (7, 3), (8, 2), (9, 1),
        (1, 5.5), (2, 5.5), (3, 5.5), (4, 5.5), (5, 5.5), (6, 5.5),
        (1, 1.5), (2, 3), (3, 4.5), (4, 6), (5, 7.5), (6, 9), (7, 10.5), (8, 12),
        (8, 8.8), (5, 3.1), (5, 9),
    }

    a.do_process()





