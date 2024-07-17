# -*- coding: utf-8  -*-
# -*- author: jokker -*-

import numpy as np
from scipy.interpolate import interp1d
from scipy.interpolate import interp2d
import matplotlib.pyplot as plt
import cv2
import time
# import scipy.interpolate.LinearNDInterpolator
import scipy.interpolate
# todo 得到的是一个插值的方法，输入数据得到结果

import scipy.interpolate

# x = np.linspace(0, 4, 12)
# y = np.cos(x**2/3+4)
# xnew = np.linspace(0, 4, 30)
#
# f1 = interp1d(x, y, kind = 'linear')
# f2 = interp1d(x, y, kind = 'cubic')
# f3 = interp1d(x, y, kind = 'nearest')
#
#
# plt.plot(x, y, 'o')
# plt.plot( xnew, f1(xnew), '-',)
# plt.plot(xnew, f2(xnew), '--')
# plt.plot(xnew, f3(xnew), '*')
# plt.legend(['data', 'linear', 'cubic','nearest'], loc = 'best')
# plt.show()



# todo 二维数据的插值
# todo 颜色分级，保存为 jpg
# todo


def set_img_color(img_mat, color_dict, save_path=None):
    """二维数据，设定不同的值，使用不同的颜色，生成三维矩阵，保存，或返回"""
    # color_dict : {(min, max]:[r,g,b],}, 范围是，左开右闭
    # todo 没有指定颜色的范围设置为背景色，一般就是黑色
    # todo 图像复制为三维，加上颜色
    # 一维矩阵转为三维矩阵
    w, h = img_mat.shape[:2]
    img = np.zeros((w, h, 3), dtype=np.uint8)
    # set background
    if "bg" in color_dict:
        img[:,:,0] = color_dict["bg"][0]
        img[:,:,1] = color_dict["bg"][1]
        img[:,:,2] = color_dict["bg"][2]
    #
    for each in color_dict:
        if each not in ["bg"]:
            v_min, v_max = each[0], each[1]
            each_color = color_dict[each]
            mask = np.logical_and(v_min < img_mat, img_mat <= v_max)
            img[mask, :] = each_color

    if save_path is not None:
        cv2.imencode('.jpg', img)[1].tofile(save_path)

    print(img.shape)
    plt.imshow(img)
    plt.show()


def interpolate_points(points, save_range, color_dict, save_path, method="cubic"):
    """对点进行插值"""
    x, y, values = zip(*points)
    x_flat, y_flat, z_flat = map(np.ravel, [x, y, values])
    # f = interp2d(x, y, value, kind='cubic')
    # f = interp2d(x_flat, y_flat, z_flat, kind='cubic')
    f = CubicHermiteSpline(x, y, values, kind='cubic')

    x_flat = np.linspace(0, save_range[0], 1000)
    y_flat = np.linspace(0, save_range[1], 1000)

    res = f(x_flat, y_flat)

    set_img_color(res, color_dict=color_dict, save_path=save_path)




# --------------------------------------------------------

def func(x, y):
    return x * (1 - x) * np.cos(4 * np.pi * x) * np.sin(4 * np.pi * y ** 2) ** 2

def interp1(x, y, values):
    # regard as rectangular grid
    f1 = interp2d(x, y, values, kind='cubic')
    return f1

def interp2(xx, yy, values):
    # regard as unstructured grid
    x_flat, y_flat, z_flat = map(np.ravel, [xx, yy, values])
    f2 = interp2d(x_flat, y_flat, z_flat, kind='cubic')
    return f2


if __name__ == "__main__":


    img = np.ones((100, 100), dtype=np.uint8)

    img[:50, :50] = 100

    # set_img_color(img, {(50, 150):[0,0,255], "bg":[255,255,255]})

    points = [(100, 100, 10), (200, 200, 20), (400, 500, 40)]

    interpolate_points(points, [1000, 1000], {(50, 150):[0,0,255], "bg":[255,255,255]}, save_path=None)


    exit()






    # Data point coordinates
    x = np.linspace(0, 1, 20)
    y = np.linspace(0, 1, 30)
    xx, yy = np.meshgrid(x, y)
    values = func(xx, yy)

    print("OK")

    #
    # f1 = interp1(x, y, values)
    # f2 = interp2(xx, yy, values)
    #
    # # Points which to interpolate data
    # x_flat = np.linspace(0, 1, 1000)
    # y_flat = np.linspace(0, 1, 2000)
    #
    # z1 = f1(x_flat, y_flat)
    # z2 = f2(x_flat, y_flat)
    #
    # print(z1.shape)
    #
    # cv2.imwrite(r"C:\Users\14271\Desktop\crop.jpg", z1)
    #
    # # plt.figure()
    # # plt.imshow(values, extent=(0, 1, 0, 1))
    # # plt.title("Origin")
    #
    # plt.figure()
    # plt.subplot(211)
    # plt.imshow(z1, extent=(0, 1, 0, 1))
    # plt.title("rectangular grid")
    # plt.subplot(212)
    # plt.imshow(z2, extent=(0, 1, 0, 1))
    # plt.title("unstructured grid")
    # plt.show()














