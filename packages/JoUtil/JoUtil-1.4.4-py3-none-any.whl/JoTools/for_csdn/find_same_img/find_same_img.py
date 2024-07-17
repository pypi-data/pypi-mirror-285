# -*- coding: utf-8  -*-
# -*- author: jokker -*-


import os
import imagehash
import cv2
import numpy as np
from PIL import Image
from ...utils.HashlibUtil import HashLibUtil
from ...utils.FileOperationUtil import FileOperationUtil
from ...utils.PickleUtil import PickleUtil
from ...utils.DecoratorUtil import DecoratorUtil
import progressbar


class HashImageUtil(object):

    def __init__(self):
        self.db_dir_list = []           # 作为数据库的文件夹，每次扫描里面的文件，丰富数据库
        self.db_save_dir = None         # 用于保存本地缓存文件的路径，文件存储了文件名和文件 MD5 img_hash 等信息
        self.md5_hash_dict = {}         # 存储文件 md5 值和对应图片的 hash 值
        self.md5_file_name_dict = {}    # 存储文件 md5 值和文件名的字典
        self.hash_size = 20             # 计算图像 img_hash 所用的 size
        self.save_num = 500             # 每扫描多少张新图片就保存数据一次

    def update_db(self):
        """更新数据库，扫描指定的文件夹里面的所有，jpg，png 后缀的文件，并更新到数据库文件中"""
        index = 0
        for each_img_dir in self.db_dir_list:
            # 去除不是文件夹的路径
            if not os.path.isdir(each_img_dir):
                continue
            # 遍历指定文件夹下面的所有文件
            print("* 更新文件夹 : {0}".format(each_img_dir))
            file_img_list = FileOperationUtil.re_all_file(each_img_dir, lambda x:str(x).endswith((".jpg", ".png", ".JPG", ".PNG")))
            # pb = progressbar.ProgressBar(len(file_img_list)).start()
            for img_index, each_img_path in enumerate(file_img_list):
                # 计算图片的 md5 值
                # pb.update(img_index+1)
                # 每 500 张图片保存一下数据库
                print(img_index, each_img_path)
                if index % 500 == 0:
                    index += 1
                    # print("* 更新数据库文件")
                    self.save_dict_to_pkl()
                try:
                    each_file_md5 = HashLibUtil.get_file_md5(each_img_path)
                    # 是个新文件，没有计算过 img_hash
                    if not each_file_md5 in self.md5_hash_dict:
                        index += 1
                        # print(index, each_img_path)
                        self.md5_file_name_dict[each_file_md5] = each_img_path
                        # 计算图像的 hash 值
                        each_img_hash = imagehash.average_hash(Image.open(each_img_path), hash_size=self.hash_size)
                        self.md5_hash_dict[each_file_md5] = each_img_hash
                except Exception as e:
                    print(e)
            # pb.finish()
        # 更新本地文件
        self.save_dict_to_pkl()

    def do_init(self):
        """初始化"""

        # 读取字典信息
        save_md5_hash_dict_path = os.path.join(self.db_save_dir, "{0}_{1}.pkl".format("md5_hash_dict", self.hash_size))
        save_md5_file_name_dict_path = os.path.join(self.db_save_dir, "{0}_{1}.pkl".format("md5_file_name_dict", self.hash_size))

        if os.path.isfile(save_md5_hash_dict_path):
            self.md5_file_name_dict = PickleUtil.load_data_from_pickle_file(save_md5_file_name_dict_path)

        if os.path.isfile(save_md5_file_name_dict_path):
            self.md5_hash_dict = PickleUtil.load_data_from_pickle_file(save_md5_hash_dict_path)

    def save_dict_to_pkl(self):
        """将两个重要的字典保存为本地文件"""
        # 文件名中要体现计算 hash 值用的 hash 位数
        save_md5_hash_dict_path = os.path.join(self.db_save_dir, "{0}_{1}.pkl".format("md5_hash_dict", self.hash_size))
        PickleUtil.save_data_to_pickle_file(self.md5_hash_dict, save_md5_hash_dict_path)
        save_md5_file_name_dict_path = os.path.join(self.db_save_dir, "{0}_{1}.pkl".format("md5_file_name_dict", self.hash_size))
        PickleUtil.save_data_to_pickle_file(self.md5_file_name_dict, save_md5_file_name_dict_path)

    def check_db(self):
        """查看数据库中是否有文件不存在，删除这些文件"""
        pass

    @DecoratorUtil.time_this
    def find_most_similar_img(self, assign_img_path, img_count=3):
        """找到最相似的几个图片"""
        # 计算图片的 img_hash
        img_hash = imagehash.average_hash(Image.open(assign_img_path), hash_size=self.hash_size)
        # 对比图片的 img_hash 和库中所有的 img_hash
        find_res = []
        for each_hash_info in self.md5_hash_dict.items():
            find_res.append((each_hash_info[1] - img_hash, each_hash_info[0]))
        # 结果进行排序，返回前 img_count 个结果
        find_res = sorted(find_res, key=lambda x:x[0], reverse=False)
        # 打印前 n 个最相似的结果
        print("当前结果，扫描对比 {0} 张图片".format(len(find_res)))
        res = []
        for each in find_res[:img_count]:
            # print(each[0], self.md5_file_name_dict[each[1]])
            res.append((each[0], self.md5_file_name_dict[each[1]]))
        return res

    def do_process(self):
        """主流程"""
        self.do_init()
        # self.update_db()


class MatchSmallImage(object):
    """大图和小图之间的匹配"""

    @staticmethod
    def get_sift_des(img_path):
        """输入图像，拿到特征矩阵"""
        sift = cv2.xfeatures2d_SIFT.create()
        # img = cv2.imread(img_path)
        img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), 1)
        kp, des = sift.detectAndCompute(img, None)
        return des

    @staticmethod
    def get_match_index_between_des(des_big, des_small, threshold=0.1):
        """计算两个图像 des 之间的相似度"""
        bf = cv2.BFMatcher(cv2.NORM_L2)
        matches = bf.knnMatch(des_big, des_small, k=2)        # k = 2  返回两个最佳匹配

        goodMatch = []
        for m, n in matches:
            if m.distance < threshold * n.distance:     # 第一个最匹配的要比第二个最匹配的匹配程度好好的多，就算是好的匹配点
                goodMatch.append(m)

        return float(len(goodMatch))/float(len(des_small))

    @staticmethod
    def do_init_for_small_img(small_img_dir, save_dir, file_coun=50):
        """将小图进行处理"""
        res = []
        pkl_index = 0
        for img_index, each_img_path in enumerate(FileOperationUtil.re_all_file(small_img_dir, lambda x:str(x).endswith('.jpg'))):
            # 只是提取前 100 个特征即可
            each_des = MatchSmallImage.get_sift_des(each_img_path)[:400]
            res.append((os.path.split(each_img_path)[1], each_des))
            print(img_index, each_img_path)
            if (img_index+1) % file_coun == 0:
                save_path = os.path.join(save_dir, "{0}.pkl".format(pkl_index))
                pkl_index += 1
                PickleUtil.save_data_to_pickle_file(res, save_path)
                print("save file --> {0}".format(save_path))
                res = []

        # 保存剩余的数据
        if len(res) != 0:
            save_path = os.path.join(save_dir, "{0}.pkl".format(pkl_index))
            PickleUtil.save_data_to_pickle_file(res, save_path)
            print("save file --> {0}".format(save_path))

    @staticmethod
    @DecoratorUtil.time_this
    def find_match_with_pkl_file(img_des, pkl_file):
        """从存储在本地文件中的小图中寻找匹配的图"""
        res_name_list = []
        des_1 = MatchSmallImage.get_sift_des(img_des)

        # 随机拿其中的百分之一的特征
        np.random.shuffle(des_1)
        des_1 = des_1[:int(des_1.shape[0]/10)]

        print("OK")

        des_list = PickleUtil.load_data_from_pickle_file(pkl_file)
        print(len(des_list))

        for each in des_list:
            img_name, each_des = each
            res = MatchSmallImage.get_match_index_between_des(des_1, each_des)
            # print(each_des.shape)
            if res > 10**-10:
                res_name_list.append(img_name)

        return res_name_list

    # todo 得到小图和大图之间的匹配关系，小图在大图中的位置

    # todo 得到小图和大图之间的匹配关系




if __name__ == "__main__":


    a = HashImageUtil()
    # 指定缓存文件存放文件夹
    a.save_num = 1000
    a.db_save_dir = r"C:\Users\14271\Desktop\del\del"
    # 指定数据库文件夹
    a.db_dir_list = [
        r"D:\data\001_fzc_优化相关资料\dataset_fzc\000_0_标准测试集\JPEGImages"]
    # 初始化
    a.do_init()
    a.update_db()
    # 需要数据库中指定相似的图片
    res = a.find_most_similar_img(r"C:\Users\14271\Desktop\save_res_2\test.jpg", img_count=1)

    for each in res:
        print(each)
