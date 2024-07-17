# -*- coding: utf-8  -*-
# -*- author: jokker -*-

import pickle
import uuid
import os
import base64
from tempfile import NamedTemporaryFile
import hashlib

try:
    from cryptography.fernet import Fernet
except ImportError:
    print('\x1b[1;31m' + 'import cryptography error : PickleUtil' + '\033[0m')


class PickleUtil(object):

    @staticmethod
    def load_data_from_pickle_file(pickle_file_path):
        with open(pickle_file_path, 'rb') as pickle_file:
            return pickle.load(pickle_file)

    @staticmethod
    def save_data_to_pickle_file(data, pickle_file_path):
        with open(pickle_file_path, 'wb') as pickle_file:
            pickle.dump(data, pickle_file)

    @staticmethod
    def _get_key(key_str):
        key = key_str.encode()
        return base64.urlsafe_b64encode(hashlib.sha256(key).digest())

    @staticmethod
    def encrypt_pickle(pkl_path, save_path, assign_key='jokker'):

        assign_key = PickleUtil._get_key(assign_key)
        cipher = Fernet(assign_key)

        # 加密 pickle 文件
        with open(pkl_path, 'rb') as f:
            encrypted_data = cipher.encrypt(f.read())

        # 保存加密的文件
        with open(save_path, 'wb') as f:
            f.write(encrypted_data)
        return assign_key

    @staticmethod
    def decrypt_pickle(pkl_path, assign_key='jokker'):
        assign_key = PickleUtil._get_key(assign_key)
        cipher = Fernet(assign_key)

        # 解密加密的 pickle 文件
        try:
            with open(pkl_path, 'rb') as f:
                decrypted_data = cipher.decrypt(f.read())
        except Exception as e:
            print('\x1b[1;31m' + 'InvalidToken, 密码错误' + '\033[0m')
            return None

        # 使用临时文件存贮中间文件
        with NamedTemporaryFile(mode='w+b') as f:
            f.write(decrypted_data)
            f.seek(0)
            data = pickle.load(f)

        return data


if __name__ == '__main__':

    from JoTools.txkjRes.deteRes import DeteRes

    a = DeteRes(r"C:\Users\14271\Desktop\del\gt_xml\005305_jpg.rf.4bfbcf630358ee01c2a6a2c1da620f63.xml")

    a.print_as_fzc_format()

    pickle_path = r'C:\Users\14271\Desktop\a.pkl'

    PickleUtil.save_data_to_pickle_file(a, pickle_path)

    PickleUtil.encrypt_pickle(pickle_path, pickle_path, "default_key")

    res = PickleUtil.decrypt_pickle(pickle_path, "default_key")

    res.print_as_fzc_format()



