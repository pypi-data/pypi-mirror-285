# -*- coding: utf-8  -*-
# -*- author: jokker -*-
import numpy as np
import math

class DetePoint(object):
    def __init__(self,x,y,shape = (1,),index=-1):
        self._x = x
        self._y = y
        self._value = np.array([x,y],dtype=np.float32)
        self._index = index

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y
    
    @property
    def index(self):
        return self._index

    @property
    def value(self):
        return self._value

    #@property
    #def prePointIndex(self):
    #    return self._preIndex

    #@property
    #def nextPointIndex(self):
    #    return self._nextIndex

    def __str__(self):
        return "x:"+str(self._x)+" "+"y:"+str(self._y)

    def __eq__(self,p):
        return self._x == p.x and self._y == p.y

class DeteLineObj(object):
    """检测结果的一个检测对象，就是一个矩形框对应的信息"""

    def __init__(self,points=None,weight=0,hight=0):
        """
        points：传入是一个点的列表
        lines: 传入是线的组合
        """
        self._points = [(int(x),int(y)) for x,y in points]
        self._nps = np.vstack(self._points)
        self.sortPoints()
        #self._head = DetePoint(points[0])
        self._end = points[-1]
        #self._value = np.array(points,dtype=np.float32)

        #print('x1')
        #print(self._value.shape)
        self._xmin = int(self._nps[:,0].argmin())
        self._ymin = int(self._nps[:,1].argmin())
        self._xmax = int(self._nps[:,0].argmax())
        self._ymax = int(self._nps[:,1].argmax())
        self._weight = max(weight,self._xmax)
        self._hight = max(hight,self._ymax)
        #print('x2')
        #for index,point in enumerate(points):
        #    self._points.append(DetePoint(point[0],point[1],index))

    def __len__(self):
        return len(self._points)

    def isEnd(self,point):
        if self._end == point:
            return True
        else:
            return False

    def sample(self,point_split_step,update=True,xInterpolation=10):
        """
        分割出的线一般是由大量点组成，sample函数提供对大量点采样的能力，让线变细
        原理是将图片从上到下进行均分，根据y的值判断是否有接近的点
        """
        sampled = []
        single_line_pt_x = self._nps[:,0]
        single_line_pt_y = self._nps[:,1]
        start_plot_y = 0
        end_plot_y = self._hight
        source_image_width = self._weight
        step = int(math.floor((end_plot_y - start_plot_y) / point_split_step))
        for plot_y in np.linspace(start_plot_y, end_plot_y, step):
            diff = single_line_pt_y - plot_y
            fake_diff_bigger_than_zero = diff.copy()
            fake_diff_smaller_than_zero = diff.copy()
            fake_diff_bigger_than_zero[np.where(diff <= 0)] = float('inf')
            fake_diff_smaller_than_zero[np.where(diff > 0)] = float('-inf')
            idx_low = np.argmax(fake_diff_smaller_than_zero)
            idx_high = np.argmin(fake_diff_bigger_than_zero)
            previous_src_pt_x = single_line_pt_x[idx_low]
            previous_src_pt_y = single_line_pt_y[idx_low]
            last_src_pt_x = single_line_pt_x[idx_high]
            last_src_pt_y = single_line_pt_y[idx_high]
            #print("previous_src_pt_x:",type(previous_src_pt_x))
            #print("previous_src_pt_y:",type(previous_src_pt_y))
            #print("last_src_pt_x:",type(last_src_pt_x))
            #print("last_src_pt_y:",type(last_src_pt_y))
            if previous_src_pt_y < start_plot_y or last_src_pt_y < start_plot_y or \
                          fake_diff_smaller_than_zero[idx_low] == float('-inf') or \
                          fake_diff_bigger_than_zero[idx_high] == float('inf'):
                 continue
            interpolation_src_pt_x = (abs(previous_src_pt_y - plot_y) * previous_src_pt_x + abs(last_src_pt_y - plot_y) * last_src_pt_x) / \
                                     (abs(previous_src_pt_y - plot_y) + abs(last_src_pt_y - plot_y))
            interpolation_src_pt_y = (abs(previous_src_pt_y - plot_y) * previous_src_pt_y + abs(last_src_pt_y - plot_y) * last_src_pt_y) / \
                                     (abs(previous_src_pt_y - plot_y) + abs(last_src_pt_y - plot_y))
            if interpolation_src_pt_x > source_image_width or interpolation_src_pt_x < xInterpolation:
                continue
            sampled.append((int(interpolation_src_pt_x),int(interpolation_src_pt_y)))
        if update:
            self._points = sampled
            self.updateValue()
        return sampled                                                                             

    def add_points(self,points):
        self._nps = np.vstack((self._nps,points))
        self.sortPoints()
        self.updateValue()

    def sortPoints(self,by='y'):
        if by == 'y':
            axis = 1
        else:
            axis = 0
        #self._nps = np.vstack(self._nps)
        self._nps = self._nps[self._nps[:,axis].argsort()]
        

    def updateValue(self):
        self._points = self._nps.tolist()


    def insertPoints(self,points,inBaseRange=True,update=True):
        for point in points:
            if inBaseRange and self.isInRange(point):
                self._points.extend(point)
        if update:
            self.updateValue()


    def isInRange(self,point):
        if point[0] in range(self._xmin,self._xmax) and point[1] in range(self._ymin,self._ymax):
            return True
        else:
            return False

    def dbscan(self):
        """
        使用DBSCAN对点进行聚类
        """
        pass

    def save(self,path):
        np.savetxt(path,self._nps,fmt='%s,%s')

    def split_lines(self,distx=100,disty=50): 
        """
        逐一比较点与点之间的间距，如果差别较大，就认为是另外一条线的点
        """
        lines = {}
        i = 0
        first = self._points[0]
        while i < len(self._points):
            deploy = False
            point = tuple(self._points[i])
            x = point[0]
            y = point[1]
            for key in lines.keys():
                breakFlag = False
                for p in lines[key]:
                    if abs(p[0]-point[0])<distx and abs(p[1]-point[1])<disty:
                        breakFlag = True
                        lines[key].append(point)
                        deploy = True
                    if breakFlag:
                        break
                if breakFlag:
                    break
            if deploy == False:
                lines[point] = []
                lines[point].append(point)
            i += 1
        lps = []
        for key,line in lines.items():
            _lps = np.vstack(line)
            _lps = _lps[_lps[:,1].argsort()]
            lps.append(_lps.tolist())

        return lps

    def get_points(self):
        return self._nps.tolist()

