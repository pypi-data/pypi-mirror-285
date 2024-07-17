# -*- coding: utf-8  -*-
# -*- author: jokker -*-


import os
import logging
import logging.config
import logging.handlers
from logging.handlers import RotatingFileHandler


#定义日志格式级别
format_dict = {
    1 : logging.Formatter("%(message)s"),
    2 : logging.Formatter("%(levelname)s - %(message)s"),
    3 : logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"),
    4 : logging.Formatter("%(asctime)s - %(levelname)s - %(message)s - [%(name)s]"),
    5 : logging.Formatter("%(asctime)s - %(levelname)s - %(message)s - [%(name)s:%(lineno)s]")
}

class LogUtil(object):

    @staticmethod
    def get_log(log_path, loglevel, logger_name, print_to_console=True):
        if not os.path.exists(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path))

        # 创建一个logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件，设定文件的多少，单个文件的大小，
        fh = RotatingFileHandler(log_path, mode='a', maxBytes=25*1024*1024, backupCount=20)
        fh.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        formatter = format_dict[int(loglevel)]
        fh.setFormatter(formatter)
        # 给logger添加handler
        logger.addHandler(fh)

        if print_to_console:
            # 再创建一个handler，用于输出到控制台
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        return logger







