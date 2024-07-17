# -*- coding: utf-8  -*-
# -*- author: jokker -*-


import os
import random
# from ..utils.ImageUtil import ImageUtil
# from .parseXml import ParseXml, parse_xml
# from ..utils.FileOperationUtil import FileOperationUtil

from JoTools.utils.ImageUtil import ImageUtil
from JoTools.txkj.parseXml import  ParseXml, parse_xml
from JoTools.utils.FileOperationUtil import FileOperationUtil



def resize_bg():
    """对背景进行重采样，P 图的前一步最好对背景重采样"""
    img_dir = r"C:\Users\14271\Desktop\防振锤优化\102_2500张P图计划\抠图素材\bg"
    save_dir = r"C:\Users\14271\Desktop\防振锤优化\102_2500张P图计划\抠图素材\reshape_bg"

    for index, each_path in enumerate(FileOperationUtil.re_all_file(img_dir)):
        a = ImageUtil(each_path)
        a.convert_to_assign_shape((2000, 2000))
        save_path = os.path.join(save_dir, "background_{0}.jpg".format(index + 120))
        a.save_to_image(save_path)

        print(each_path)


class AutoPS(object):
    """将图片 p 到背景上"""

    def __init__(self, bg):
        self.back_ground_path = bg                                  # 背景图
        self.object_path_list = []                                  # 对象名
        self.res_xml_info = {}                                      # 最后用于保存的 xml 信息
        self.object_xml_info = []                                   # 解析出来的
        self.background_img = ImageUtil(self.back_ground_path)      # 读取背景
        self.save_path = r""                                        # 结果的保存路径
        self.parse_xml = ParseXml()
        self.assign_object_num = 2                                     # 增加对象的个数，超过个数会被随机删除掉

    def do_init(self):
        """初始化"""
        # random.seed()
        random.shuffle(self.object_path_list)                                               # 只随机取指定的数目
        self.object_path_list = self.object_path_list[:self.assign_object_num]
        # 初始化保存 xml 信息

        file_path = self.save_path[:-3] + 'jpg'
        file_name = os.path.split(file_path)[1]
        self.res_xml_info = {
            'folder': 'None',
            'filename': file_name,
            'path': file_path,
            'segmented': '0',
            'size': {'width': str(self.background_img.get_img_shape()[1]), 'height': str(self.background_img.get_img_shape()[0]), 'depth': '3'},
            'source': {'database': 'Unknown'},
            'object': []}

    def parse_xml_info(self):
        """解析要放入背景的 object xml信息，认为一个 xml 只能有一个对象"""
        for each_object_path in self.object_path_list:
            each_xml_path = os.path.splitext(each_object_path)[0] + ".xml"
            # each_xml_info = parse_xml(each_xml_path)['object'][0]
            # self.object_xml_info.append(each_xml_info)

    def draw_object_to_background(self):
        """往背景上画 object，并生成 xml 信息"""
        for index, each_object in enumerate([1,2]):
            # name = each_object['name']                                                                  # object 的名字
            name = "test"                                                                  # object 的名字
            each_bndbox = each_object['bndbox']
            each_img = ImageUtil(self.object_path_list[index])
            # object 的范围

            # fixme 随机选择缩放比例
            random_ratio = random.choice([i/10.0 for i in range(5, 15, 1)])

            each_width, each_hight = each_img.get_img_shape()[:2]
            new_width = int(each_width * random_ratio)
            new_hight = int(each_hight * random_ratio)

            each_img.convert_to_assign_shape((new_hight, new_width))

            #
            width, hight = self.background_img.get_img_shape()[:2]
            loc = (random.randint(0, width - each_img.get_img_shape()[0]), random.randint(0, hight - each_img.get_img_shape()[1]))
            self.background_img.draw(each_img, assign_loc=loc)
            # 将标注的框信息写到 xml_info 中
            # fixme 缩放后的标注信息写入 xml 中
            each_bndbox['xmin'] = str(int((int(each_bndbox['xmin'])*random_ratio + loc[1])) + random.randint(-10, 10))
            each_bndbox['xmax'] = str(int((int(each_bndbox['xmax'])*random_ratio + loc[1])) + random.randint(-10, 10))
            each_bndbox['ymin'] = str(int((int(each_bndbox['ymin'])*random_ratio + loc[0])) + random.randint(-10, 10))
            each_bndbox['ymax'] = str(int((int(each_bndbox['ymax'])*random_ratio + loc[0])) + random.randint(-10, 10))
            #
            each_object_info = {'name': name, 'pose': 'Unspecified', 'truncated': '0', 'difficult': '0', 'bndbox': each_bndbox}
            self.res_xml_info['object'].append(each_object_info)

    def re_fresh(self):
        """清空缓存，去掉前面做的步奏"""
        self.background_img = ImageUtil(self.back_ground_path)

    def save_ps_res(self):
        """保存 ps 结果"""
        self.background_img.save_to_image(self.save_path)
        save_xml_path = self.save_path[:-4] + '.xml'
        self.parse_xml.save_to_xml(save_xml_path, assign_xml_info=self.res_xml_info)

    def do_proces(self):
        """全流程"""
        a.do_init()
        a.parse_xml_info()
        a.draw_object_to_background()
        a.save_ps_res()


if __name__ == "__main__":

    # 背景文件夹
    bg_dir = r"C:\Users\14271\Desktop\test\bg"
    # 物体文件夹，对应的 jpg 和 img 文件
    object_dir = r"C:\Users\14271\Desktop\test\obj"
    # 保存文件夹
    save_dir = r"C:\Users\14271\Desktop\test\save"
    # 所有的背景图片
    bg_files = list(FileOperationUtil.re_all_file(bg_dir, lambda x:str(x).endswith('.jpg')))

    for i in range(3):
        print(i, 2500)
        ground_path = random.choice(bg_files)

        save_path = os.path.join(save_dir, "res_{0}.jpg".format(i))
        #
        a = AutoPS(ground_path)
        a.object_path_list = list(FileOperationUtil.re_all_file(object_dir, func=lambda x:str(x).endswith('.png')))
        a.save_path = save_path
        a.assign_object_num = random.randint(1, 2)
        a.do_proces()




