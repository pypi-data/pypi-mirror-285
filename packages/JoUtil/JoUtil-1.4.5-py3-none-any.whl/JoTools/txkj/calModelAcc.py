# -*- coding: utf-8  -*-
# -*- author: jokker -*-
# -*- author: fbc | jokker-*-

import os
import shutil
import prettytable as pt
import xml.etree.ElementTree as ET


class CalModelAcc(object):
    """ 计算模型，正确率，召回率 """

    def __init__(self):
        self.gt_xml_dir = r"C:\data\test_data\防振锤计算模型精度\测试集标注"          # 人工标注的结果
        self.pr_xml_dir = r"C:\Users\14271\Desktop\merge"                           # 算法检测的结果
        self.img_path = r"C:\Users\14271\Desktop\result"                            # 检测结果文件夹
        #
        self.label_list = ["Fnormal", "fzc_broken"]                                 # xml 中的分类
        # self.label_list = ["fzc"]                                                 # xml 中的分类
        self.iou_thershold = 0.4                                                    # 判定两矩形重合的 iou 阈值
        self.metrics_list = ["miss", "extra", "correct", "mistake"]                 # 分类结果
        self.metric_name = ["漏检", "多检", "正确", "误检"]                          # 分类结果中文名
        self.copy_img = True                                                        # 是否将识别错误的图片进行保存
        self.save_res_path = r""                                                    # 保存拷贝数据文件夹

    def xml_read(self, xml_path):
        """读取 xml 信息"""
        voc_labels = []
        print(xml_path)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for obj in root.iter('object'):
            label = obj.find('name').text
            if label not in self.label_list:
                continue
            bndbox = obj.find('bndbox')
            xmin = int(float(bndbox.find('xmin').text))
            xmax = int(float(bndbox.find('xmax').text))
            ymin = int(float(bndbox.find('ymin').text))
            ymax = int(float(bndbox.find('ymax').text))
            # fixme 默认值 false 为了标记，是否与其他框进行了比较，和其他框进行了比较，这个值就设置为 True，就不会定义为 漏检？这块好号看看
            voc_labels.append([label, [xmin, ymin, xmax, ymax], False])
        return voc_labels

    def cal_iou(self, gt_box, pr_box):
        """计算相交程度, xmin, ymin, xmax, ymax"""
        # xmin, ymin, xmax, ymax
        dx = max(min(gt_box[2], pr_box[2]) - max(gt_box[0], pr_box[0]) + 1, 0)
        dy = max(min(gt_box[3], pr_box[3]) - max(gt_box[1], pr_box[1]) + 1, 0)
        overlap_area = dx * dy
        union_area = ((gt_box[2] - gt_box[0] + 1) * (gt_box[3] - gt_box[1] + 1) + (pr_box[2] - pr_box[0] + 1) * (pr_box[3] - pr_box[1] + 1) - overlap_area)
        return overlap_area * 1. / union_area

    def comparison(self, total_imgs, extra_imgs, miss_imgs):
        """对比"""
        miss, extra, correct, mistake = {}, {}, {}, {}

        # fixme 遍历所有的 xml
        for i, xml in enumerate(total_imgs):
            # fixme 这边放的是多出来的 xml
            if xml in extra_imgs:
                pr_xml_path = os.path.join(self.pr_xml_dir, xml)
                pr_objects = self.xml_read(pr_xml_path)
                pr_objects = [[label, box] for label, box, _ in pr_objects]
                extra[xml] = pr_objects
            # fixme 这边放的是少的 xml
            elif xml in miss_imgs:
                gt_xml_path = os.path.join(self.gt_xml_dir, xml)
                gt_objects = self.xml_read(gt_xml_path)
                gt_objects = [[label, box] for label, box, _ in gt_objects]
                miss[xml] = gt_objects
            # fixme 这边存放的是有对照 xml 的图片
            else:
                miss[xml], extra[xml], correct[xml], mistake[xml] = [], [], [], []   # 一个 xml 是一个 key ，对应的 value 是

                gt_xml_path = os.path.join(self.gt_xml_dir, xml)
                pr_xml_path = os.path.join(self.pr_xml_dir, xml)

                gt_objects = self.xml_read(gt_xml_path)     # 人工标注的结果
                pr_objects = self.xml_read(pr_xml_path)     # 模型跑出来的结果

                overlap_dict = {}       # 重叠字典

                # fixme 遍历预测的结果
                for pr_index, pr_obj in enumerate(pr_objects):
                    _, pr_box, _ = pr_obj
                    overlap_dict[pr_index] = []

                    for gt_index, gt_obj in enumerate(gt_objects):
                        _, gt_box, _ = gt_obj
                        iou = self.cal_iou(gt_box, pr_box)                                          # 计算标图和预测出来的矩形范围的相交程度 iou
                        if iou > self.iou_thershold:
                            pr_objects[pr_index][2], gt_objects[gt_index][2] = True, True           # 当有框已经被识别了，这个框的标签改为 True，即当前框已经被识别
                            overlap_dict[pr_index].append([gt_index, iou])

                # --------------------------------------------------------------------------

                for pr_index, pr_obj in enumerate(pr_objects):
                    pr_label, pr_box, pr_flag = pr_obj
                    # fixme 如果被标记为已经识别
                    if pr_flag:
                        # fixme 如果某一个预测出来的框，对应一个人工识别出来的框
                        if len(overlap_dict[pr_index]) == 1:
                            gt_index, _ = overlap_dict[pr_index][0]
                            gt_label, gt_box, _ = gt_objects[gt_index]
                            # fixme 当框相同，标签也一一致的情况下，认为是识别对的
                            if pr_label == gt_label:
                                correct[xml].append(pr_obj)
                            else:
                                # fixme 框相同，但是标签不一致，认为识别错误
                                mistake[xml].append([gt_label, pr_label])

                        # fixme 如果某一个预测出来的框，对应多个人工识别出来的框
                        else:
                            iou_list = [iou for _, iou in overlap_dict[pr_index]]
                            gt_index, _ = overlap_dict[pr_index][iou_list.index(max(iou_list))]
                            gt_label, gt_box, _ = gt_objects[gt_index]
                            if pr_label == gt_label:
                                correct[xml].append([pr_label, pr_box])
                            else:
                                mistake[xml].append([gt_label, pr_label])

                    else:
                        extra[xml].append([pr_obj[0], pr_obj[1]])

                miss_gt_objects = [obj for obj in gt_objects if not obj[-1] and len(obj) != 0]
                for gt_index, gt_obj in enumerate(miss_gt_objects):
                    miss[xml].append([gt_obj[0], gt_obj[1]])

        return miss, extra, correct, mistake

    def get_result(self, _dict):
        """根据统计结果拿到统计的表述信息"""

        # 拿到字典的值，现在字典的键不重要
        objects = []
        for k, v in _dict.items():
            for each in v:
                objects.append([k, each])

        # 按照标签进行分类
        res = {}
        for label in self.label_list:
            if label not in res:
                res[label] = []
            for each_obj in objects:
                if label == each_obj[1][0]:
                    res[label].append(each_obj)
        return res

    def copy_res_img(self, res_dict, folder_name):
        """拷贝文件夹"""

        # 正确类型的不进行拷贝
        if folder_name == self.metric_name[2]:
            return

        # 遍历文件标签
        for each_label in res_dict:
            folder_path = os.path.join(self.save_res_path, folder_name, each_label)
            # 如果文件夹不存在
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            #
            for each_check_info in res_dict[each_label]:
                each_xml_name = each_check_info[0]
                each_img_name = each_xml_name[:-4] + '.jpg'
                each_img_path = os.path.join(self.img_path, each_img_name)
                save_img_path = os.path.join(folder_path, each_img_name)

                if os.path.exists(save_img_path):
                    # print("文件已存在 ：{0}".format(save_img_path))
                    pass
                elif os.path.exists(each_img_path):
                    shutil.copyfile(each_img_path, save_img_path)
                else:
                    print("缺少文件 ：{0}".format(each_img_path))

    def get_result_error(self, _dict):
        """根据统计结果拿到统计的表述信息"""

        # 拿到字典的值，现在字典的键不重要
        objects = []
        for k, v in _dict.items():
            for each in v:
                objects.append([k, each])

        # 按照标签进行分类
        res = {}
        for label0 in self.label_list:
            for label1 in self.label_list:
                # 去掉相同的标签
                if label0 == label1:
                    continue
                each_label = label0 + "-" + label1
                #
                if each_label not in res:
                    res[each_label] = []
                #
                for each_obj in objects:
                    #
                    if label0 == each_obj[1][0] and label1 == each_obj[1][1]:
                        res[each_label].append(each_obj)
        return res

    def objects_count(self, xml_dir, gt=False):
        """统计 xml 文件夹中的个数，找到元素的个数"""
        tot_objects = []
        results = {}

        xml_list = [i for i in os.listdir(xml_dir) if i.endswith(".xml")]
        for index, xml in enumerate(xml_list):
            xml_path = os.path.join(xml_dir, xml)
            # print(index)
            objects = self.xml_read(xml_path)

            if len(objects) != 0:
                tot_objects.extend(objects)
            else:
                if not gt:
                    print("no objects in {}".format(xml_path))

        for label in self.label_list:
            results[label] = len([obj for obj in tot_objects if obj[0] == label])
        return len(tot_objects), results

    def do_process(self):
        """主流程"""
        print("-"*80)
        gt_xml_list = [xml for xml in os.listdir(self.gt_xml_dir) if xml.endswith(".xml")]
        pr_xml_list = [xml for xml in os.listdir(self.pr_xml_dir) if xml.endswith(".xml")]
        print("测试集   {0} 张".format(len(gt_xml_list)))
        print("预测结果 {0} 张".format(len(pr_xml_list)))

        gt_objects_num, gt_results = self.objects_count(self.gt_xml_dir, gt=True)
        pr_objects_num, pr_rough_results = self.objects_count(self.pr_xml_dir)

        print("应检目标 {0} 个 : {1}".format(gt_objects_num, gt_results))
        print("检出目标 {0} 个 : {1}".format(pr_objects_num, pr_rough_results))
        print("-"*80)

        # 这边如果不存在对应的 xml 就认为没检测出来？
        total_imgs = list(set(gt_xml_list) | set(pr_xml_list))
        common_imgs = list(set(gt_xml_list) & set(pr_xml_list))
        extra_imgs = list(set(pr_xml_list) - set(gt_xml_list))
        miss_imgs = list(set(gt_xml_list) - set(pr_xml_list))

        statics = self.comparison(total_imgs, extra_imgs, miss_imgs)                            # 对 xml 信息进行统计对比
        statics_table = pt.PrettyTable()
        statics_table.field_names = ["type", "label", "count"]
        for i, metric in enumerate(statics):
            # 对误检进行特殊处理
            if i != 3:
                res_dict = self.get_result(metric)
            else:
                res_dict = self.get_result_error(metric)

            # 对结果进行拷贝
            # self.copy_res_img(res_dict, self.metric_name[i])                                    # 检测有问题的图片拷贝出来看
            for each in res_dict.keys():
                statics_table.add_row([self.metric_name[i], each, len(res_dict[each])])
        #
        print(statics_table)

        # ----------------------------------------------------------



if __name__ == "__main__":
    
    # todo 多检，漏检，误检用不用的颜色进行标注，不用直接在

    # todo 貌似有问题，需要好好检查一下

    a = CalModelAcc()
    a.label_list = ["Fnormal", "fzc_broken"]
    # a.label_list = ["K", "Lm", "Xnormal"]
    # a.label_list = ["fzc"]
    a.iou_thershold = 0.4

    a.gt_xml_dir = r"C:\data\fzc_优化相关资料\防振锤优化\000_标准测试集\xml_remove_zd"
    #
    # a.pr_xml_dir = r"C:\Users\14271\Desktop\result\res"
    a.pr_xml_dir = r"C:\Users\14271\Desktop\result_v0.2.0-A"
    a.img_path = r"C:\data\fzc_优化相关资料\防振锤优化\000_标准测试集\img"
    #
    a.save_res_path = r"C:\Users\14271\Desktop\对比版本结果\v0.2.0-A"

    a.do_process()
