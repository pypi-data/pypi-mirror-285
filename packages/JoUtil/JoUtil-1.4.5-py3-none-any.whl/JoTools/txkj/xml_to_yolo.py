# -*- coding: utf-8  -*-
# -*- author: jokker -*-


import os
from JoTools.txkjRes.deteRes import DeteRes
from JoTools.utils.FileOperationUtil import FileOperationUtil

xml_dir = r"C:\Users\14271\Desktop\xml"
res_dir = r"C:\Users\14271\Desktop\txt"

tag_list = ["aqm","aqm_error","aqm_miss","error","gz","gzf","gzf_error","gzf_miss","hmj","kz","kz_error","qz","st","st_error","st_miss","xz","xz_error","ydb"]
tag_map = {}
for index, each in enumerate(tag_list):
    tag_map[each] = index

index = 0
for each_xml_path in FileOperationUtil.re_all_file(xml_dir, endswitch=[".xml"]):
    index += 1
    print(index, each_xml_path)
    dete_res = DeteRes(each_xml_path)
    each_txt_path = os.path.join(res_dir, FileOperationUtil.bang_path(each_xml_path)[1] + ".txt")
    dete_res.save_to_yolo_txt(each_txt_path, tag_map)


    # dete_res.do_nms(threshold=0.1, ignore_tag=False)

    # # dete_res.filter_by_conf()
    # #
    # dete_res.filter_by_tags(remove_tag=["hmj", "qz", "gz", "ydb"], update=True)
    #
    # dete_res.reset_alarms()
    #













