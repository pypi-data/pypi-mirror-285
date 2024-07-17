# -*- coding: utf-8  -*-
# -*- author: jokker -*-



import os
import copy
import random
import math
import shutil
import numpy as np
import prettytable
from ..utils.JsonUtil import JsonUtil
from ..utils.CsvUtil import CsvUtil
from ..utils.ImageUtil import ImageUtil
from .parseXml import ParseXml, parse_xml
from ..utils.FileOperationUtil import FileOperationUtil
from PIL import Image



"""
* 专门用于处理 efficient 用于训练的数据，也就是将数据转为  efficientdet 可以训练的样式
"""

class CocoDatabaseUtil(object):

    # ----------- 训练数据之间互转 ----------------

    @staticmethod
    def voc2coco(xml_dir, save_path, category_dict):
        """voc 转为 coco文件"""

        # 检查 category_dict 是否按照规范填写的
        for each in category_dict.values():
            if each == 0:
                raise ValueError("需要从 category_dict 的值 需要从 1 开始")

        coco_dict = {"info": {"description": "", "url": "", "version": "", "year": 2020, "contributor": "",
                              "data_created": "'2020-04-14 01:45:18.567988'"},
                     "licenses": [{"id": 1, "name": None, "url": None}],
                     "categories": [],
                     "images": [],
                     "annotations": []}

        # 加载分类信息
        for each_category in category_dict:
            categories_info = {"id": category_dict[each_category], "name": each_category, "supercategory": 'None'}
            coco_dict['categories'].append(categories_info)

        # 加载
        box_id = 0
        for index, each_xml_path in enumerate(FileOperationUtil.re_all_file(xml_dir, lambda x: str(x).endswith('.xml'))):
            xml_info = parse_xml(each_xml_path)
            each_image = {"id": index, "file_name": xml_info["filename"],
                          "width": int(float(xml_info["size"]["width"])),
                          "height": int(float(xml_info["size"]["height"]))}
            coco_dict['images'].append(each_image)
            for bndbox_info in xml_info["object"]:
                category_id = category_dict[bndbox_info['name']]
                each_box = bndbox_info['bndbox']
                bndbox = [float(each_box['xmin']), float(each_box['ymin']),
                          (float(each_box['xmax']) - float(each_box['xmin'])),
                          (float(each_box['ymax']) - float(each_box['ymin']))]
                area = bndbox[2] * bndbox[3]
                segmentation = [bndbox[0], bndbox[1], (bndbox[0] + bndbox[2]), bndbox[1], (bndbox[0] + bndbox[2]),
                                (bndbox[1] + bndbox[3]), bndbox[0], (bndbox[1] + bndbox[3])]
                each_annotations = {"id": box_id, "image_id": index, "category_id": category_id, "iscrowd": 0,
                                    "area": area, "bbox": bndbox, "segmentation": segmentation}
                coco_dict['annotations'].append(each_annotations)
                box_id += 1

        # 保存文件
        JsonUtil.save_data_to_json_file(coco_dict, save_path)

    @staticmethod
    def coco2voc(json_file_path, save_folder):
        """json文件转为xml文件"""

        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        json_info = JsonUtil.load_data_from_json_file(json_file_path)
        # 解析 categories，得到字典
        categorie_dict = {}
        for each_categorie in json_info["categories"]:
            categorie_dict[each_categorie['id']] = each_categorie['name']

        # 解析 image 信息
        image_dict = {}
        for each in json_info["images"]:
            id = each['id']
            file_name = each['file_name']
            width = each['width']
            height = each['height']
            image_dict[id] = {"filename": each['file_name'], 'object': [], "folder": "None", "path": "None",
                              "source": {"database": "Unknow"},
                              "segmented": "0", "size": {"width": str(width), "height": str(height), "depth": "3"}}

        # 解析 annotations 信息
        for each in json_info["annotations"]:
            image_id = each['image_id']
            category_id = each['category_id']
            each_name = categorie_dict[category_id]
            bbox = each["bbox"]
            bbox_dict = {"xmin": str(bbox[0]), "ymin": str(bbox[1]), "xmax": str(int(bbox[0]) + int(bbox[2])),
                         "ymax": str(int(bbox[1]) + int(bbox[3]))}
            object_info = {"name": each_name, "pose": "Unspecified", "truncated": "0", "difficult": "0",
                           "bndbox": bbox_dict}
            image_dict[image_id]["object"].append(object_info)

        # 将数据转为 xml
        aa = ParseXml()
        for each_img in image_dict.values():
            save_path = os.path.join(save_folder, each_img['filename'][:-3] + 'xml')
            aa.save_to_xml(save_path, each_img)

    @staticmethod
    def csv2voc(csv_path, save_folder):
        """csv 转为 voc 文件"""

        csv_info = CsvUtil.read_csv_to_list(csv_path)

        image_dict = {}

        for each in csv_info[1:]:
            image_id = each[0]
            bbox = each[3].strip("[]").split(',')
            bbox_dict = {"xmin": str(bbox[0]), "ymin": str(bbox[1]), "xmax": str(float(bbox[0]) + float(bbox[2])),
                         "ymax": str(float(bbox[1]) + float(bbox[3]))}
            object_info = {"name": "xiao_mai", "pose": "Unspecified", "truncated": "0", "difficult": "0",
                           "bndbox": bbox_dict}
            #
            if image_id not in image_dict:
                image_dict[image_id] = {}
                image_dict[image_id]["filename"] = "{0}.jpg".format(each[0])
                image_dict[image_id]["folder"] = "None"
                image_dict[image_id]["source"] = {"database": "Unknow"}
                image_dict[image_id]["path"] = "None"
                image_dict[image_id]["segmented"] = "0"
                image_dict[image_id]["size"] = {"width": str(each[1]), "height": str(each[2]), "depth": "3"}
                image_dict[image_id]['object'] = [object_info]
            else:
                image_dict[image_id]['object'].append(object_info)

        # 将数据转为 xml
        aa = ParseXml()
        for each_img in image_dict.values():
            save_path = os.path.join(save_folder, each_img['filename'][:-3] + 'xml')
            aa.save_to_xml(save_path, each_img)

    @staticmethod
    def voc2csv(xml_dir, save_csv_path):
        """voc xml 转为 csv 文件"""

        csv_list = []
        for each in FileOperationUtil.re_all_file(xml_dir, lambda x: str(x).endswith('.xml')):
            xml_info = parse_xml(each)
            a = xml_info['object']
            width = xml_info['size']['width']
            height = xml_info['size']['height']
            file_name = xml_info['filename'][:-4]
            #
            for each_box_info in xml_info['object']:
                each_class = each_box_info['name']
                each_box = each_box_info['bndbox']
                # fixme 这边对防振锤 box 做一下限定, x,y,w,h
                x, y, w, h = int(each_box['xmin']), int(each_box['ymin']), (
                            int(each_box['xmax']) - int(each_box['xmin'])), (
                                         int(each_box['ymax']) - int(each_box['ymin']))
                each_line = [file_name, width, height, [x, y, w, h], each_class]

                csv_list.append(each_line)

        CsvUtil.save_list_to_csv(csv_list, save_csv_path)

    # ----------- 图片转为 coco 数据样式 -----------

    @staticmethod
    def zoom_img_and_xml_to_square(img_path, xml_path, save_dir, assign_length_of_side=1536, assign_save_name=None):
        """将图像先填充为正方形，再将 xml 和 图像拉伸到指定长宽"""
        file_list = []
        img = ImageUtil(img_path)
        img_shape = img.get_img_shape()
        # 将图像填充为正方形
        img_mat = img.get_img_mat()
        length_of_side = max(img_shape[0], img_shape[1])
        new_img = np.ones((length_of_side, length_of_side, 4), dtype=np.uint8) * 127
        new_img[:img_shape[0], :img_shape[1], :] = img_mat
        img.set_img_mat(new_img)
        #
        img.convert_to_assign_shape((assign_length_of_side, assign_length_of_side))
        if assign_save_name is None:
            img_name = os.path.split(img_path)[1]
        else:
            img_name = assign_save_name + '.jpg'
        save_path = os.path.join(save_dir, img_name)
        img.save_to_image(save_path)
        file_list.append(save_path)
        # 读取 xml，xml 进行 resize 并保存
        img_shape = (length_of_side, length_of_side)  # 图像信息已经进行了更新
        xml = ParseXml()
        each_xml_info = xml.get_xml_info(xml_path)
        # 改变图片长宽
        each_xml_info['size'] = {'width': str(assign_length_of_side), 'height': str(assign_length_of_side), 'depth': '3'}
        each_xml_info["filename"] = img_name

        # 遍历每一个 object 改变其中的坐标
        for each_object in each_xml_info['object']:
            bndbox = each_object['bndbox']
            bndbox['xmin'] = str(int(float(bndbox['xmin']) / (img_shape[0] / assign_length_of_side)))
            bndbox['xmax'] = str(int(float(bndbox['xmax']) / (img_shape[0] / assign_length_of_side)))
            bndbox['ymin'] = str(int(float(bndbox['ymin']) / (img_shape[1] / assign_length_of_side)))
            bndbox['ymax'] = str(int(float(bndbox['ymax']) / (img_shape[1] / assign_length_of_side)))

        if assign_save_name is None:
            xml_name = os.path.split(xml_path)[1]
        else:
            xml_name = assign_save_name + '.xml'

        save_xml_path = os.path.join(save_dir, xml_name)
        xml.save_to_xml(save_xml_path)
        file_list.append(save_xml_path)
        return file_list

    @staticmethod
    def change_img_to_coco_format(img_folder, save_folder, assign_length_of_side=1536, xml_folder=None, val_train_ratio=0.1, category_dict=None, file_head=""):
        """将文件夹中的文件转为 coco 的样式，正方形，填充需要的部分, 将按照需要对文件进行重命名, file_head 文件的前缀"""
        if xml_folder is None:
            xml_folder = img_folder
        # 创建保存文件夹
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # 创建 train 和 val 文件夹
        train_dir = os.path.join(save_folder, "train")
        val_dir = os.path.join(save_folder, "val")
        annotations_dir = os.path.join(save_folder, "annotations")

        if not os.path.exists(train_dir):
            os.makedirs(train_dir)

        if not os.path.exists(val_dir):
            os.makedirs(val_dir)

        if not os.path.exists(annotations_dir):
            os.makedirs(annotations_dir)

        # 计算文件名的长度
        count = len(os.listdir(img_folder))
        o_count = int(math.log10(count)) + 1

        for index, each_img_name in enumerate(os.listdir(img_folder)):
            if not each_img_name.endswith('.jpg'):
                continue

            img_path = os.path.join(img_folder, each_img_name)
            xml_path = os.path.join(xml_folder, each_img_name[:-3] + 'xml')

            print("{0} : {1}".format(index, img_path))

            if not os.path.exists(xml_path):
                continue

            # 进行转换
            assign_save_name = file_head + str(index).rjust(o_count, "0")
            file_list = CocoDatabaseUtil.zoom_img_and_xml_to_square(img_path, xml_path, save_folder, assign_length_of_side, assign_save_name=assign_save_name)

            # 有一定的概率分配到两个文件夹之中
            if random.random() > val_train_ratio:
                traget_dir = train_dir
            else:
                traget_dir = val_dir

            for each_file_path in file_list:
                new_file_path = os.path.join(traget_dir, os.path.split(each_file_path)[1])
                shutil.move(each_file_path, new_file_path)

        # 将 xml 生成 json 文件，并存放到指定的文件夹中
        if category_dict is not None:
            save_train_path = os.path.join(annotations_dir, "instances_train.json")
            save_val_path = os.path.join(annotations_dir, "instances_val.json")
            CocoDatabaseUtil.voc2coco(train_dir, save_train_path, category_dict=category_dict)
            CocoDatabaseUtil.voc2coco(val_dir, save_val_path, category_dict=category_dict)
        else:
            print("未指定 category_dict 不进行 xml --> json 转换")




if __name__ == "__main__":

    img_dir = r"C:\Users\14271\Desktop\优化开口销第二步\001_训练数据\save_small_img_new"
    xml_dir = r"C:\Users\14271\Desktop\优化开口销第二步\001_训练数据\save_small_img_new"
    save_dir = r"C:\Users\14271\Desktop\优化开口销第二步\001_训练数据\save_small_img_reshape"

    # category_dict = {"middle_pole":1, "single":2, "no_single":3}
    # category_dict = {"fzc":1, "zd":2, "xj":3, "other":4, "ljj":5}
    # category_dict = {"fzc":1, "zfzc":2, "hzfzc":3, "holder":4, "single":5}
    category_dict = {"K":1, "KG":2, "Lm":3, "dense2":4, "other_L4kkx":5,"other_fist":6,"other_fzc":7,"other1":8,"other2":9,
                     "other3":10, "other4":11, "other5":12, "other6":13, "other7":14, "other8":15, "other9":16, "dense1":17, "dense3":18}


    CocoDatabaseUtil.change_img_to_coco_format(img_dir, save_dir, 1536, xml_dir, category_dict=category_dict, file_head="")




