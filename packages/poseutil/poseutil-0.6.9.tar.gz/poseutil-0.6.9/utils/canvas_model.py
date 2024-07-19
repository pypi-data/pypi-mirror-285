from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
from PyQt6 import QtCore, QtWidgets
from utils.const import poseConnection, poseConnection_body
from utils.common_component import load_pickle_path
from utils.pose_util import convert_pose
from utils.poseMeasure import PoseMeasure
import time
import math

matplotlib.use('Qt5Agg')

def draw_skeleton(frame, axes, header=1010, scale=1000):
    axes.scatter(frame[0].x*scale,
                    frame[0].z*scale,
                    frame[0].y*scale)
    if header == 0:
        connectionList = poseConnection(frame)
    else: 
        connectionList = poseConnection_body(frame)
    for line in connectionList:
        axes.plot([line[0].x*scale, line[1].x*scale],
                    [line[0].z*scale, line[1].z*scale],
                    [line[0].y*scale, line[1].y*scale],
                    alpha=0.6, marker='o',
                    markersize=3)

def draw_skeleton2(frame, axes, scale):
    axes.scatter(scale, scale, scale)
    connectionList = poseConnection_body(frame)
    for line in connectionList:
        axes.plot([line[0].x, line[1].x],
                    [line[0].z, line[1].z],
                    [line[0].y, line[1].y],
                    alpha=0.6, marker='o',
                    markersize=3)
        
def getScaleList(scale):
    scaleList = []
    scaleList.append((0, -scale / 2, 0))
    scaleList.append((0, -scale / 2, scale))
    scaleList.append((0, scale / 2, 0))
    scaleList.append((0, scale / 2, scale))
    scaleList.append((scale, -scale / 2, 0))
    scaleList.append((scale, -scale / 2, scale))
    scaleList.append((scale, scale / 2, 0))
    scaleList.append((scale, scale / 2, scale))
    return scaleList

def updateLabelInfo(axes, text, move):
        axes.text2D(
            move[0], move[1], text, transform=axes.transAxes, style='italic',
            bbox={'facecolor': 'blue', 'edgecolor': 'black', 'alpha': 0.6, 'pad': 5},
            fontsize=10)


class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=10, height=10, dpi=100):
        # 초기 뷰 셋팅
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.init_axes()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Policy.Expanding,
                                   QtWidgets.QSizePolicy.Policy.Expanding)
        FigureCanvas.updateGeometry(self)
    
    def init_axes(self, scale=640):
        self.axes = self.fig.add_subplot(111, projection='3d')
        self.scale = scale
        self.angle = 30
        self.axes.set_xlabel('$X$', fontsize=10, rotation=0)
        self.axes.set_ylabel('$Z$', fontsize=10, rotation=0)
        self.axes.set_zlabel('$Y$', fontsize=10, rotation=0)

        self.axes.set_xlim(0, self.scale)
        self.axes.set_ylim(-self.scale / 2, self.scale / 2)
        self.axes.set_zlim(0, self.scale)
        self.axes.set_box_aspect((1, 1, 1))
        self.axes.view_init(180, self.angle)
    
    def compute_initial_figure(self):
        pass

class MatPlotCanvasView(Canvas):
    frameNum = 0
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)

    def update_figure(self, frameNum):
        self.axes.cla()
        frame = self.frameDataList[frameNum]
        draw_skeleton2(frame, self.axes, self.scale)
        scaleList = getScaleList(self.scale)
        for scalePoint in scaleList:
            self.axes.scatter(scalePoint[0], scalePoint[1], scalePoint[2])

        self.poseMeasure = PoseMeasure(frame)
        try:
            angle = getattr(self.poseMeasure, self.func)(*self.inputs)
            updateLabelInfo(self.axes, f"{self.angleSelect}", (0.8, 1))
            updateLabelInfo(self.axes, f"angle : {angle}", (0.8, 0.9))
        except:
            return

        self.draw()
        self.pbData.setValue(((frameNum)/len(self.frameDataList)) * 100)
        if len(self.frameDataList) < (frameNum+1):
            self.close()

    def setData(self, pickle, angleSelect, pbData):
        pickle_data = load_pickle_path(pickle)
        self.pose_width = pickle_data["width"]
        self.pose_height = pickle_data["height"]
        self.frameDataList = convert_pose(pickle_data["pose"], self.pose_width, self.pose_height)
        self.angleSelect = angleSelect
        self.func, *self.inputs = angleSelect.split(",")
        self.scale = max(self.pose_width, self.pose_height)
        self.angleSelect = angleSelect
        self.pbData = pbData
        self.header = 1010

class MatPlotCanvasAutoView(Canvas):
    
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.frameNum = 0

    def update_figure(self):
        self.axes.cla()
        frame = self.frameDataList[self.frameNum]
        draw_skeleton2(frame, self.axes, self.scale)
        scaleList = getScaleList(self.scale)
        for scalePoint in scaleList:
            self.axes.scatter(scalePoint[0], scalePoint[1], scalePoint[2])

        self.draw()
        self.pbData.setValue(((self.frameNum)/len(self.frameDataList)) * 100)
        if len(self.frameDataList) < (self.frameNum+1):
            self.close()
        else :
            self.frameNum += 1

    def setData(self, pickle, angleSelect, scale, pbData):
        pickle_data = load_pickle_path(pickle)
        self.frameDataList = pickle_data["pose"]
        self.angleSelect = angleSelect
        self.func, *self.inputs = angleSelect.split(",")
        self.scale = scale
        self.angleSelect = angleSelect
        self.pbData = pbData
        self.header = 1010
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_figure)
        self.timer.start()


class MatPlotCanvasLabel(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.frameNum = 0
        self.viewSpeed = 1

    def init_figure(self):
        self.axes.cla()
        frame = self.frameDataList[self.frameNum]
        draw_skeleton(frame, self.axes)
        scaleList = getScaleList(self.scale)
        for scalePoint in scaleList:
            self.axes.scatter(scalePoint[0], scalePoint[1], scalePoint[2])

        updateLabelInfo(self.axes, f"UP   : {0}", (0.8, 1))
        updateLabelInfo(self.axes, f"MIDDLE : {0}", (0.8, 0.9))
        updateLabelInfo(self.axes, f"DOWN : {0}", (0.8, 0.8))
        updateLabelInfo(self.axes, f"Exercise : ", (0, 1))
        updateLabelInfo(self.axes, f"SideViserblity : ", (0, 0.9))
        self.draw()

    def update_figure(self, exerciseName, upCnt, middleCnt, downCnt, sideViserblity, infoIsShow = True):
        self.frameNum += self.viewSpeed
        self.axes.cla()
        frame = self.frameDataList[self.frameNum]
        draw_skeleton(frame, self.axes)
        scaleList = getScaleList(self.scale)
        for scalePoint in scaleList:
            self.axes.scatter(scalePoint[0], scalePoint[1], scalePoint[2])
        if infoIsShow:
            updateLabelInfo(self.axes, f"UP   : {upCnt}", (0.8, 1))
            updateLabelInfo(self.axes, f"MIDDLE : {middleCnt}", (0.8, 0.9))
            updateLabelInfo(self.axes, f"DOWN : {downCnt}", (0.8, 0.8))
            updateLabelInfo(self.axes, f"Exercise : {exerciseName}", (0, 1))
            updateLabelInfo(self.axes, f"SideViserblity : {sideViserblity}", (0, 0.9))

        self.draw()
        
        if len(self.frameDataList) < self.frameNum + self.viewSpeed:
            self.close()

    def setData(self, frameData, scale, viewSpeed):
        self.frameDataList = frameData
        self.scale = scale
        self.viewSpeed = viewSpeed
        self.init_figure()

    def captureFrame(self):
        lineData = []
        frame = self.frameDataList[self.frameNum]
        for body in frame:
            lineData += [round(body.x, 2), round(body.y, 2), round(body.z, 2)]
        return lineData
    
    def jumpFrame(self, frame_num):
        self.frameNum += frame_num


class MatPlotCanvasLabelLive(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)

    def update_figure(self,frame_data, exerciseName, upCnt, downCnt, sideViserblity, infoIsShow = True):
        self.axes.cla()
        draw_skeleton(frame_data[0], self.axes)
        scaleList = getScaleList(self.scale)
        for scalePoint in scaleList:
            self.axes.scatter(scalePoint[0], scalePoint[1], scalePoint[2])
        if infoIsShow:
            updateLabelInfo(self.axes, f"UP   : {upCnt}", (0.8, 1))
            updateLabelInfo(self.axes, f"DOWN : {downCnt}", (0.8, 0.9))
            updateLabelInfo(self.axes, f"Exercise : {exerciseName}", (0, 1))
            updateLabelInfo(self.axes, f"SideViserblity : {sideViserblity}", (0, 0.9))

        self.draw()




class CanvasImg(FigureCanvas):
    def __init__(self, parent=None, width=10, height=10, dpi=100):
        # 초기 뷰 셋팅
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.init_axes()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Policy.Expanding,
                                   QtWidgets.QSizePolicy.Policy.Expanding)
        FigureCanvas.updateGeometry(self)
    
    def init_axes(self):
        self.axes = self.fig.add_subplot(111)
        self.scale = 1024

    
    def compute_initial_figure(self):
        pass


class MatPlotCanvasImg(CanvasImg):
    def __init__(self, *args, **kwargs):
        CanvasImg.__init__(self, *args, **kwargs)

    def update_figure(self, img):
        self.axes.cla()
        self.axes.imshow(img)
        self.draw()

    def setText(self, text, move):
        self.axes.text2D(
            move[0], move[1], text, transform=self.axes.transAxes, style='italic',
            bbox={'facecolor': 'blue', 'edgecolor': 'black', 'alpha': 0.6, 'pad': 5},
            fontsize=10)

class MatPlotCanvasDance(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.frameNum = 0

    def init_figure(self):
        self.axes.cla()
        frame = self.frameDataList[0]
        draw_skeleton(frame, self.axes)
        scaleList = getScaleList(self.scale)
        for scalePoint in scaleList:
            self.axes.scatter(scalePoint[0], scalePoint[1], scalePoint[2])

        updateLabelInfo(self.axes, f"Time   : {0}", (0.1, 1))
        updateLabelInfo(self.axes, f"FrameNum : {0}", (0.1, 0.9))
        self.draw()

    def update_figure(self, frame_num):
        if len(self.frameDataList) < frame_num or frame_num < 0:
            return
        self.axes.cla()
        frame = self.frameDataList[frame_num]
        draw_skeleton(frame, self.axes)
        scaleList = getScaleList(self.scale)
        for scalePoint in scaleList:
            self.axes.scatter(scalePoint[0], scalePoint[1], scalePoint[2])
        updateLabelInfo(self.axes, f"Frame   : {frame_num}", (0.1, 1))
        updateLabelInfo(self.axes, f"Time : {self.info_data[frame_num]}", (0.1, 0.9))

        self.draw()

    def getTimeInfo(self, frame_num):
        return self.info_data[frame_num]

    def getFrameData(self, frame_num):
        return self.frameDataList[frame_num]

    def setData(self, frameData, scale, info_data):
        self.frameDataList = frameData
        self.info_data = info_data
        self.scale = scale
        # self.init_figure()

    def captureFrame(self, frame_num):
        lineData = []
        frame = self.frameDataList[frame_num]
        for body in frame:
            lineData += [round(body.x, 2), round(body.y, 2), round(body.z, 2)]
        return lineData
    

class MatPlotCanvasDanceLive(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)

    def init_figure(self):
        self.axes.cla()
        scaleList = getScaleList(self.scale)
        for scalePoint in scaleList:
            self.axes.scatter(scalePoint[0]/2, scalePoint[1]/2, scalePoint[2]/2)
        self.draw()

    def update_figure(self, frame):
        self.axes.cla()
        draw_skeleton(frame, self.axes)
        scaleList = getScaleList(self.scale)
        for scalePoint in scaleList:
            self.axes.scatter(scalePoint[0]/2, scalePoint[1]/2, scalePoint[2]/2)
        self.draw()

    def setData(self, scale):
        self.scale = scale
        self.init_figure()

    
class MatPlotCanvasTaekwondoView(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.labels = None

    def update_figure(self):
        self.axes.cla()
        if self.labels != None and len(self.labels) > (self.frameNum + 1):
            label = self.labels[self.frameNum]
            updateLabelInfo(self.axes, f"label   : {label}", (0.1, 1))
        if len(self.poses) > (self.frameNum+1):
            frame = self.poses[self.frameNum]
            draw_skeleton2(frame, self.axes, self.scale)
            scaleList = getScaleList(self.scale)
            for scalePoint in scaleList:
                self.axes.scatter(scalePoint[0], scalePoint[1], scalePoint[2])
            self.draw()
            self.frameNum += 1
        else: 
            self.timer.stop()     

    def set_data(self, poses, scale, labels=None):
        self.frameNum = 0
        self.scale = scale
        self.poses = poses
        self.labels = labels
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_figure)
        self.timer.start()

class MatPlotCanvasSkeletonView(Canvas):
    
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)

    def set_scale(self, scale):
        Canvas.init_axes(self, scale)
    
    def update_figure(self):
        self.axes.cla()
        if len(self.poses) < (self.frameNum+1):
            self.frameNum = len(self.poses) - 1

        frame = self.poses[self.frameNum]
        draw_skeleton2(frame, self.axes, self.scale)
        scaleList = getScaleList(self.scale)
        for scalePoint in scaleList:
            self.axes.scatter(scalePoint[0], scalePoint[1], scalePoint[2])
        self.draw()

    def chagneFrameNum(self, frameNum):
        self.frameNum = frameNum
    
    def set_data(self, poses):
        self.frameNum = 0
        self.poses = poses


class MatPlotCanvasEmbeddingData(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.markers = ['^', '^', '^', '^', 'o', 'o', 'o', 'o', 'x', 'x', 'x', 'x']
        self.colors = ['r', 'b', 'g', 'y', 'r', 'b', 'g', 'y', 'r', 'b', 'g', 'y']
        self.axes.set_xlabel('$X$', fontsize=10, rotation=0)
        self.axes.set_ylabel('$Z$', fontsize=10, rotation=0)
        self.axes.set_zlabel('$Y$', fontsize=10, rotation=0)
        self.scale = 30
        self.axes.set_xlim(-self.scale, self.scale)
        self.axes.set_ylim(-self.scale, self.scale)
        self.axes.set_zlim(-self.scale, self.scale)
        self.axes.set_box_aspect((1, 1, 1))
        self.axes.view_init(180, 0)
        self.col_means = {}

    def update_figure(self, df, labels):
        max_val = df.max(numeric_only=True).max() * 1.5
        self.axes.set_xlim(-max_val, max_val)
        self.axes.set_ylim(-max_val, max_val)
        self.axes.set_zlim(-max_val, max_val)
        for i, label in enumerate(labels):
            x_axis_data = df[df['target']==i]['lda_x']
            y_axis_data = df[df['target']==i]['lda_z']
            z_axis_data = df[df['target']==i]['lda_y']

            print(f"==============  {label}  ==============")
            print(f" 표준편차   : {x_axis_data.std(), z_axis_data.std(), y_axis_data.std()}")
            print(f" 표준편차 합 : {x_axis_data.std() + z_axis_data.std() + y_axis_data.std()}")
            self.col_means[label] = (x_axis_data.mean(), z_axis_data.mean(), y_axis_data.mean())
            self.axes.scatter(x_axis_data, z_axis_data, y_axis_data, marker=self.markers[i], color=self.colors[i], label=label, alpha = 0.5)

        for col_mean_key, col_mean_value in zip(self.col_means.keys(), self.col_means.values()):
            for label in labels:
                if col_mean_key == label:
                    continue
                else :
                    col_dist = math.dist(col_mean_value, self.col_means[label])
                    print(f"{col_mean_key}  --  {label} :{col_dist}")
        self.axes.legend()
        self.draw()
    
    def clear_figure(self):
        self.axes.cla()
        self.axes.set_xlabel('$X$', fontsize=10, rotation=0)
        self.axes.set_ylabel('$Z$', fontsize=10, rotation=0)
        self.axes.set_zlabel('$Y$', fontsize=10, rotation=0)
        self.scale = 30
        self.axes.set_xlim(-self.scale, self.scale)
        self.axes.set_ylim(-self.scale, self.scale)
        self.axes.set_zlim(-self.scale, self.scale)
        self.axes.set_box_aspect((1, 1, 1))
        self.axes.view_init(180, 0)