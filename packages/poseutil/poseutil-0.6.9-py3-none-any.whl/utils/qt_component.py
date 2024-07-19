from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QSlider, QPushButton
from PyQt6 import QtWidgets

def listViewSetup(list_widget, row, connect):
    for i in row:
        if ".DS_Store" in i:
            continue
        list_widget.addItem(i)
    list_widget.currentItemChanged.connect(connect)
    
def checkBoxSetup(checkBox, toolTip, toggle, connect):
    checkBox.setToolTip(toolTip)
    if toggle:
        checkBox.toggle()
    checkBox.stateChanged.connect(connect)


def labelSetup(label, move, title, fontSize = 15):
    label.move(move[0], move[1])
    label.setFont(QFont(title, fontSize))
    label.setText(title)
    label.show()

def sliderSetup(slider, label, move, range, step, defaultValue, connectData, val=1):
    slider.move(move[0], move[1])
    slider.setRange(range[0], range[1])
    slider.setSingleStep(step)
    slider.setValue(defaultValue)
    slider.valueChanged.connect(lambda: label.setText(str(round(slider.value() * val, 1))))
    slider.valueChanged.connect(connectData)
    slider.show()

def btnSetup(btn, toolTip, font, move, resize, connect):
    btn.setToolTip(toolTip)
    btn.setFont(font)
    btn.move(move[0], move[1])
    btn.resize(resize[0], resize[1])
    btn.clicked.connect(connect)

def btnSetting(btn, toolTip, font, clickedEvent):
    btn.setToolTip(toolTip)
    btn.setFont(font)
    btn.resize(btn.sizeHint())
    btn.clicked.connect(clickedEvent)

def tableSetup(table: QTableWidget, rows: int, cols: int, data=None, row_header=None, col_header=None):
    table.setRowCount(rows)
    table.setColumnCount(cols)
    if row_header is not None:
        table.setHorizontalHeaderLabels(row_header)
    if col_header is not None:
        table.setVerticalHeaderLabels(col_header)
    if data is None: 
        return
    for idx, val in enumerate(data):
        if type(val) is list:
            for idx_2, val_2 in enumerate(val):
                item = QTableWidgetItem(str(val_2))
                table.setItem(idx_2, idx, item)
        else:
            item = QTableWidgetItem(val)
            table.setItem(idx, 0, item)
    table.resizeColumnsToContents()
    table.resizeRowsToContents()

def comboBoxSetup(combo_box, item_list, connect):
    for item in item_list:
        combo_box.addItem(item)
    combo_box.activated.connect(connect)



class PlaySliderBar(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.pb_play = QPushButton('', self)
        self.pb_fast = QPushButton('', self)
        self.pb_slow = QPushButton('', self)
        self.pb_play_back = QPushButton('', self)
        self.pb_fast.setIcon(QIcon('imgs/fast.png'))
        self.pb_slow.setIcon(QIcon('imgs/slow.png'))
        self.pb_play.setIcon(QIcon('imgs/play.png'))
        self.pb_play_back.setIcon(QIcon('imgs/play_back.png'))

        self.pb_play_is_clicked = False
        self.cur_frame_num = 0
        self.load_finished_frame_num = 0
        self.defalut_interval = 20
        self.frame_interval = 1
        self.timer = QTimer()
        self.timer.setInterval(self.defalut_interval)
        self.timer.timeout.connect(self.playOnChangedFrameNum)
        self.setUpUI()

    def setTimer(self):
        self.timer = QTimer()
        self.timer.setInterval(self.defalut_interval)
        self.timer.timeout.connect(self.playOnChangedFrameNum)
    
    def setUpUI(self):
        self.main_widget = QtWidgets.QWidget(self)
        self.mainLayout = QtWidgets.QGridLayout(self.main_widget)
        easySliderSetup(self.slider, self.onChangedFrameNum)
        self.pb_play.clicked.connect(self.onClickedPlayBtn)
        self.pb_fast.clicked.connect(self.onClickedFastBtn)
        self.pb_slow.clicked.connect(self.onClickedSlowBtn)
        self.pb_play_back.clicked.connect(self.onClickedPlayBackBtn)

        self.mainLayout.addWidget(self.pb_slow, 0, 0, 1, 1)
        self.mainLayout.addWidget(self.pb_play, 0, 1, 1, 1)
        self.mainLayout.addWidget(self.pb_fast, 0, 2, 1, 1)
        self.mainLayout.addWidget(self.pb_play_back, 0, 3, 1, 1)
        self.mainLayout.addWidget(self.slider, 0, 4, 1, 1)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
    
    def onClickedPlayBackBtn(self):
        self.cur_frame_num -= 1

    def onClickedSlowBtn(self):
        self.defalut_interval += 20
        if self.defalut_interval >= 200:
            self.defalut_interval = 200
        self.timer.setInterval(self.defalut_interval)

    def onClickedFastBtn(self):
        self.defalut_interval -= 20
        if self.defalut_interval < 0:
            self.defalut_interval = 0
            self.timer.setInterval(1)
        else:
            self.timer.setInterval(self.defalut_interval)

    def onClickedPlayBtn(self):
        if self.pb_play_is_clicked:
            self.pb_play.setIcon(QIcon('imgs/play.png'))
            self.timer.stop()
        else:
            self.pb_play.setIcon(QIcon('imgs/pause.png'))
            self.timer.start()
        self.pb_play_is_clicked = not self.pb_play_is_clicked
    
    def onChangedFrameNum(self, value):
        if not self.isLimitFrameNum(value):
            self.cur_frame_num = value

    def playOnChangedFrameNum(self):
        if not self.isLimitFrameNum(self.cur_frame_num):
            self.cur_frame_num += self.frame_interval
            self.onChangedFrameNum(self.cur_frame_num)
            self.slider.setValue(self.cur_frame_num)
    
    def isLimitFrameNum(self, frame_num):
        if frame_num > self.load_finished_frame_num:
            self.cur_frame_num = self.load_finished_frame_num
            self.slider.setValue(self.cur_frame_num)
            return True
        else:
            return False