# -*- coding: utf-8  -*-
# -*- author: jokker -*-

import redis
import datetime
from JoTools.utils.DecoratorUtil import DecoratorUtil
from JoTools.utils.HashlibUtil import HashLibUtil
from JoTools.utils.FileOperationUtil import FileOperationUtil

# todo 创建自己的 UC 规则
# todo 将 UC 的位数设置为每天 1000 * 1000 * 1000 位数
# todo 其实限制每一秒只分配一个 UC 即可，知道分配 UC 的时间点 + MD5 就能唯一地确定这个 UC
# todo UC 中包含文件的类型信息 + 时间信息
# todo 析构函数能在出意外的时候保存 新申请的 UC dict

# todo 是否可以使用 resids 代替数据库


# fixme json 的定位是记录所有的数据，没有其他所有部分，依靠 json 和 data 能全部恢复
# fixme redis 等数据库的定位在于更快地执行（1）更快地获取 UC （2）更快地查询标签 UC 等

# todo (1) 保持 md5 与 UC 强相关，不会出现多次申请 md5 乱跑的问题
# todo (2) 不按照顺序生成 UC 解决无法完美多线程问题

# todo 标签名要和标签类型相对应，若是没有对应类型的标志如 R 代表旋转框，那么默认为正框，就是未旋转的矩形框

# fixme 使用 redis 的五张表就能代替 mysql
# fixme MD5 hash 用于查询 md5 是否有被使用过
# fixme UC-MD5 哈希表
# fixme tags set 表
# fixme tag-uc set 表，
# fixme -tag-uc set 表，标记某一个标签不存在某一个 UC 中
# fixme 一个记录数据类型的表，jpg JPG PNG 等等，用于快速获取数据类型
# todo 是否还需要，某张表中不存在某一标签这个功能？这个信息在 json 中存放着

# fixme 可复杂性 | 简约 , 表达的就是一个意思，抓住本质，




class UCGenerator(object):
    """redis 的使用仅仅是为了加速和防止丢失以及安全，没有 redis，在本地使用字典文件照样可以生成 UC"""

    _NUMB_CHAR_DICT = {
        0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i', 9: 'j', 10: 'k', 11: 'm', 12: 'n',
        13: 'p', 14: 'q', 15: 'r', 16: 's', 17: 't', 18: 'u', 19: 'v', 20: 'w', 21: 'x', 22: 'y', 23: 'z', 24: '0',
        25: '1', 26: '2', 27: '3', 28: '4', 29: '5', 30: '6', 31: '7', 32: '8', 33: '9'}

    _CHAR_NUMB_DICT = {
        'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'm': 11, 'n': 12,
        'p': 13, 'q': 14, 'r': 15, 's': 16, 't': 17, 'u': 18, 'v': 19, 'w': 20, 'x': 21, 'y': 22, 'z': 23, '0': 24,
        '1': 25, '2': 26, '3': 27, '4': 28, '5': 29, '6': 30, '7': 31, '8': 32, '9': 33}

    _YEAR_CHAR_DICT = {2019: 'A', 2020: 'B', 2021: 'C', 2022: 'D', 2023: 'E', 2024: 'F', 2025: 'G', 9999: "Z"}

    _CHAR_YEAR_DICT = {'A': 2019, 'B': 2020, 'C': 2021, 'D': 2022, 'E': 2023, 'F': 2024, 'G': 2025, 'Z': 9999}

    _MAX_INDEX = 34 ** 5

    def __init__(self, host, port):
        # todo 给 redis 增加密码，增加安全性
        self._host = host
        self._port = port
        self.r = redis.StrictRedis(host=host, port=port, decode_responses=True)
        #
        # self._init_redis()

    def _init_redis(self):
        """初始化 redis 中的表"""

        # 貌似这些表根本不需要初始化，没有数据会直接返回 None

        # MD5_UC
        if "MD5_UC" not in self.r.keys():
            self.r.hset('MD5_UC', 'md5', 'uc')
        # MD5_set
        if "MD5_SET" not in self.r.keys():
            self.r.sadd("MD5_SET", 'md5_demo')
        # UC_set
        if "UC_SET" not in self.r.keys():
            self.r.sadd("UC_SET", 'uc_demo')
        # tags
        if "TAG_SET" not in self.r.keys():
            self.r.sadd("TAG_SET", "demo")
        # TAG_UC
        if "TAG_UC" not in self.r.keys():
            self.r.hset("TAG_UC", "tag_demo", "uc_demo")
        # UC_SUFFIX
        if "UC_SUFFIX" not in self.r.keys():
            self.r.hset("UC_SUFFIX", "uc_demo", "suffix_demo")

        print(self.r.keys())

    def _add_md5(self, md5):
        """插入 md5"""

        if self.r.sismember('MD5_SET', md5):
            return

        region_md5 = md5
        now = datetime.datetime.now()
        year, month, day = now.year, now.month, now.day
        uc_part1 = UCGenerator._YEAR_CHAR_DICT[year] + UCGenerator._NUMB_CHAR_DICT[month] + UCGenerator._NUMB_CHAR_DICT[day]
        crash_index = 0
        while True:
            serial_number = hash(md5) % UCGenerator._MAX_INDEX
            remainder_1 = serial_number % 34
            quotient_1 = serial_number // 34
            remainder_2 = quotient_1 % 34
            quotient_2 = quotient_1 // 34
            remainder_3 = quotient_2 % 34
            quotient_3 = quotient_2 // 34
            remainder_4 = quotient_3 % 34
            quotient_4 = quotient_3 // 34
            remainder_5 = quotient_4 % 34  # 取余数
            #
            letter_1 = UCGenerator._NUMB_CHAR_DICT[remainder_1]
            letter_2 = UCGenerator._NUMB_CHAR_DICT[remainder_2]
            letter_3 = UCGenerator._NUMB_CHAR_DICT[remainder_3]
            letter_4 = UCGenerator._NUMB_CHAR_DICT[remainder_4]
            letter_5 = UCGenerator._NUMB_CHAR_DICT[remainder_5]
            uc_part2 = letter_5 + letter_4 + letter_3 + letter_2 + letter_1
            uc = uc_part1 + uc_part2

            if self.r.sismember('UC_SET', uc):
                crash_index += 1
                # 碰撞次数大于 5 异常，查看原因，查看是否 UC 机制出现问题
                assert crash_index < 5
                md5 += str(crash_index)
                print(f"* crash_index : {crash_index}, 不同 md5 存在重复的 UC 继续碰撞")
            else:
                p_1 = self.r.hset('MD5_UC', region_md5, uc)
                p_2 = self.r.sadd('MD5_SET', region_md5)
                p_3 = self.r.sadd('UC_SET', uc)
                # todo 如果三个操作有任意一个失败，直接回滚上面的操作
                break

    def get_uc(self, md5):
        """增加一个 md5 获取一个 UC"""
        self._add_md5(md5)
        return self.r.hget('MD5_UC', md5)

    def md5_in_redis(self, md5):
        """MD5是否在 redis 数据库中"""
        if self.r.sismember('MD5_SET', md5):
            return True
        else:
            return False

    def uc_in_redis(self, uc):
        """是否是符合规范的 uc，在库中的就是符合规范的，不在的就不是符合规范的"""
        if self.r.sismember('UC_SET', uc):
            return True
        else:
            return False


class JsonReis(object):
    """将 json 中用于查询的信息写在 redis 中，redis 的作用只是为了加速，所有信息来自于 json"""

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self.r = redis.StrictRedis(host=host, port=port, decode_responses=True)





@DecoratorUtil.time_this
def main():
    a = UCGenerator('192.168.3.221', '6379')
    imgDir = r"D:\data\001_fzc_优化相关资料\dataset_fzc\000_0_标准测试集\JPEGImages"
    #
    for index, each_img_path in enumerate(FileOperationUtil.re_all_file(imgDir, endswitch=['.jpg'])):
        img_md5 = HashLibUtil.get_file_md5(each_img_path)
        print(index, a.get_uc(img_md5))


if __name__ == "__main__":

    main()






