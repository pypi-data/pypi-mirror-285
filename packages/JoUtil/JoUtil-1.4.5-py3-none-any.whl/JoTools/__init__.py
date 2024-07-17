# -*- coding: utf-8  -*-
# -*- author: jokker -*-



import sys
import os

# 没有下面三行代码，就会报错
this_dir = os.path.dirname(__file__)
lib_path = os.path.join(this_dir, '..')
sys.path.insert(0, lib_path)
