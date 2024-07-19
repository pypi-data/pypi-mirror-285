from PyQt6.QtWidgets import QMainWindow, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QWidget, QPushButton, QSlider, QHBoxLayout, QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6. QtGui import QGuiApplication, QIcon, QColor, QBrush
from PyQt6 import QtCore
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl
from enum import Enum
import threading


class AppMode(Enum):
    normal = 1
    debug = 2

class BaseQMainWindow(QMainWindow):
    def __init__(self, width, height, mode):
        super().__init__()
        self.mode = mode
        if mode == AppMode.normal:
            self.monitor = QGuiApplication.screens()[0].geometry()
        elif mode == AppMode.debug:
            if len(QGuiApplication.screens()) > 2:
                self.monitor = QGuiApplication.screens()[2].geometry()
            elif len(QGuiApplication.screens()) > 1:
                self.monitor = QGuiApplication.screens()[1].geometry()
            else :
                self.monitor = QGuiApplication.screens()[0].geometry()
        self.setGeometry(self.monitor.left(), self.monitor.top(), width, height)
        self.keyInfo = []
    
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key.Key_Escape:
            self.close()
        elif e.key() == QtCore.Qt.Key.Key_H:
            print("==================================")
            for idx, info in enumerate(self.keyInfo):
                print(f"{idx}. {info}")
            print("==================================")

class BaseQDialog(QDialog):
    def __init__(self, width, height, mode):
        super().__init__()
        self.mode = mode
        if mode == AppMode.normal:
            self.monitor = QGuiApplication.screens()[0].geometry()
        elif mode == AppMode.debug:
            if len(QGuiApplication.screens()) > 2:
                self.monitor = QGuiApplication.screens()[2].geometry()
            elif len(QGuiApplication.screens()) > 1:
                self.monitor = QGuiApplication.screens()[1].geometry()
            else :
                self.monitor = QGuiApplication.screens()[0].geometry()
        self.setGeometry(self.monitor.left(), self.monitor.top(), width, height)
    
    # def createDialog(self, message_text):
    #     QBtn = QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
    #     self.buttonBox = QDialogButtonBox(QBtn)
    #     self.buttonBox.accepted.connect(self.accept)
    #     self.buttonBox.rejected.connect(self.reject)

    #     self.mainLayout = QVBoxLayout()
    #     message = QLabel(message_text)
    #     self.mainLayout.addWidget(message)
    #     self.mainLayout.addWidget(self.buttonBox)
    #     self.setLayout(self.mainLayout)

class StoppableThread(threading.Thread):
    
    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class VideoPlayer(BaseQMainWindow):
    def __init__(self, videoPath):
        super().__init__(800, 600, AppMode.normal)
        self.setWindowTitle('Video Player')
        
        self.mediaPlayer = QMediaPlayer(self)
        self.audioOutput = QAudioOutput(self)
        self.mediaPlayer.setAudioOutput(self.audioOutput)

        videoWidget = QVideoWidget(self)
        self.mediaPlayer.setVideoOutput(videoWidget)

        self.playButton = QPushButton('')
        self.playButton.setIcon(QIcon('./imgs/play.png'))
        self.playButton.clicked.connect(self.togglePlayback)

        self.stopButton = QPushButton('')
        self.stopButton.setIcon(QIcon('./imgs/GymateLogo.png'))
        self.stopButton.clicked.connect(self.stopVideo)

        self.forwardButton = QPushButton('')
        self.forwardButton.setIcon(QIcon('./imgs/fast.png'))
        self.forwardButton.clicked.connect(self.forwardVideo)

        self.backwardButton = QPushButton('')
        self.backwardButton.setIcon(QIcon('./imgs/slow.png'))
        self.backwardButton.clicked.connect(self.backwardVideo)

        self.positionSlider = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.stopButton)
        controlLayout.addWidget(self.backwardButton)
        controlLayout.addWidget(self.forwardButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.videoPath = videoPath
        self.playVideo()

    def togglePlayback(self):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.mediaPlayer.pause()
            self.playButton.setIcon(QIcon('./imgs/play'))
        else:
            self.mediaPlayer.play()
            self.playButton.setIcon(QIcon('./imgs/pause'))

    def stopVideo(self):
        self.mediaPlayer.stop()
        self.playButton.setIcon(QIcon('./imgs/play'))

    def forwardVideo(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() + 10000)  # 10 seconds forward

    def backwardVideo(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() - 10000)  # 10 seconds backward

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def playVideo(self):
        url = QUrl.fromLocalFile(self.videoPath)
        self.mediaPlayer.setSource(url)
        self.mediaPlayer.play()

class ColorProgressBar(QProgressBar):
    def __init__(self, color, *args, **kwargs):
        super(ColorProgressBar, self).__init__(*args, **kwargs)
        self.color = color
        self.setTextVisible(True)

    def setValue(self, label, value):
        super().setValue(value)
        self.setFormat(f'{label}  {value}%')
        self.setStyleSheet(f"""
            QProgressBar {{
                text-align: center;
                color: white;
            }}
            QProgressBar::chunk {{
                background-color: {self.color.name()};
            }}
        """)

class InfoChangeDialog(BaseQDialog):
    def __init__(self, width, height, mode, oldData: dict, newData: dict):
        super().__init__(width, height, AppMode.debug)
        self.setFixedSize(width, height)
        self.setWindowTitle("Information Change!")
        self.mainLayout = QVBoxLayout()
        header = QLabel("The information has been updated. Do you want to save the changes?")
        self.mainLayout.addWidget(header)
        
        self.table = QTableWidget(len(oldData), 3)
        self.table.setHorizontalHeaderLabels(["Key", "Old Value", "New Value"])
        
        for row, key in enumerate(oldData.keys()):
            old_value = oldData[key]
            new_value = newData.get(key, old_value)
            
            self.table.setItem(row, 0, QTableWidgetItem(key))
            
            old_value_str = self.convert_to_str(old_value)
            new_value_str = self.convert_to_str(new_value)
            
            self.table.setItem(row, 1, QTableWidgetItem(old_value_str))
            
            new_value_item = QTableWidgetItem(new_value_str)
            if old_value != new_value:
                print(old_value, new_value)
                new_value_item.setBackground(QColor("lightyellow"))
                new_value_item.setForeground(QBrush(QColor("black")))

            self.table.setItem(row, 2, new_value_item)
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        #TODO: Files 의 개수가 많아지면 버튼 + 추가 Dialog 로 변경예정
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.mainLayout.addWidget(self.table)
        self.adjustSize()
        self.buttonBox = QHBoxLayout()
        self.yesButton = QPushButton("Yes")
        self.noButton = QPushButton("No")
        
        self.yesButton.clicked.connect(self.accept)
        self.noButton.clicked.connect(self.reject)
        
        self.buttonBox.addWidget(self.yesButton)
        self.buttonBox.addWidget(self.noButton)
        
        self.mainLayout.addLayout(self.buttonBox)
        self.setLayout(self.mainLayout)
    
    def convert_to_str(self, value):
        if isinstance(value, (dict, list)):
            return str(value)
        elif isinstance(value, (int, float)):
            return str(value)
        return value

def showNoticeDialog(noticeMessage):
    msgBox = QMessageBox()
    msgBox.setWindowTitle("Notice!")
    msgBox.setText(noticeMessage)
    msgBox.setIcon(QMessageBox.Icon.Information)
    msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
    msgBox.exec()

def showWarningDialog(warningMessage):
    msgBox = QMessageBox()
    msgBox.setWindowTitle("Warning!")
    msgBox.setText(warningMessage)
    msgBox.setIcon(QMessageBox.Icon.Warning)
    msgBox.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    result = msgBox.exec()
    return result

def showCriticalDialog(CriticalMessage):
    msgBox = QMessageBox()
    msgBox.setWindowTitle("Critical!")
    msgBox.setText(CriticalMessage)
    msgBox.setIcon(QMessageBox.Icon.Critical)
    msgBox.setStandardButtons(QMessageBox.StandardButton.Close)
    result = msgBox.exec()
    return result