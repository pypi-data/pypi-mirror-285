# -*- coding: utf-8  -*-
# -*- author: jokker -*-



import yaml
import numpy as np

# yaml_path = r"C:\Users\14271\Desktop\fzc.yaml"
#
# with open(yaml_path, "r", encoding="utf8") as f:
#     context = yaml.load(f, Loader=yaml.FullLoader)
#
# print(context["train"])




cache_path = r"C:\Users\14271\Desktop\train.cache"

a = np.load(cache_path, allow_pickle=True).item()

print(a)