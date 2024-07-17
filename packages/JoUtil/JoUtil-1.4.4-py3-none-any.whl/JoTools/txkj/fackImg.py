# -*- coding: utf-8  -*-
# -*- author: jokker -*-

# 伪造的数据 左上角 有 5*5 有 F 字母的标注，

# 位置不能重复，每一个位置有缓冲区域

# 支持透明和不透明 jpg 和 png 两个格式的贴图


import os
import cv2
import copy
import shutil
import numpy as np
import PIL.Image as Image
from JoTools.txkjRes.deteRes import DeteRes


class FakeImg(object):

    def __init__(self, img_path, icon_dir):
        # 原图路径
        self.img_path = img_path
        # 贴图路径
        self.icon_path = icon_dir
        # 原图矩阵
        self.img_ndarry = cv2.imdecode(np.fromfile(self.img_path, dtype=np.uint8), 1)
        # 贴图文件夹路径
        self.icon_dir = icon_dir

    @staticmethod
    def mark_img(assign_img_array):
        """伪造图片要打上固定的 F 标记"""
        fake_icon = np.array(
            [[0,0,0,0],
             [0,1,1,1],
             [0,0,0,0],
             [0,1,1,1],
             [0,1,1,1]], dtype=np.uint8)
        fake_icon *= 255
        fake_icon = np.stack([fake_icon, fake_icon, fake_icon], axis=2)
        assign_img_array[:5, :4, :] = fake_icon
        return assign_img_array

    def make_fake_img(self, fake_img_info, save_img_path, save_xml_path):
        """制作伪造图片,位图信息需要进行传入"""
        # [{‘loc_lt_point’:(x, y), 'icon_path':'', 'new_size':(width, height), 'tag':'new_tag'}]
        a = DeteRes(assign_img_path=self.img_path)
        img_array = copy.deepcopy(self.img_ndarry)
        for each_icon_info in fake_img_info:
            (x, y) = each_icon_info['loc_lt_point']
            icon_path = each_icon_info['icon_path']
            new_size = each_icon_info['new_size']
            tag = each_icon_info['tag']
            icon_img = Image.open(icon_path)
            icon_img = icon_img.resize(new_size)
            icon_img_array = np.array(icon_img)
            img_array[x:x+new_size[0], y:y+new_size[1], :] = icon_img_array[:,:,:3]
            a.add_obj(x1=x, y1=y, x2=x+new_size[0], y2=y+new_size[1], tag=tag)

        # mark
        img_array = self.mark_img(img_array)
        # save
        cv2.imencode('.jpg', img_array)[1].tofile(save_img_path)
        a.save_to_xml(save_xml_path)

# class FakeImgOpt(object):
#
#     # todo


if __name__ == "__main__":


    imgPath = r"C:\Users\14271\Desktop\fake_img\origin_img\57c72bdea659d35fb0afd9a794f7f07e.jpg"
    iconDir = r"C:\Users\14271\Desktop\fake_img\icon_img\005.png"
    saveFakePath = r"C:\Users\14271\Desktop\fake_img\fake_img\123.jpg"
    saveFakeXmlPath = r"C:\Users\14271\Desktop\fake_img\fake_img\123.xml"

    a = FakeImg(img_path=imgPath, icon_dir=iconDir)

    fake_info = [{'loc_lt_point':(100, 100), 'icon_path':r'C:\Users\14271\Desktop\fake_img\icon_img\001.png', 'new_size':(200, 200), 'tag':'test'}]

    a.make_fake_img(fake_img_info=fake_info, save_img_path=saveFakePath, save_xml_path=saveFakeXmlPath)

    pass
























