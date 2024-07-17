# -*- coding: utf-8  -*-
# -*- author: jokker -*-


from JoTools.utils.JsonUtil import JsonUtil
from JoTools.txkjRes.deteObj import PointObj, LineObj, LineStripObj, CricleObj, PolygonObj, RectangleObj

json_path = r"C:\Users\14271\Desktop\关键点\images.json"
json_info = {"polygon":None, "rectangle":None, "circle":None, "line_strip":None, "line":None, "point":None}


a = JsonUtil.load_data_from_json_file(json_path, encoding='GBK')


# # parse attr
# self.version = a["version"] if "version" in a else ""
# self.width = a["imageWidth"] if "imageWidth" in a else ""
# self.height = a["imageHeight"] if "imageWidth" in a else ""
# self.file_name = a["imagePath"] if "imagePath" in a else ""
# self.image_data_bs64 = a["imageData"]

obj_index = -1
for each_shape in a["shapes"]:
    each_shape_type = each_shape["shape_type"]  # 数据的类型 point,
    #
    obj_index += 1
    each_label = each_shape["label"]
    # point
    if each_shape_type == 'point':
        each_x, each_y = each_shape["points"][0]
        new_point = PointObj(each_x, each_y, each_label, assign_id=obj_index)
        self.alarms.append(new_point)
    # rectangle
    elif each_shape_type == 'rectangle':
        (x1, y1), (x2, y2) = each_shape["points"][0], each_shape["points"][1]
        new_rectangle = RectangleObj(x1, y1, x2, y2, tag=each_label, assign_id=obj_index)
    # circle
    elif each_shape_type == 'circle':
        (center_x, center_y), (point_x, point_y) = each_shape["points"][0], each_shape["points"][1]
        new_rectangle = CricleObj(center_x, center_y, point_x, point_y, tag=each_label, assign_id=obj_index)
    # polygon
    elif each_shape_type == 'polygon':
        new_polygon = PolygonObj(tag=each_label, assign_id=obj_index)
        for each_point in each_shape["points"]:
            new_polygon.add_point(each_point[0], each_point[1], tag="poly_point")
    # line
    elif each_shape_type == 'line':
        (start_x, start_y), (end_x, end_y) = each_shape["points"][0], each_shape["points"][1]
        new_rectangle = LineObj(start_x, start_y, end_x, end_y, tag=each_label, assign_id=obj_index)
    # line strip
    elif each_shape_type == 'line_strip':
        new_line_strip = LineStripObj(tag=each_label, assign_id=obj_index)
        for each_point in each_shape["points"]:
            new_line_strip.add_point(each_point[0], each_point[1], tag="line_strip_point")
    else:
        raise TypeError("type not support : {0}".format(each_shape_type))

