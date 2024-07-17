# -*- coding: utf-8  -*-
# -*- author: jokker -*-



"""
* 实现各个版本的 post 代码，不用来回去找了
"""

import base64
import io
from PIL import Image
import urllib.parse
import time
import requests
import requests
import os
import json
import uuid
from JoTools.utils.FileOperationUtil import FileOperationUtil
from JoTools.utils.JsonUtil import JsonUtil
from JoTools.txkjRes.deteRes import DeteRes



class PostUtil():

    @staticmethod
    def img_to_base64(img_path):
        image = Image.open(img_path)
        image_buffer = io.BytesIO()
        image.save(image_buffer, format='JPEG')
        image_bytes = image_buffer.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        return image_base64

    @staticmethod
    def post_feihua(post_url='http://192.168.3.221:5001/dete', each_img_path="", model_name="gzf"):
        """北京飞华项目"""
        headers = {'Content-Type': 'text/plain'}
        img_base_64 = PostUtil.img_to_base64(each_img_path)
        payload = {
            "image": img_base_64,
            "uuid": "abad6a3f-8a98-41ad-8c59-0960def9e03d",
            "modelName": model_name,
            "imageBase64": img_base_64,
            "imageUrl": "",
            "ext": "",
        }

        response = requests.post(post_url, headers=headers, json=payload)
        dete_res = DeteRes()
        res = JsonUtil.load_data_from_json_str(response.text)

        # res to DeteRes
        for each in res["data"]["res"]:
            dete_res.add_obj(x1=each["x1"], y1=each["y1"], x2=each["x2"], y2=each["y2"], tag=each["tag"],
                      conf=each["confidence"])
        return dete_res

    @staticmethod
    def post_v0(post_url='http://192.168.3.221:11223/dete', img_path="", model_list="nc,kkx"):
        files = {'image': open(img_path, 'rb')}
        data = {'image_name': "test_name", "model_list": ",".join(model_list)}
        res = requests.post(url=post_url, json=data, files=files)
        print(res)
        print(res.text)

    @staticmethod
    def post_v2(post_url=r"http://192.168.3.221:5001/dete", model_list="nc,kkx", ucd_path="", receive_url=r"http://192.168.3.221:1223", heart_beat_url="http://192.168.3.221:1223/heart_beat"):
        """标准 v2 接口"""
        data = {
            "model_list"        : model_list,
            "img_path_list"     : "",
            "post_url"          : receive_url,
            "heart_beat_url"    : heart_beat_url,
            "batch_id"          : "Repeated_output_001" + str(uuid.uuid1())
        }

        a = JsonUtil.load_data_from_json_file(ucd_path)
        img_path_list = []
        for each_uc in a["uc_list"]:
            img_path = f"http://192.168.3.111:11101/file/{each_uc}.jpg"
            img_path_list.append(r",{0}-+-{1}".format(img_path, each_uc))

        data["img_path_list"] = ",".join(img_path_list)
        response_data = requests.post(url=post_url, data=data)
        return response_data.text



