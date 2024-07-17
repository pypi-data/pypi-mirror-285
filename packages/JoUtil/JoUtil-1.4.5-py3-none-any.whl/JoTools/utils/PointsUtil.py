# -*- coding: utf-8  -*-
# -*- author: jokker -*-


import numpy as np
import cv2


class PointsUtil(object):

    @staticmethod
    def get_left_point(points):
        """找到最左边的点"""
        points = sorted(points, key=lambda point:point[0])
        return points[0]

    @staticmethod
    def get_right_point(points):
        """找到最右边的点"""
        points = sorted(points, key=lambda point:point[0], reverse=True)
        return points[0]

    @staticmethod
    def get_top_point(points):
        """找到最上边的点"""
        points = sorted(points, key=lambda point:point[1], reverse=True)
        return points[0]

    @staticmethod
    def get_bottom_point(points):
        """找到最下边的点"""
        points = sorted(points, key=lambda point:point[1])
        return points[0]

    @staticmethod
    def get_bounding_rect(points):
        """获的正外接矩形的四个点"""
        left = PointsUtil.get_left_point(points)
        right = PointsUtil.get_right_point(points)
        bottom = PointsUtil.get_bottom_point(points)
        top = PointsUtil.get_top_point(points)
        return [left, right, bottom, top]

    @staticmethod
    def bounding_rect_middle_line(points, long_line=True):
        """外接矩形的中心点连线，分长边和短边"""
        points = np.array(points)
        x, y, w, h = cv2.boundingRect(points)
        # (x,y) 左上角的点
        if ((w > h) and long_line) or ((w < h) and (not long_line)) :
            line = [(x, y+h/2), (x+w, y+h/2)]
        else:
            line = [(x+w/2, y), (x+w/2, y+h)]
        return line

    @staticmethod
    def get_line_from_points(points):
        """从一系列点中得到拟合的直线"""
        data_x, data_y = zip(*points)
        m = len(data_y)
        x_bar = np.mean(data_x)
        sum_yx = 0
        sum_x2 = 0
        sum_delta = 0
        for i in range(m):
            x = data_x[i]
            y = data_y[i]
            sum_yx += y * (x - x_bar)
            sum_x2 += x ** 2
        # 根据公式计算w
        w = sum_yx / (sum_x2 - m * (x_bar ** 2))
        for i in range(m):
            x = data_x[i]
            y = data_y[i]
            sum_delta += (y - w * x)
        b = sum_delta / m
        return w, b

    @staticmethod
    def get_fit_line(points):
        """输入点集，获得拟合线，输出一个拟合的线段"""
        w, b = PointsUtil.get_line_from_points(points)
        points = sorted(points, key=lambda x:x[0])
        x_min, x_max = points[0][0], points[-1][0]
        y_1 = x_min*w + b
        y_2 = x_max*w + b
        return [(x_min, y_1), (x_max, y_2)]

    @staticmethod
    def LSC(xi, Yi):

        def func(p, x):
            k, b = p
            return k * x + b

        def error(p, x, y):
            return func(p, x) - y

        p0 = [100, 2]
        Para = leastsq(error, p0, args=(xi, Yi))
        k, b = Para[0]

        return k, b

    @staticmethod
    def get_line_from_points_2(points):
        """最小二乘法来做"""

        # fixme 最小二乘法是有缺陷的，对于斜率特别大的曲线，最小二乘法没办法得到准确的斜率，会得到一个有问题的斜率，我一般直接把 x,y 对调，得到斜率 k 再用 1/k 得到真正的斜率，

        xi, yi = [], []
        for each in points:
            xi.append(each[0])
            yi.append(each[1])
        xi = np.array(xi)
        yi = np.array(yi)
        # k, b = LSC(yi, xi)
        # k_new = 1 / k
        k, b = LSC(xi, yi)
        b = np.mean(xi)
        return k_new, b


if __name__ == "__main__":


    points = [(10,10), (100,100), (10,100), (100,10), (97,65), (122, 43), (50, 180)]

    # print(PointsUtil.get_left_point(points))
    # print(PointsUtil.get_right_point(points))
    # print(PointsUtil.get_top_point(points))
    # print(PointsUtil.get_bottom_point(points))


    # line = PointsUtil.bounding_rect_middle_line(points)
    #
    # # print(points)
    #
    # img = np.zeros((200,200, 3), dtype=np.uint8)
    #
    # for each_point in points:
    #     cv2.circle(img, (int(each_point[0]), int(each_point[1])), 5, [0,0,255], 2)
    #
    # cv2.circle(img, (int(line[0][0]), int(line[0][1])), 5, [255, 0, 255], 2)
    # cv2.circle(img, (int(line[1][0]), int(line[1][1])), 5, [255, 0, 255], 2)
    #
    # cv2.imwrite(r"C:\Users\14271\Desktop\xj_labelme.jpg", img)


    line = PointsUtil.get_fit_line(points)

