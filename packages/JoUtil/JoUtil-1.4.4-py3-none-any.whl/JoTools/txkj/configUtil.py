# -*- coding: utf-8  -*-
# -*- author: jokker -*-

import configparser


# 解析我们常用的配置文件中的信息

class ConfigUtil(object):

    def __init__(self, config_path):
        self.cf = configparser.ConfigParser()
        self.cf.read(config_path, encoding='utf-8')
        #
        self.version = None
        self.debug = None
        self.model = None
        self.encryption = None
        self.run_mode = None
        self.color_dict = None
        #
        self.track_info = {}
        self.section_info = {}
        #
        self.parse_info()

    def parse_info(self):
        """解析数据"""

        # 版本信息
        self.version = self.cf.get('version', 'version') if self.cf.has_option('version', 'version') else None
        # 解析 common section
        self.parse_common_info("common", ["debug", "model", "encryption", "run_mode", "color_dict"])
        # 解析 track 信息
        self.parse_track_info()

    def parse_common_info(self, section, option_list):
        """解析 common section"""
        if not self.cf.has_section(section):
            return

        for each_option in option_list:
            if self.cf.has_option(section, each_option):
                exec('self.{0} = self.cf.get("common", "{0}")'.format(each_option))

    def parse_section_info(self, section_name):
        """解析指定 section 信息"""
        if not self.cf.has_section(section_name):
            return

        section_dict = {}
        for each_option in self.cf.items(section_name):
            section_dict[each_option[0]] = each_option[1]
        self.section_info[section_name] = section_dict

    @staticmethod
    def _get_input_from_track_section(section_info):
        """从 track 中的信息中找到 section 名 和 输入数据"""
        # 括号里面放的是输入的参数
        section_name, input_str = section_info.split('(')
        # 去掉空格
        print(input_str)
        if input_str.strip(')').strip():
            input_list = input_str.strip(')').split(',')
            input_list = list(map(lambda x:x.strip(), input_list))
            return section_name, input_list
        else:
            return section_name, []

    def parse_track_info(self):
        """解析 track 部分"""

        if not self.cf.has_section("track"):
            return

        # parse track info
        for (script, section) in self.cf.items("track"):
            if ',' in script:
                model_name_list = script.split(',')
                # delete space
                section = section.replace(" ", "")
                section_name_list = section.split('),')
                #
                for (script_mul, section_mul) in zip(model_name_list, section_name_list):
                    if script_mul in self.track_info:
                        section_name, input_list = self._get_input_from_track_section(section_mul)
                        self.track_info[script_mul].append({"section_name":section_name, "input":input_list})
                    else:
                        section_name, input_list = self._get_input_from_track_section(section_mul)
                        self.track_info[script_mul]  = [{"section_name":section_name, "input":input_list}]
            else:
                section_name, input_list = self._get_input_from_track_section(section)
                self.track_info[script] = [{"section_name": section_name, "input": input_list}]

        # parse section info
        for each_script_name in self.track_info:
            for each_section_info in self.track_info[each_script_name]:
                self.parse_section_info(each_section_info["section_name"])

    def print(self):
        """打印"""
        print('-'*80)
        for each_option in ["version", "debug", "model", "encryption", "run_mode", "color_dict"]:
            print(each_option.ljust(20, ' '), eval("self.{0}".format(each_option)))
        #
        print('-'*80)
        for each in self.track_info.items():
            print(each)

        print('-'*80)
        for each in self.section_info.items():
            print(each)


if __name__ == "__main__":

    cp = r"C:\Users\14271\Desktop\del\config.ini"

    a = ConfigUtil(cp)

    a.print()







