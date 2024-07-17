# -*- coding: utf-8  -*-
# -*- author: jokker -*-

import os
import numpy as np
import cv2
from ...utils.BisectUtil import BisectUtil
from PIL import Image
import progressbar
# from JoTools.utils.ArcpyGdalUtil import ArcpyGdalUtil
from ...utils.FileOperationUtil import FileOperationUtil
from ...utils.PickleUtil import PickleUtil
from ...utils.RandomUtil import RandomUtil
from ...utils.ImageUtil import ImageUtil
from ...utils.DecoratorUtil import DecoratorUtil

# todo 统计的时候需要加载英文字母 或者 标点符号，这样能扩充汉字图库
# todo 找到最邻近的值可以使用 HighPerformance 中的函数来做，最好能找到最邻近的几个值
# todo 可以使用固定的汉字集来做，比如是一篇文章内包含的字，或者有特殊意义上的字
# todo 如何才能快速的进行像元的替换，不用一个像元一个像元的处理，
# （1）将每一个图片进行编码
# （2）根据一定的规则将像元值替换为对应的编码
# （3）根据像元和编码的对应关系，逐个替换编码所对应的图片
# todo 可以对图片的整体进行调整，防止出现大片白色的区域，将图片调整为合适的区域（往中间压缩）
# todo 可以加入一个纯白的图片，这样可以更好的展现白色，同理可以加一个纯黑的颜色，这样对于特定的图片起到美化的效果

# todo 将字用背景颜色代替

"""
* 实现步奏
* --------------------------------------
* 将照片转为黑白（单波段）
* 将图像采样为需要的分辨率（或者行列大小）
* 将单波段照片读取为矩阵
* 遍历矩阵的每一个元素，根据其像素值获取随机的一匹配的汉字（汉字的黑度等于像素的值）
* 将矩阵中的所有值进行替换，得到新的照片矩阵

"""



class WordImage(object):

    def __init__(self, img_path, new_size=(200, 200), save_path=None):
        #
        self.__analysis_max = None
        self.__analysis_min = None
        self.__analysis_dict = None
        self.__analysis_dict_keys = None
        self.img_mat = None
        #
        self.img_data_folder = None  # 用于保存图库的文件夹
        self.analysis_pkl_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), r'./data/del.pkl')  # 分析结果的保存路径
        #
        self.img_path = img_path  # 用于转换的图片
        self.new_size = new_size  # 图片重采样后的大小
        self.save_path = save_path

    def load_init_data(self):
        """载入数据"""
        if self.analysis_pkl_path is None:
            raise ValueError('analysis_pkl_path is needed')

        pic_data = PickleUtil.load_data_from_pickle_file(self.analysis_pkl_path)
        self.__analysis_dict = pic_data
        self.__analysis_max = max(list(pic_data.keys()))
        self.__analysis_min = min(list(pic_data.keys()))
        self.__analysis_dict_keys = sorted(list(self.__analysis_dict.keys()))

    def get_mat_from_assign_img(self):
        """从指定的图片中获取对应的矩阵"""
        img = Image.open(self.img_path)
        # gray = img.convert('L')
        gray = img.resize(self.new_size)
        bw = np.asarray(gray).copy()
        self.img_mat = bw

    def get_random_word_mat_by_dark_index(self, pic_dark_index):
        """获取对应的随机字符图片的路径"""
        # 没有需要的字的时候，找到最近的字符
        if pic_dark_index in self.__analysis_dict:
            find_index = pic_dark_index
        else:
            find_index = self.__analysis_dict_keys[BisectUtil.find_closest(self.__analysis_dict_keys, pic_dark_index)]
        return RandomUtil.choice(self.__analysis_dict[find_index])

    @staticmethod
    def get_pic_with_assign_word(word_str, save_path, word_size=50):
        """获得单个字符的图片，用于作为拼接的素材"""
        word = ImageUtil.create_word_img(word_str, word_size=word_size, background_color=(255, 255, 255),
                                         is_cut_border=False)
        word.save_to_image(save_path)

    def get_img_data(self):
        """获取对应的图库"""
        if os.path.exists(self.analysis_pkl_path):
            return

        if self.img_data_folder is None or self.analysis_pkl_path is None:
            raise ValueError('img_data_folder and analysis_pkl_path is needed')

        all_china_str = self.get_all_chinese_character()
        self.convert_chinese_to_word_pic(all_china_str, self.img_data_folder)
        self.word_analysis(self.img_data_folder, self.analysis_pkl_path)

    @DecoratorUtil.time_this
    def do_process(self):

        self.get_img_data()
        self.load_init_data()
        self.get_mat_from_assign_img()

        dark_index_mat = ((255 - self.img_mat) / (255 / (self.__analysis_max - self.__analysis_min)) + 8).astype(
            np.uint8)
        line_index, col_index, _ = dark_index_mat.shape
        new_mat = np.zeros((line_index * 25, col_index * 25, 3), dtype=np.uint8)
        #
        pb = progressbar.ProgressBar(line_index).start()
        for i in range(line_index):
            # print(round(float(i) / (float(line_index)), 3))
            pb.update(i+1)
            for j in range(col_index):
                each_dark_index = int(np.mean(dark_index_mat[i, j, :]))
                each_pic_mat = self.get_random_word_mat_by_dark_index(each_dark_index)
                color_mat = np.ones((each_pic_mat.shape[0], each_pic_mat.shape[1], 3))*255
                color_mat[each_pic_mat<175, :] = self.img_mat[i, j, :3]
                new_mat[i * 25: (i + 1) * 25, j * 25: (j + 1) * 25, :] = color_mat
        pb.finish()
        print(" * saving")
        img = Image.fromarray(new_mat)
        img.save(self.save_path)

    # ----------------- help ----------------------
    @staticmethod
    def convert_chinese_to_word_pic(word_str_list, save_folder, img_type='.png'):
        """主流程"""
        # 将中文转为对应的图片用于拼接
        for word_str in word_str_list:
            if not WordImage.is_chinese(word_str):  # 不是中文字符
                pass

            save_path = os.path.join(save_folder, word_str + img_type)
            if not os.path.exists(save_path):
                WordImage.get_pic_with_assign_word(word_str, save_path, 25)

    @staticmethod
    def is_chinese(assign_str):
        if '\u4e00' <= assign_str <= '\u9fff':
            return True
        else:
            return False

    @staticmethod
    def get_all_chinese_character():
        """打印所有汉字"""
        all_chrs = []
        for ch in range(0x4e00, 0x9fa6):  # range(0x4e00, 0x9fff)
            all_chrs.append(chr(ch))
        return all_chrs

    @staticmethod
    def get_word_dark_index(img_path):
        """汉字的深度指数"""
        # img_mat = ArcpyGdalUtil.read_tiff(img_path)[0][0, :, :]
        img_mat = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), 1)[0,:,:]
        dark_index = int(255 - np.sum(img_mat) / (25 * 25))
        return dark_index

    @staticmethod
    def word_analysis(word_pic_dir, pkl_save_path):
        """文字分析，得到各个段的汉字的统计情况"""
        word_dark_index_dict = {}
        img_files = FileOperationUtil.re_all_file(word_pic_dir)
        for each_pic_file in img_files:
            dark_index = WordImage.get_word_dark_index(each_pic_file)
            # 读取图片矩阵
            # img_mat = ArcpyGdalUtil.read_tiff(each_pic_file)[0][0, :, :]
            img_mat = cv2.imdecode(np.fromfile(each_pic_file, dtype=np.uint8), 1)[0, :, :]
            #
            if dark_index not in word_dark_index_dict:
                word_dark_index_dict[dark_index] = [img_mat]
            else:
                word_dark_index_dict[dark_index].append(img_mat)

        PickleUtil.save_data_to_pickle_file(word_dark_index_dict, pkl_save_path)


if __name__ == '__main__':

    # -------------------------------------------------------------------------------------
    ratio = 1                                                   # 图像缩小的比例
    img_path = r"C:\Users\14271\Desktop\test.jpg"
    save_path = r"C:\Users\14271\Desktop\test_2.jpg"
    # -------------------------------------------------------------------------------------

    img = Image.open(img_path)
    width, height = img.size
    new_width, new_height = int(width/ratio), int(height/ratio)

    a = WordImage(img_path, new_size = (new_width, new_height))
    a.analysis_pkl_path = r'.\data\del.pkl'
    a.save_path = save_path
    a.do_process()

    # todo 分为三个部分，（1）汉字转为对应的图库中的图片（2）对拥有的图库进行分析，参数可视化（3）指定图片得到对应的汉字图
    # todo 使用全部汉字得到的图片结果反而不好，找到原因，并分析时候需要进行修改
    # todo 对各个灰度做统计，得到对应的数字的个数
