import onnxruntime
import numpy as np
import onnx
import cv2
import time
from JoTools.txkjRes.deteRes import DeteRes
from JoTools.utils.DecoratorUtil import DecoratorUtil

def filter_box(org_box,conf_thres,iou_thres): #过滤掉无用的框
    org_box=np.squeeze(org_box) #删除为1的维度
    conf = org_box[..., 4] > conf_thres #删除置信度小于conf_thres的BOX
    box = org_box[conf == True]
    cls_cinf = box[..., 5:]
    cls = []
    for i in range(len(cls_cinf)):
        cls.append(int(np.argmax(cls_cinf[i])))
    all_cls = list(set(cls))     #删除重复的类别
    
    output = []
    for i in range(len(all_cls)):
        curr_cls = all_cls[i]
        curr_cls_box = []
        curr_out_box = []
        for j in range(len(cls)):
            if cls[j] == curr_cls:
                box[j][5] = curr_cls #将第6列元素替换为类别下标
                curr_cls_box.append(box[j][:6])   #当前类别的BOX
        curr_cls_box = np.array(curr_cls_box)
        curr_cls_box = xywh2xyxy(curr_cls_box)
        curr_out_box = pynms(curr_cls_box,iou_thres) #经过非极大抑制后输出的BOX下标
        for k in curr_out_box:
            output.append(curr_cls_box[k])  #利用下标取出非极大抑制后的BOX
    output = np.array(output)
    return output

def draw(image,box_data):  #画图
    boxes=box_data[...,:4].astype(np.int32) #取整方便画框
    scores=box_data[...,4]
    classes=box_data[...,5].astype(np.int32) #下标取整

    for box, score, cl in zip(boxes, scores, classes):
        top, left, right, bottom = box
        #print('class: {}, score: {}'.format(CLASSES[cl], score))
        # print('box coordinate left,top,right,down: [{}, {}, {}, {}]'.format(top, left, right, bottom))

        cv2.rectangle(image, (int(top), int(left)), (int(right), int(bottom)), (255, 0, 0), 2)
        cv2.putText(image, '{0} {1:.2f}'.format("test", score),
                    (top, left ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 255), 2)
    #img0 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
          
    cv2.imwrite("./hehe.jpg", image)

def get_dete_res(box_data, class_list):
    boxes=box_data[...,:4].astype(np.int32)
    scores=box_data[...,4]
    classes=box_data[...,5].astype(np.int32)
    dete_res = DeteRes()
    for box, score, cl in zip(boxes, scores, classes):
        left, top, right, bottom = box
        tag = class_list[cl]
        dete_res.add_obj(left, top, right, bottom, tag=str(tag), conf=float(score))
        #print(left, top, right, bottom, str(tag), score)
    return dete_res

def scale_coords(img1_shape, coords, img0_shape, ratio_pad=None):
    # Rescale coords (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    coords[:, [0, 2]] -= pad[0]  # x padding
    coords[:, [1, 3]] -= pad[1]  # y padding
    coords[:, :4] /= gain
    clip_coords(coords, img0_shape)
    return coords

def clip_coords(boxes, shape):
    # Clip bounding xyxy bounding boxes to image shape (height, width)
    if isinstance(boxes, np.ndarray):  # faster individually
        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, shape[0])  # y1, y2
    else:  # np.array (faster grouped)
        boxes[:, 0].clamp_(0, shape[1])  # x1
        boxes[:, 1].clamp_(0, shape[0])  # y1
        boxes[:, 2].clamp_(0, shape[1])  # x2
        boxes[:, 3].clamp_(0, shape[0])  # y2

def pynms(dets, thresh): #非极大抑制
    x1 = dets[:, 0]
    y1 = dets[:, 1]
    x2 = dets[:, 2]
    y2 = dets[:, 3]
    areas = (y2 - y1 + 1) * (x2 - x1 + 1)
    scores = dets[:, 4]
    keep = []
    index = scores.argsort()[::-1] #置信度从大到小排序（下标）

    while index.size > 0:
        i = index[0]
        keep.append(i)

        x11 = np.maximum(x1[i], x1[index[1:]])  # 计算相交面积
        y11 = np.maximum(y1[i], y1[index[1:]])
        x22 = np.minimum(x2[i], x2[index[1:]])
        y22 = np.minimum(y2[i], y2[index[1:]])

        w = np.maximum(0, x22 - x11 + 1)  # 当两个框不想交时x22 - x11或y22 - y11 为负数，
                                           # 两框不相交时把相交面积置0
        h = np.maximum(0, y22 - y11 + 1)  #

        overlaps = w * h
        ious = overlaps / (areas[i] + areas[index[1:]] - overlaps)#计算IOU

        idx = np.where(ious <= thresh)[0]  #IOU小于thresh的框保留下来
        index = index[idx + 1]  # 下标以1开始
        #print(index)

    return keep

def xywh2xyxy(x):
    # [x, y, w, h] to [x1, y1, x2, y2]
    y = np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2
    y[:, 1] = x[:, 1] - x[:, 3] / 2
    y[:, 2] = x[:, 0] + x[:, 2] / 2
    y[:, 3] = x[:, 1] + x[:, 3] / 2
    return y

def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return im, ratio, (dw, dh)


class Dete_onnx():

    def __init__(self):
        self.model = None
        self.class_list = []
        self.model_path = ""
        self.img_size = 640

    def model_restore(self, model_path, class_list, img_size, use_gpu=True):
        self.class_list = class_list
        self.img_size = img_size
        self.model_path = model_path
        if use_gpu:
            self.model = onnxruntime.InferenceSession(model_path, providers=['CUDAExecutionProvider'])
        else:
            self.model = onnxruntime.InferenceSession(model_path, providers=['CPUExecutionProvider'])

        input_data = np.random.randn(1, 3, self.img_size, self.img_size).astype(np.float32)
        self.model.run(None, {'images': input_data})

    @DecoratorUtil.time_this
    def detectSOUT(self, path="", image=""):

        try:
            if path != "":
                img0 = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)
                img0 = cv2.cvtColor(img0, cv2.COLOR_BGR2RGB)
            else:
                img0 = image

            img = letterbox(img0, (self.img_size, self.img_size), stride=32, auto=False)[0]
            img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR2RGB和HWC2CHW
            img = img.astype(dtype=np.float32)
            img /= 255.0
            img = np.expand_dims(img, axis=0)

            result = self.model.run(None, {'images': img})
            output = list(result[0][0])
            outbox = filter_box(output.copy(), 0.5, 0.5)
            outbox[:, :4] = scale_coords(img.shape[2:], outbox[:, :4], img0.shape).round()
            if len(output) > 0:
                dete_res = get_dete_res(outbox, self.class_list)
                return dete_res
            else:
                return DeteRes()

        except Exception as e:
            print(e)
            print(e.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            print(e.__traceback__.tb_lineno)  # 发生异常所在的行数
            return DeteRes()



if __name__ == "__main__":

    imgPath    = r"C:\Users\14271\Desktop\temp\test.jpg"
    modelPath  = r"C:\Users\14271\Desktop\temp\yolov5x.onnx"
    # model_path  = r"C:\Users\14271\Desktop\temp\yolov5x6.onnx"

    classNames = [
        'Person', 'Bicycle', 'Car', 'Motorcycle', 'Airplane', 'Bus', 'Train', 'Truck',
        'Boat', 'Traffic light', 'Fire hydrant', 'Stop sign', 'Parking meter', 'Bench',
        'Bird', 'Cat', 'Dog', 'Horse', 'Sheep', 'Cow', 'Elephant', 'Bear', 'Zebra',
        'Giraffe', 'Backpack', 'Umbrella', 'Handbag', 'Tie', 'Suitcase', 'Frisbee',
        'Skis', 'Snowboard', 'Sports ball', 'Kite', 'Baseball bat', 'Baseball glove',
        'Skateboard', 'Surfboard', 'Tennis racket', 'Bottle', 'Wine glass', 'Cup',
        'Fork', 'Knife', 'Spoon', 'Bowl', 'Banana', 'Apple', 'Sandwich', 'Orange',
        'Broccoli', 'Carrot', 'Hot dog', 'Pizza', 'Donut', 'Cake', 'Chair', 'Couch',
        'Potted plant', 'Bed', 'Dining table', 'Toilet', 'TV', 'Laptop', 'Mouse',
        'Remote', 'Keyboard', 'Cell phone', 'Microwave', 'Oven', 'Toaster', 'Sink',
        'Refrigerator', 'Book', 'Clock', 'Vase', 'Scissors', 'Teddy bear', 'Hair drier',
        'Toothbrush'
    ]

    a = Dete_onnx()
    a.model_restore(modelPath, classNames, 640, use_gpu=False)
    # a.model_restore(model_path, class_names, 1280, use_gpu=False)

    dete_res = a.detectSOUT(imgPath)
    dete_res.print_as_fzc_format()
    dete_res.img_path = imgPath
    dete_res.draw_dete_res(r"C:\Users\14271\Desktop\temp\hehe_123.jpg", line_thickness=2, )
















