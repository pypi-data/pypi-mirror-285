import mediapipe as mp
import cv2
import sys
from os import path
sys.path.append(path.dirname( path.dirname( path.abspath(__file__) ) ))


class Video:
    def __init__(self, videoPath) -> None:
        self.cap = cv2.VideoCapture(videoPath)
        self.mp_drawing, self.mp_drawing_styles, self.pose, self.mpPose = self.mp_init()
        # self.vc = version.VersionCaster(0)

    def mp_init(self):
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mpPose = mp.solutions.pose
        pose = mpPose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=True)
        return mp_drawing, mp_drawing_styles, pose, mpPose

    def read_frame(self):
        rawData = []
        allData = []
        leftData = []
        rightData = []
        ret, img = self.cap.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        height, width, t = img.shape
        if height > 2000 or width > 2000:
            thickness = 12
            circle_radius = 12
        elif height > 1500 or width > 1500:
            thickness = 8
            circle_radius = 8
        else :
            thickness = 4
            circle_radius = 4
        results = self.pose.process(imgRGB)
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(img, results.pose_landmarks, self.mpPose.POSE_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(224,224,224), thickness=thickness, circle_radius=circle_radius), 
            self.mp_drawing.DrawingSpec(color=(245,10,10), thickness=thickness, circle_radius=circle_radius))
            # landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                rawData.append(round((lm.x * w), 4))
                rawData.append(round((lm.y * h), 4))
                rawData.append(round((lm.z * h), 4))

            tempData = rawData.copy()

            if results.pose_landmarks.landmark[11].z < results.pose_landmarks.landmark[12].z:
                leftData.append(tempData)
            else:
                rightData.append(tempData)
            allData.append(tempData)
        rawData.clear()
        convert_data = self.vc.get_version_casting_convert_pose_data(allData, 0.3)
        while (height > 300 or width > 300):
            height /= 2
            width /= 2
        dst = cv2.resize(img, dsize=(int(width), int(height)))
        dst = cv2.cvtColor(dst, cv2.COLOR_RGB2BGR)
        return dst, convert_data

class Img:
    def __init__(self, img_dir_path) -> None:
        self.img_dir_path = img_dir_path

    def readImg(self, img_num):
        img = cv2.imread(f"{self.img_dir_path}/{img_num:05d}.jpg")
        dst = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return dst