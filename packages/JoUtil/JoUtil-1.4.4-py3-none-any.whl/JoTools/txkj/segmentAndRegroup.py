# -*- coding: utf-8  -*-
# -*- author: jokker -*-

import numpy as np
from PIL import Image
import random
import copy

"""
1. 对于图片边缘不能完全进行等分的情况如何处理？
    * 可以先将图片从采样成能进行等分的情况，进行区块交换，然后再改变回来
    * 重采样可能引入不确定误差，可以排除边缘的几个不能进行等分的像素
"""

# todo 支持京东论文中的 block 交换策略


class SegmentAndRegroup(object):
    """对图片进行切块并重组，两种模式（1）设定横竖格分为几块（2）设定每个 block 的长宽"""

    def __init__(self):
        self.segment_x = 7  # 沿着 x 轴 切分的块数
        self.segment_y = 7
        self.img_path = None
        self.img_array = None
        self.img_array_origin = None  # 原始图片矩阵，因为要使得每一个分块一样大，所以需要去掉边缘的像素
        self.exchange_times = None # 区块之间两两交换的次数
        self.assign_block_height = None  # 指定 block 的长度
        self.assign_block_width = None
        self.assign_block_size = False  # 使用指定大小的 block 进行分类

    def get_segment_x_y(self):
        """获得横纵向裁剪的个数"""
        if self.assign_block_size:
            # 当指定使用固定大小的 block 的时候
            if self.assign_block_width is None or self.assign_block_height is None:
                raise ValueError("需要指定 block 的长宽")
            #
            self.segment_x = int(self.img_array_origin.shape[1] / self.assign_block_width)
            self.segment_y = int(self.img_array_origin.shape[0] / self.assign_block_height)

    def exchange_two_block(self, block_index_1, block_index_2):
        """交换两个区块中的内容，使用二维坐标表示每个矩阵"""
        # 找到两个 block 的范围
        x_min_1, y_min_1 = self.assign_block_width * block_index_1[1], self.assign_block_height * block_index_1[0]
        x_max_1, y_max_1 = x_min_1 + self.assign_block_width, y_min_1 + self.assign_block_height
        x_min_2, y_min_2 = self.assign_block_width * block_index_2[1], self.assign_block_height * block_index_2[0]
        x_max_2, y_max_2 = x_min_2 + self.assign_block_width, y_min_2 + self.assign_block_height
        # 将两个 block 中的值进行交换

        print('-'*100)

        print(y_min_1, y_max_1, x_min_1, x_max_1)
        print(y_min_2, y_max_2, x_min_2, x_max_2)

        block_value_temp_1 = copy.deepcopy(self.img_array[y_min_1:y_max_1, x_min_1:x_max_1, :])
        block_value_temp_2 = copy.deepcopy(self.img_array[y_min_2:y_max_2, x_min_2:x_max_2, :])

        print(block_value_temp_1.shape)
        print(block_value_temp_2.shape)

        if block_value_temp_1.shape == (50,50,3) and block_value_temp_2.shape == (50,50,3):
            self.img_array[y_min_1:y_max_1, x_min_1:x_max_1, :] = block_value_temp_2
            self.img_array[y_min_2:y_max_2, x_min_2:x_max_2, :] = block_value_temp_1

    def get_array_from_img(self):
        """将图片的转为 array"""
        # fixme 现在默认为的是输入有 rgb三通道的 .jpg 图片
        img = Image.open(self.img_path)
        img_array = np.array(np.asarray(img, dtype=np.uint8))
        img_array.flags.writeable = True  # 解决图片为 read only 的问题
        # 如果 img_array 是只有一个通道扩展为 3 通道
        if len(img_array.shape) == 2:
            img_array = np.rollaxis(np.tile(img_array, (3, 1, 1)), 0, 3)

        height, width, = img_array.shape[:2]
        self.img_array_origin = img_array
        # 根据设置的分块模式设定横竖切块个数
        self.get_segment_x_y()
        # 将不能分块的边缘先去掉
        self.img_array = img_array[:height-(height % self.segment_y), :width-(width % self.segment_y), :]
        # 当没指定 block size 时，计算得到 block size
        if not self.assign_block_size:
            self.assign_block_width = int(self.img_array.shape[1] / self.segment_x)
            self.assign_block_height = int(self.img_array.shape[0] / self.segment_y)

    def save_array_to_img(self, save_path):
        """将 array 转为图片"""
        height, width = self.img_array.shape[:2]
        self.img_array_origin[:height, :width, :] = self.img_array
        img = Image.fromarray(self.img_array_origin)
        img.save(save_path)

    def get_block_index_for_exchange(self):
        """获取一对用于交换的 block 的index"""
        # (1) 每次只跟相邻的 bolck 进行交换
        # while True:
            # x_1, y_1 = random.randint(0, self.segment_y-1), random.randint(0, self.segment_x-1)
            # x_2, y_2 = x_1 + random.choice([-1, 0, 1]), y_1 + random.choice([-1, 0, 1])
            # 判断得到的两个位置是否符合要求
            # if min(x_1, y_1, x_2, y_2) >= 0 and max(x_1, x_2) < self.segment_y and max(y_1, y_2) < self.segment_x:
            #     return (x_1, y_1), (x_2, y_2)

        # (2) 任意两个 block 进行交换
        # return (random.randint(0, self.segment_x-1), random.randint(0, self.segment_y-1)), \
        #        (random.randint(0, self.segment_x-1), random.randint(0, self.segment_y-1))

        return (random.randint(0, self.segment_x-2), random.randint(0, self.segment_y-2)), \
               (random.randint(0, self.segment_x-3), random.randint(0, self.segment_y-2))

        # (3) 看京东论文里面的 block 之间交换的策略

    def do_process(self, save_path):
        """主流程"""
        # 从图像获取矩阵，对分割 block 数目和 block 大小进行确定
        if self.get_array_from_img() is False:
            print("目前只能处理 rgb 图")
            return
        # 根据需要打乱的次数打乱区块
        for i in range(self.exchange_times):
            block_index_1, block_index_2 = self.get_block_index_for_exchange()
            print(block_index_1, block_index_2)
            self.exchange_two_block(block_index_1, block_index_2)
        # 保存矩阵到图片
        self.save_array_to_img(save_path)


def segment_and_regroup(img_path, save_path, exchange_times=10, segment_x=7, segment_y=7, assign_block_size=False,
                        assign_block_width=None, assign_block_heignt=None):
    a = SegmentAndRegroup()
    a.img_path = img_path
    a.segment_x = segment_x
    a.segment_y = segment_y
    a.exchange_times = exchange_times
    # 当使用指定 block 大小的时候，指定的切割长宽个数参数将重新计算
    a.assign_block_size = assign_block_size
    a.assign_block_height = assign_block_heignt
    a.assign_block_width = assign_block_width
    a.do_process(save_path)


if __name__ == "__main__":

    JpgPath = r"C:\Users\14271\Desktop\del\rust.jpg"
    SavePath = r"C:\Users\14271\Desktop\del\rust_2.jpg"
    # segment_and_regroup(JpgPath, SavePath, 10, assign_block_size=True, assign_block_heignt=100, assign_block_width=100)
    # segment_and_regroup(JpgPath, SavePath, int(20*20/2), segment_x=20, segment_y=20)
    segment_and_regroup(JpgPath, SavePath, 200, assign_block_width=50, assign_block_heignt=50, assign_block_size=True)






