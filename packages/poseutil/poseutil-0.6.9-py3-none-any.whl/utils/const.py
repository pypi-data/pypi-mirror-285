import os

MATCOLORS = {
    'black':                '#000000',
    'antiquewhite':         '#FAEBD7',
    'aqua':                 '#00FFFF',
    'aquamarine':           '#7FFFD4',
    'azure':                '#F0FFFF',
    'beige':                '#F5F5DC',
    'bisque':               '#FFE4C4',
    'aliceblue':            '#F0F8FF',
    'blanchedalmond':       '#FFEBCD',
    'blue':                 '#0000FF',
    'blueviolet':           '#8A2BE2',
    'brown':                '#A52A2A',
    'burlywood':            '#DEB887',
    'cadetblue':            '#5F9EA0',
    'chartreuse':           '#7FFF00',
    'chocolate':            '#D2691E',
    'coral':                '#FF7F50',
    'cornflowerblue':       '#6495ED',
    'cornsilk':             '#FFF8DC',
    'crimson':              '#DC143C',
    'cyan':                 '#00FFFF',
    'darkblue':             '#00008B',
    'darkcyan':             '#008B8B',
    'darkgoldenrod':        '#B8860B',
    'darkgray':             '#A9A9A9',
    'darkgreen':            '#006400',
    'darkgrey':             '#A9A9A9',
    'darkkhaki':            '#BDB76B',
    'darkmagenta':          '#8B008B',
    'darkolivegreen':       '#556B2F',
    'darkorange':           '#FF8C00',
    'darkorchid':           '#9932CC',
    'darkred':              '#8B0000',
    'darksalmon':           '#E9967A',
    'darkseagreen':         '#8FBC8F',
    'darkslateblue':        '#483D8B',
    'darkslategray':        '#2F4F4F',
    'darkslategrey':        '#2F4F4F',
    'darkturquoise':        '#00CED1',}

MATCOLORNAMES = list(MATCOLORS.keys())
#------------------------------------------------------------------------
# Path 
DIR_PATH = os.getcwd()
KNN_PATH = DIR_PATH + '/data/knnData'
DANCE_DATA_PATH = DIR_PATH + '/data/danceData'

DANCE_VIDEO_PATH = DANCE_DATA_PATH + '/video'
DANCE_PICKLE_PATH = DANCE_DATA_PATH + '/pickle'
DANCE_IMG_PATH = DANCE_DATA_PATH + '/imgs'
DANCE_AUDIO_PATH = DANCE_DATA_PATH + '/audio'
DANCE_AUDIO_COMMON_PATH = DANCE_AUDIO_PATH + '/common/'


AUDIO_JSON_PATH = DIR_PATH + "/audio_info.json"
NAS_PATH = "/Volumes/Multimedia/댄스"
MLP_PATH_DATA = "/Volumes/FrameData/ml/mlp/data"
MLP_PATH = "/Volumes/FrameData/ml/mlp"
LSTM_PATH = "/Volumes/FrameData/ml/lstm"
COACHING_PATH = "/Volumes/FrameData/ml/coaching"
TRANSFORMER_PATH = "/Volumes/FrameData/ml/transformer"
LINUX_TRANSFORMER_PATH = "/home/hnh/FrameData/ml/transformer"
LINUX_MLP_PATH = "/home/hnh/FrameData/ml/mlp"
LINUX_LSTM_PATH = "/home/hnh/FrameData/ml/lstm"
VERSION_PATH = "/Volumes/FrameData/ml/version"


TAEKWONDO_PATH = "/Volumes/FrameData/TaeKwondo"
TAEKWONDO_LINUX_PATH = "/home/hnh/FrameData/TaeKwondo"

YOLO_PATH = "/Volumes/FrameData/yolo"

POSE_MEASURE_SAVE_PATH = DIR_PATH + "/poseutil/utils/poseMeasure.py"

KT_LOGIC_COACHING_PATH = DIR_PATH + "/ktLogicCoaching"
POSE_KT_PATH = DIR_PATH + "/poseKt"
GYMMATE_FONT_PATH = DIR_PATH + "/font"

NO_COUNTING_PATH = "/Volumes/FrameData/ml/no_counting_data"
LINUX_NO_COUNTING_PATH = "/home/hnh/FrameData/ml/no_counting_data"
APP_LIST = ["pose-test-app", "gymmate-app"]

#------------------------------------------------------------------------
# list view Setup
EMBEDDINGLIST = ["UPPER", "BODYNOSE", "LOWER","FULL", "HAND", "LOWERYANG", "TAEKWONDO", "HANDDETAIL"]
SIDECHECKLIST = ["SIDE", "FRONT"]
CONTENTLIST = ["Weight", "Golf", "Yang", "Beginner", "Test"]
ANGLELIST = [
    "NONE",  
    "getKneeHipAnkleAngle,xyz,avg", "getElbowWristShoulderAngle,xyz,avg",
    "getShoulderHipMinusPlane,xy,x,11", "getHipAnkleShoulderMinusAngle,xy,z,11",
    "getElbowWristShoulderMinusAngle,xy,z,11", "getHipShoulderKneeMinusAngle,xy,z,11",
    "getShoulderWristHipMinusAngle,xy,z,11", "getShoulderElbowHipMinusAngle,xy,z,11",
    "getKneeHipAnkleAngle,xy,avg", "getShoulderElbowHipAngle,xyz,avg",
    "getShoulderElbowHipAngle,xy,avg", "getKneeHipAnkleMinusAngle,xy,z,11",
    "getElbowWristShoulderAngle,xy,avg", "getKneeHipAnkleMinusAngle,xyz,z,25",
    "getElbowWristShoulderPlusAngle,xyz,y,11", "getHipShoulderKneePlusAngle,xy,y,15",
]
#------------------------------------------------------------------------
# Equation
COSINE = 0
LINEAR = 1
PARABOLA = 2
#------------------------------------------------------------------------
OFFSET = 20
CUTLINE = 75
#-------------------------------------------------------------------------
# Body Const
NOSE = 0
LEFT_EYE_INNER = 1
LEFT_EYE = 2
LEFT_EYE_OUTER = 3
RIGHT_EYE_INNER = 4
RIGHT_EYE = 5
RIGHT_EYE_OUTER = 6
LEFT_EAR = 7
RIGHT_EAR = 8
LEFT_MOUTH = 9
RIGHT_MOUTH = 10
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_ELBOW = 13
RIGHT_ELBOW = 14
LEFT_WRIST = 15
RIGHT_WRIST = 16
LEFT_PINKY = 17
RIGHT_PINKY = 18
LEFT_INDEX = 19
RIGHT_INDEX = 20
LEFT_THUMB = 21
RIGHT_THUMB = 22
LEFT_HIP = 23
RIGHT_HIP = 24
LEFT_KNEE = 25
RIGHT_KNEE = 26
LEFT_ANKLE = 27
RIGHT_ANKLE = 28
LEFT_HEEL = 29
RIGHT_HEEL = 30
LEFT_FOOT_INDEX = 31
RIGHT_FOOT_INDEX = 32
CENTER = 33

# Hand Const
LEFT_HAND_WRIST = 0
RIGHT_HAND_WRIST = 1
LEFT_HAND_THUMB_CMC = 2
RIGHT_HAND_THUMB_CMC = 3
LEFT_HAND_THUMB_MCP = 4
RIGHT_HAND_THUMB_MCP = 5
LEFT_HAND_THUMB_IP = 6
RIGHT_HAND_THUMB_IP = 7
LEFT_HAND_THUMB_TIP = 8
RIGHT_HAND_THUMB_TIP = 9
LEFT_HAND_INDEX_FINGER_MCP = 10
RIGHT_HAND_INDEX_FINGER_MCP = 11
LEFT_HAND_INDEX_FINGER_PIP = 12
RIGHT_HAND_INDEX_FINGER_PIP = 13 
LEFT_HAND_INDEX_FINGER_DIP = 14
RIGHT_HAND_INDEX_FINGER_DIP = 15
LEFT_HAND_INDEX_FINGER_TIP = 16
RIGHT_HAND_INDEX_FINGER_TIP = 17
LEFT_HAND_MIDDLE_FINGER_MCP = 18
RIGHT_HAND_MIDDLE_FINGER_MCP = 19
LEFT_HAND_MIDDLE_FINGER_PIP = 20
RIGHT_HAND_MIDDLE_FINGER_PIP = 21
LEFT_HAND_MIDDLE_FINGER_DIP = 22
RIGHT_HAND_MIDDLE_FINGER_DIP = 23
LEFT_HAND_MIDDLE_FINGER_TIP = 24
RIGHT_HAND_MIDDLE_FINGER_TIP = 25
LEFT_HAND_RING_FINGER_MCP = 26
RIGHT_HAND_RING_FINGER_MCP = 27
LEFT_HAND_RING_FINGER_PIP = 28
RIGHT_HAND_RING_FINGER_PIP = 29
LEFT_HAND_RING_FINGER_DIP = 30
RIGHT_HAND_RING_FINGER_DIP = 31
LEFT_HAND_RING_FINGER_TIP = 32
RIGHT_HAND_RING_FINGER_TIP = 33
LEFT_HAND_PINKY_MCP = 34
RIGHT_HAND_PINKY_MCP = 35
LEFT_HAND_PINKY_PIP = 36
RIGHT_HAND_PINKY_PIP = 37
LEFT_HAND_PINKY_DIP = 38
RIGHT_HAND_PINKY_DIP = 39
LEFT_HAND_PINKY_TIP = 40
RIGHT_HAND_PINKY_TIP = 41

ALL = 33
TORSO_MULTIPLIER = 2.5


# 몸만
def poseConnection_body(frame):
    connectionList = []
    # 왼쪽 어깨 ->
    connectionList.append([frame[LEFT_SHOULDER], frame[RIGHT_SHOULDER]])
    connectionList.append([frame[LEFT_SHOULDER], frame[LEFT_HIP]])
    connectionList.append([frame[LEFT_SHOULDER], frame[LEFT_ELBOW]])
    # 오른쪽 어깨 ->
    connectionList.append([frame[RIGHT_SHOULDER], frame[RIGHT_HIP]])
    connectionList.append([frame[RIGHT_SHOULDER], frame[RIGHT_ELBOW]])
    connectionList.append([frame[RIGHT_ELBOW], frame[RIGHT_WRIST]])

    connectionList.append([frame[LEFT_ELBOW], frame[LEFT_WRIST]])

    connectionList.append([frame[RIGHT_HIP], frame[LEFT_HIP]])

    connectionList.append([frame[LEFT_HIP], frame[LEFT_KNEE]])
    connectionList.append([frame[LEFT_KNEE], frame[LEFT_ANKLE]])

    connectionList.append([frame[RIGHT_HIP], frame[RIGHT_KNEE]])
    connectionList.append([frame[RIGHT_KNEE], frame[RIGHT_ANKLE]])

    return connectionList


# 손, 발 포함
def poseConnection(frame):
    connectionList = []
    # 왼쪽 어깨 ->
    connectionList.append([frame[LEFT_SHOULDER], frame[RIGHT_SHOULDER]])
    connectionList.append([frame[LEFT_SHOULDER], frame[LEFT_HIP]])
    connectionList.append([frame[LEFT_SHOULDER], frame[LEFT_ELBOW]])
    # 오른쪽 어깨 ->
    connectionList.append([frame[RIGHT_SHOULDER], frame[RIGHT_HIP]])
    connectionList.append([frame[RIGHT_SHOULDER], frame[RIGHT_ELBOW]])
    connectionList.append([frame[RIGHT_ELBOW], frame[RIGHT_WRIST]])

    connectionList.append([frame[LEFT_ELBOW], frame[LEFT_WRIST]])

    connectionList.append([frame[RIGHT_HIP], frame[LEFT_HIP]])

    connectionList.append([frame[LEFT_HIP], frame[LEFT_KNEE]])
    connectionList.append([frame[LEFT_KNEE], frame[LEFT_ANKLE]])

    connectionList.append([frame[RIGHT_HIP], frame[RIGHT_KNEE]])
    connectionList.append([frame[RIGHT_KNEE], frame[RIGHT_ANKLE]])

    connectionList.append([frame[LEFT_ANKLE], frame[LEFT_FOOT_INDEX]])
    connectionList.append([frame[LEFT_ANKLE], frame[LEFT_HEEL]])
    connectionList.append([frame[LEFT_HEEL], frame[LEFT_FOOT_INDEX]])

    connectionList.append([frame[RIGHT_ANKLE], frame[RIGHT_FOOT_INDEX]])
    connectionList.append([frame[RIGHT_ANKLE], frame[RIGHT_HEEL]])
    connectionList.append([frame[RIGHT_HEEL], frame[RIGHT_FOOT_INDEX]])

    # 손 ->
    connectionList.append([frame[LEFT_WRIST], frame[LEFT_THUMB]])
    connectionList.append([frame[RIGHT_WRIST], frame[RIGHT_THUMB]])

    connectionList.append([frame[LEFT_WRIST], frame[LEFT_INDEX]])
    connectionList.append([frame[LEFT_WRIST], frame[LEFT_PINKY]])
    connectionList.append([frame[LEFT_PINKY], frame[LEFT_INDEX]])

    connectionList.append([frame[RIGHT_WRIST], frame[RIGHT_INDEX]])
    connectionList.append([frame[RIGHT_WRIST], frame[RIGHT_PINKY]])
    connectionList.append([frame[RIGHT_PINKY], frame[RIGHT_INDEX]])

    return connectionList


ALL_BODY_STR_LIST = [
    "NOSE", "LEFT_EYE_INNER","LEFT_EYE", "LEFT_EYE_OUTER",
    "RIGHT_EYE_INNER", "RIGHT_EYE", "RIGHT_EYE_OUTER", "LEFT_EAR",
    "RIGHT_EAR", "LEFT_MOUTH", "RIGHT_MOUTH", "LEFT_SHOULDER", "RIGHT_SHOULDER",
    "LEFT_ELBOW", "RIGHT_ELBOW", "LEFT_WRIST", "RIGHT_WRIST", "LEFT_PINKY",
    "RIGHT_PINKY", "LEFT_INDEX", "RIGHT_INDEX", "LEFT_THUMB", "RIGHT_THUMB",
    "LEFT_HIP", "RIGHT_HIP", "LEFT_KNEE", "RIGHT_KNEE", "LEFT_ANKLE", "RIGHT_ANKLE",
    "LEFT_HEEL", "RIGHT_HEEL", "LEFT_FOOT_INDEX", "RIGHT_FOOT_INDEX"
]

ALLBODY_CONST_DICTIONARY = {
    "NOSE": NOSE, 
    "LEFT_EYE_INNER": LEFT_EYE_INNER,
    "LEFT_EYE": LEFT_EYE,
    "LEFT_EYE_OUTER": LEFT_EYE_OUTER,
    "RIGHT_EYE_INNER": RIGHT_EYE_INNER,
    "RIGHT_EYE": RIGHT_EYE,
    "RIGHT_EYE_OUTER": RIGHT_EYE_OUTER,
    "LEFT_EAR": LEFT_EAR,
    "RIGHT_EAR": RIGHT_EAR,
    "LEFT_MOUTH": LEFT_MOUTH,
    "RIGHT_MOUTH" : RIGHT_MOUTH ,
    "LEFT_SHOULDER" : LEFT_SHOULDER ,
    "RIGHT_SHOULDER" : RIGHT_SHOULDER ,
    "LEFT_ELBOW" : LEFT_ELBOW ,
    "RIGHT_ELBOW" : RIGHT_ELBOW ,
    "LEFT_WRIST" : LEFT_WRIST ,
    "RIGHT_WRIST" : RIGHT_WRIST ,
    "LEFT_PINKY" : LEFT_PINKY ,
    "RIGHT_PINKY" : RIGHT_PINKY ,
    "LEFT_INDEX" : LEFT_INDEX ,
    "RIGHT_INDEX" : RIGHT_INDEX ,
    "LEFT_THUMB" : LEFT_THUMB ,
    "RIGHT_THUMB" : RIGHT_THUMB ,
    "LEFT_HIP" : LEFT_HIP ,
    "RIGHT_HIP" : RIGHT_HIP ,
    "LEFT_KNEE" : LEFT_KNEE ,
    "RIGHT_KNEE" : RIGHT_KNEE ,
    "LEFT_ANKLE" : LEFT_ANKLE ,
    "RIGHT_ANKLE" : RIGHT_ANKLE ,
    "LEFT_HEEL" : LEFT_HEEL ,
    "RIGHT_HEEL" : RIGHT_HEEL ,
    "LEFT_FOOT_INDEX" : LEFT_FOOT_INDEX ,
    "RIGHT_FOOT_INDEX" : RIGHT_FOOT_INDEX
}

#------------------------------------------------------------------------
# Color Const RGB
RED = (200, 50, 50)
ORANGE = (255, 153, 50)
YELLOW = (255, 255, 50)
GREEN = (153, 255, 50)
SKY = (100, 255, 255)
DARK_SKY = (102, 178, 255)
PURPLE = (178, 102, 255)
BLUE = (51, 51, 255)
PINK = (255, 102, 255)
GRAY = (160, 160, 160)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLOR = [BLUE, BLACK, PINK, YELLOW, GREEN, SKY, DARK_SKY, ORANGE, RED, PURPLE, GRAY]

# Color Const BGR
BGR_RED = (50, 50, 200)
BGR_YELLOW = (50, 255, 255)
BGR_GREEN = (50, 255, 153)

#------------------------------------------------------------------------
RESOLUTION = (480, 640)

body_setting_id = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_KNEE, RIGHT_KNEE,
                   LEFT_ELBOW, LEFT_WRIST, LEFT_ANKLE,  
                   RIGHT_ELBOW, RIGHT_WRIST, RIGHT_ANKLE,
                   RIGHT_HIP, LEFT_HIP]

body_setting_id_right = [RIGHT_SHOULDER, RIGHT_KNEE,
                         RIGHT_ELBOW, RIGHT_WRIST, RIGHT_ANKLE,
                         RIGHT_HIP]

body_setting_id_left = [LEFT_SHOULDER, LEFT_KNEE,
                        LEFT_ELBOW, LEFT_WRIST, LEFT_ANKLE,
                        LEFT_HIP]

foot_setting_id = [LEFT_FOOT_INDEX, LEFT_HEEL, RIGHT_FOOT_INDEX, RIGHT_HEEL]
foot_setting_id_left = [LEFT_FOOT_INDEX, LEFT_HEEL]
foot_setting_id_right = [RIGHT_FOOT_INDEX, RIGHT_HEEL]
hand_setting_id_left = [LEFT_THUMB, LEFT_PINKY, LEFT_INDEX]
hand_setting_id_right = [RIGHT_THUMB, RIGHT_PINKY, RIGHT_INDEX]

VECTORS = [
    (LEFT_SHOULDER, RIGHT_SHOULDER),
    (LEFT_SHOULDER, LEFT_HIP),
    (RIGHT_SHOULDER, RIGHT_HIP),
    (LEFT_HIP, RIGHT_HIP),
    (LEFT_HIP, LEFT_KNEE),
    (RIGHT_HIP, RIGHT_KNEE),
    (LEFT_KNEE, LEFT_ANKLE),
    (RIGHT_KNEE, RIGHT_ANKLE),
    (LEFT_ANKLE, RIGHT_ANKLE),
]

DEFAULT_LOWER_BODY_SET = [
    (LEFT_KNEE, 'left_knee'), 
    (RIGHT_KNEE, 'right_knee'), 
    (LEFT_ANKLE, 'left_ankle'), 
    (RIGHT_ANKLE,'right_ankle'), 
    (LEFT_SHOULDER, 'left_shoulder'), 
    (RIGHT_SHOULDER, 'right_shoulder')
    ]

NAME = [
    "shoulder-shoulder",
    "leftShoulder-leftHip",
    "rightShoulder-rightHip",
    "leftHip-rightHip",
    "leftHip-leftKnee",
    "rightHip-rightKnee",
    "leftKnee-leftAnkle",
    "rightKnee-rightAnkle",
    "leftAnkle-rightAnkle"
]

UPPER = "UPPER"
UPPERLEFT = "UPPERLEFT"
UPPERRIGHT = "UPPERRIGHT"
LOWER = "LOWER"
LOWERLEFT = "LOWERLEFT"
LOWERRIGHT = "LOWERRIGHT"
FULL = "FULL"
FULLLEFT = "FULLLEFT"
FULLRIGHT = "FULLRIGHT"
HAND = "HAND"
HANDLEFT = "HANDLEFT"
HANDRIGHT = "HANDRIGHT"
BODYNOSE = "BODYNOSE"
BODYNOSELEFT = "BODYNOSELEFT"
BODYNOSERIGHT = "BODYNOSERIGHT"
LOWERYANG = "LOWERYANG"
LOWERYANGLEFT = "LOWERYANGLEFT"
LOWERYANGRIGHT = "LOWERYANGRIGHT"
HANDDETAIL = "HANDDETAIL"
YOLOLOWER = "YOLOLOWER"


TAEKWONDO_EMBEDDING = [
    LEFT_SHOULDER, RIGHT_SHOULDER,
    LEFT_HIP, RIGHT_HIP,
    LEFT_KNEE, RIGHT_KNEE,
    LEFT_ANKLE, RIGHT_ANKLE,
    LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX,
    LEFT_HEEL, RIGHT_HEEL
]

SYNC_TARGET_LOWER = [
    [LEFT_SHOULDER, RIGHT_SHOULDER],
    [LEFT_SHOULDER, LEFT_HIP],
    [RIGHT_SHOULDER, RIGHT_HIP],
    [LEFT_HIP, RIGHT_HIP],
    [LEFT_HIP, LEFT_KNEE],
    [RIGHT_HIP, RIGHT_KNEE],
    [LEFT_KNEE, LEFT_ANKLE],
    [RIGHT_KNEE, RIGHT_ANKLE],
]

DANCE_TARGET_BODY = [
    [NOSE, LEFT_SHOULDER],
    [NOSE, RIGHT_SHOULDER],
    [LEFT_SHOULDER, LEFT_ELBOW],
    [LEFT_ELBOW, LEFT_WRIST],
    [LEFT_SHOULDER, LEFT_WRIST],
    [RIGHT_SHOULDER, RIGHT_ELBOW],
    [RIGHT_ELBOW, RIGHT_WRIST],
    [RIGHT_SHOULDER, RIGHT_WRIST],
    [LEFT_HIP, LEFT_KNEE],
    [LEFT_HIP, LEFT_ANKLE],
    [LEFT_HIP, RIGHT_HIP],
    [RIGHT_HIP, RIGHT_KNEE],
    [RIGHT_HIP, RIGHT_ANKLE],
    [LEFT_KNEE, LEFT_ANKLE],
    [LEFT_KNEE, RIGHT_ANKLE],
    [LEFT_KNEE, RIGHT_KNEE],
    [RIGHT_KNEE, LEFT_ANKLE],
    [RIGHT_KNEE, RIGHT_ANKLE],
    [LEFT_ANKLE, RIGHT_ANKLE],
]

DANCE_TARGET_BODY_STR = [
    "[NOSE, LEFT_SHOULDER]",
    "[NOSE, RIGHT_SHOULDER]",
    "[LEFT_SHOULDER, LEFT_ELBOW]",
    "[LEFT_ELBOW, LEFT_WRIST]",
    "[LEFT_SHOULDER, LEFT_WRIST]",
    "[RIGHT_SHOULDER, RIGHT_ELBOW]",
    "[RIGHT_ELBOW, RIGHT_WRIST]",
    "[RIGHT_SHOULDER, RIGHT_WRIST]",
    "[LEFT_HIP, LEFT_KNEE]",
    "[LEFT_HIP, LEFT_ANKLE]",
    '[LEFT_HIP, RIGHT_HIP]',
    "[RIGHT_HIP, RIGHT_KNEE]",
    "[RIGHT_HIP, RIGHT_ANKLE]",
    "[LEFT_KNEE, LEFT_ANKLE]",
    "[LEFT_KNEE, RIGHT_ANKLE]",
    "[LEFT_KNEE, RIGHT_KNEE]",
    "[RIGHT_KNEE, LEFT_ANKLE]",
    "[RIGHT_KNEE, RIGHT_ANKLE]",
    "[LEFT_ANKLE, RIGHT_ANKLE]",
    "TOTAL HAND"
]

DANCE_TARGET_HAND = [
    # [HAND_WRIST, HAND_THUMB_TIP],
    # [HAND_WRIST, HAND_INDEX_FINGER_MCP],
    # [HAND_WRIST, HAND_PINKY_MCP],
    # [HAND_INDEX_FINGER_MCP, HAND_INDEX_FINGER_TIP],
    # [HAND_MIDDLE_FINGER_MCP, HAND_MIDDLE_FINGER_TIP],
    # [HAND_RING_FINGER_MCP, HAND_RING_FINGER_TIP],
    # [HAND_PINKY_MCP, HAND_PINKY_TIP]
]

DANCE_TARGET_HIP = [
    [LEFT_HIP, RIGHT_HIP]
]

DANCE_TARGET_ARM = [
    [LEFT_SHOULDER, LEFT_ELBOW],
    [LEFT_SHOULDER, LEFT_WRIST],
    [LEFT_SHOULDER, RIGHT_SHOULDER],
    [RIGHT_SHOULDER, RIGHT_ELBOW],
    [RIGHT_SHOULDER, RIGHT_WRIST],
    [LEFT_ELBOW, LEFT_WRIST],
    [LEFT_ELBOW, RIGHT_ELBOW],
    [RIGHT_ELBOW, RIGHT_WRIST],
]

DANCE_TARGET_BODY_RESULT = [
    "LEFT_SHOULDER, LEFT_ELBOW",
    "LEFT_ELBOW, LEFT_WRIST",
    "LEFT_SHOULDER, LEFT_WRIST",
    "RIGHT_SHOULDER, RIGHT_ELBOW",
    "RIGHT_ELBOW, RIGHT_WRIST",
    "RIGHT_SHOULDER, RIGHT_WRIST",
    "LEFT_HIP, LEFT_KNEE",
    "LEFT_KNEE, LEFT_ANKLE",
    "LEFT_HIP, LEFT_ANKLE",
    "RIGHT_HIP, RIGHT_KNEE",
    "RIGHT_KNEE, RIGHT_ANKLE",
    "RIGHT_HIP, RIGHT_ANKLE"
]

DANCE_TARGET_UPPER_BODY = [
    [LEFT_SHOULDER, RIGHT_SHOULDER],
    [LEFT_SHOULDER, LEFT_HIP],
    [LEFT_SHOULDER, RIGHT_HIP],
    [RIGHT_SHOULDER, LEFT_SHOULDER]
]

DANCE_TARGET_UPPER_BODY_RESULT = [
    "LEFT_SHOULDER, RIGHT_SHOULDER",
    "LEFT_SHOULDER, LEFT_HIP",
    "LEFT_SHOULDER, RIGHT_HIP",
    "RIGHT_SHOULDER, LEFT_SHOULDER"
]

DANCE_BODY = [LEFT_ANKLE,LEFT_KNEE,LEFT_HIP,LEFT_SHOULDER, LEFT_ELBOW,LEFT_WRIST,NOSE,
              RIGHT_ANKLE,RIGHT_KNEE,RIGHT_HIP,RIGHT_SHOULDER,RIGHT_ELBOW,RIGHT_WRIST]
DANCE_BODY_RESULT = ["LEFT_ANKLE","LEFT_KNEE","LEFT_HIP","LEFT_SHOULDER", "LEFT_ELBOW",'LEFT_WRIST','NOSE',
              "RIGHT_ANKLE","RIGHT_KNEE","RIGHT_HIP","RIGHT_SHOULDER","RIGHT_ELBOW","RIGHT_WRIST"]

BODY_SET = [LEFT_SHOULDER, RIGHT_SHOULDER,LEFT_HIP, RIGHT_HIP]

BODY_DOT = [
    0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32
]
FACE_DOT = [
    LEFT_EAR, LEFT_EYE, NOSE, RIGHT_EYE, RIGHT_EAR
]
LEFT_LINK = [
    [11, 13], [13, 15], [11, 23], [23, 25], [25, 27], [27, 29], [27, 31], [29, 31]
]
RIGHT_LINK = [
    [12, 14], [14, 16], [12, 24], [24, 26], [26, 28], [28, 30], [28, 32], [30, 32]
]
CENTER_LINK = [
    [11, 12], [23, 24]
]
FACE_LINK = [
    [LEFT_EAR, LEFT_EYE], [LEFT_EYE, NOSE], [NOSE, RIGHT_EYE], [RIGHT_EYE, RIGHT_EAR]
]
HAND_DOT = [i for i in range(41)]
LEFT_HAND_LINK = [ 
    [0, 2], [2, 4], [4, 6], [6, 8], 
    [0, 10], [10, 12], [12, 14], [14, 16],
    [18, 20], [20, 22], [22, 24],
    [26, 28], [28, 30], [30, 32],
    [0, 34], [34, 36], [36, 38], [38, 40],
    [10, 18], [18, 26], [26, 34]
]
RIGHT_HAND_LINK = [
    [1, 3], [3, 5], [5, 7], [7, 9],
    [1, 11], [11, 13], [13, 15], [15, 17],
    [19, 21], [21, 23], [23, 25],
    [27, 29], [29, 31], [31, 33],
    [1, 35], [35, 37], [37, 39], [39, 41],
    [11, 19], [19, 27], [27, 35]
]



KEY_INFO_CAPTURE_LIVE_HEADER = [""]
KEY_INFO_CAPTURE_LIVE_HEADER = [""]
STATIC_HEADER = ["Width", "Height", "Origin", "Compare"]
DYNAMIC_HEADER = ["Total Score", "Frame Num", "Time"]
AUDIO_JSON_HEADER = ["name", "startPos", "interval"]

X = 'x'
Y = 'y'
Z = 'z'
XY = 'xy'
YZ = 'yz'
XZ = 'xz'
XYZ = 'xyz'

LEFT = 'left'
RIGHT = 'right'
AVG = 'avg'

COORD_LIST = [X, Y, Z]
EQUATION_LIST = ["MINUS", "PLUS"]
STANDARD_JOINT_LIST = [
    "LEFT_SHOULDER", "LEFT_HIP", "LEFT_KNEE", "LEFT_ELBOW", "LEFT_WRIST", "LEFT_ANKLE"
]
STANDARD_JOINT_MAP = {
    LEFT_SHOULDER: "LEFT_SHOULDER",
    LEFT_HIP: "LEFT_HIP",
    LEFT_KNEE: "LEFT_KNEE",
    LEFT_ELBOW: "LEFT_ELBOW",
    LEFT_WRIST: "LEFT_WRIST",
    LEFT_ANKLE: "LEFT_ANKLE"
}

CONTENTS = ["Weight", "Yang", "Beginner"]

TAEKWONDO_LSTM_MAP = {
    "STANDBY" : 0 ,
    "SIDE_KICK" : 1 , 
    "FRONT_KICK" : 2 ,
    "DOWNWARD_KICK" : 3 ,
    "ROUND_KICK" : 4 ,
    "BACK_KICK" : 5 ,
    "BACK_ROUND_KICK" : 6 ,
    "TURN_ROUND_KICK" : 7 ,
}

TAEKWONDO_LSTM_MAP_REVERSE = {
    0 : "STANDBY" ,
    1 : "SIDE_KICK", 
    2 : "FRONT_KICK"  ,
    3 : "DOWNWARD_KICK" ,
    4 : "ROUND_KICK" ,
    5 : "BACK_KICK" ,
    6 : "BACK_ROUND_KICK" ,
    7 : "TURN_ROUND_KICK" ,
}
TAEKWONDO_LABEL = [
            "STANDBY",
            "SIDE_KICK", 
            "FRONT_KICK",
            "DOWNWARD_KICK",
            "ROUND_KICK",
            "BACK_KICK",
            "BACK_ROUND_KICK",
            "TURN_ROUND_KICK",
            "NONE"
            ]

NEW_TAEKWONDO_LABWL_MAP = {
    "STANDBY" : 0 ,
    "LEFT_MIDDLE_SIDE_KICK" : 1 ,
    "LEFT_UPPER_SIDE_KICK" : 2 ,
    "RIGHT_MIDDLE_SIDE_KICK" : 3 ,
    "RIGHT_UPPER_SIDE_KICK" : 4 ,
    "LEFT_MIDDLE_FRONT_KICK" : 5 ,
    "LEFT_UPPER_FRONT_KICK" : 6 ,
    "RIGHT_MIDDLE_FRONT_KICK" : 7 ,
    "RIGHT_UPPER_FRONT_KICK" : 8 ,
    "LEFT_DOWNWARD_KICK" : 9 ,
    "RIGHT_DOWNWARD_KICK" : 10,
    "LEFT_MIDDLE_ROUND_KICK" : 11,
    "LEFT_UPPER_ROUND_KICK" : 12,
    "RIGHT_MIDDLE_ROUND_KICK" : 13,
    "RIGHT_UPPER_ROUND_KICK" : 14,
    "LEFT_MIDDLE_BACK_KICK" : 15,
    "LEFT_UPPER_BACK_KICK" : 16,
    "RIGHT_MIDDLE_BACK_KICK" : 17,
    "RIGHT_UPPER_BACK_KICK" : 18,
    "LEFT_MIDDLE_BACK_ROUND_KICK" : 19,
    "LEFT_UPPER_BACK_ROUND_KICK" : 20,
    "RIGHT_MIDDLE_BACK_ROUND_KICK" : 21,
    "RIGHT_UPPER_BACK_ROUND_KICK" : 22,
    "LEFT_MIDDLE_TURN_ROUND_KICK" : 23,
    "LEFT_UPPER_TURN_ROUND_KICK" : 24,
    "RIGHT_MIDDLE_TURN_ROUND_KICK" : 25,
    "RIGHT_UPPER_TURN_ROUND_KICK" : 26,
    "LEFT_PUNCH" : 27,
    "RIGHT_PUNCH" : 28,
}

NEW_TAEKWONDO_LABEL = [
    "STANDBY",
    "LEFT_MIDDLE_SIDE_KICK", 
    "LEFT_UPPER_SIDE_KICK", 
    "RIGHT_MIDDLE_SIDE_KICK", 
    "RIGHT_UPPER_SIDE_KICK", 
    "LEFT_MIDDLE_FRONT_KICK",
    "LEFT_UPPER_FRONT_KICK",
    "RIGHT_MIDDLE_FRONT_KICK",
    "RIGHT_UPPER_FRONT_KICK",
    "LEFT_DOWNWARD_KICK",
     "RIGHT_DOWNWARD_KICK",
     "LEFT_MIDDLE_ROUND_KICK",
     "LEFT_UPPER_ROUND_KICK",
     "RIGHT_MIDDLE_ROUND_KICK",
     "RIGHT_UPPER_ROUND_KICK",
     "LEFT_MIDDLE_BACK_KICK",
     "LEFT_UPPER_BACK_KICK",
     "RIGHT_MIDDLE_BACK_KICK",
     "RIGHT_UPPER_BACK_KICK",
     "LEFT_MIDDLE_BACK_ROUND_KICK",
     "LEFT_UPPER_BACK_ROUND_KICK",
     "RIGHT_MIDDLE_BACK_ROUND_KICK",
     "RIGHT_UPPER_BACK_ROUND_KICK",
     "LEFT_MIDDLE_TURN_ROUND_KICK",
     "LEFT_UPPER_TURN_ROUND_KICK",
     "RIGHT_MIDDLE_TURN_ROUND_KICK",
     "RIGHT_UPPER_TURN_ROUND_KICK",
     "LEFT_PUNCH",
     "RIGHT_PUNCH",
]

NEW_TAEKWONDO_LABEL_MAP_REVERSE = {
    0 : "STANDBY",
    1 : "LEFT_MIDDLE_SIDE_KICK", 
    2 : "LEFT_UPPER_SIDE_KICK", 
    3 : "RIGHT_MIDDLE_SIDE_KICK", 
    4 : "RIGHT_UPPER_SIDE_KICK", 
    5 : "LEFT_MIDDLE_FRONT_KICK",
    6 : "LEFT_UPPER_FRONT_KICK",
    7 : "RIGHT_MIDDLE_FRONT_KICK",
    8 : "RIGHT_UPPER_FRONT_KICK",
    9 : "LEFT_DOWNWARD_KICK",
    10 : "RIGHT_DOWNWARD_KICK",
    11 : "LEFT_MIDDLE_ROUND_KICK",
    12 : "LEFT_UPPER_ROUND_KICK",
    13 : "RIGHT_MIDDLE_ROUND_KICK",
    14 : "RIGHT_UPPER_ROUND_KICK",
    15 : "LEFT_MIDDLE_BACK_KICK",
    16 : "LEFT_UPPER_BACK_KICK",
    17 : "RIGHT_MIDDLE_BACK_KICK",
    18 : "RIGHT_UPPER_BACK_KICK",
    19 : "LEFT_MIDDLE_BACK_ROUND_KICK",
    20 : "LEFT_UPPER_BACK_ROUND_KICK",
    21 : "RIGHT_MIDDLE_BACK_ROUND_KICK",
    22 : "RIGHT_UPPER_BACK_ROUND_KICK",
    23 : "LEFT_MIDDLE_TURN_ROUND_KICK",
    24 : "LEFT_UPPER_TURN_ROUND_KICK",
    25 : "RIGHT_MIDDLE_TURN_ROUND_KICK",
    26 : "RIGHT_UPPER_TURN_ROUND_KICK",
    27 : "LEFT_PUNCH",
    28 : "RIGHT_PUNCH",
}

NEW_TAEKWONDO_LABEL_MAP_REVERSE_KR = {
    0 : "준비",
    1 : "왼발 중단 옆차기", 
    2 : "왼발 상단 옆차기", 
    3 : "오른발 중단 옆차기", 
    4 : "오른발 상단 옆차기", 
    5 : "왼발 중단 앞차기",
    6 : "왼발 상단 앞차기",
    7 : "오른발 중단 앞차기",
    8 : "오른발 상단 앞차기",
    9 : "왼발 내려차기",
    10 : "오른발 내려차기",
    11 : "왼발 중단 돌려차기",
    12 : "왼발 상단 돌려차기",
    13 : "오른발 중단 돌려차기",
    14 : "오른발 상단 돌려차기",
    15 : "왼발 중단 뒤차기",
    16 : "왼발 상단 뒤차기",
    17 : "오른발 중단 뒤차기",
    18 : "오른발 상단 뒤차기",
    19 : "왼발 중단 뒤후리기",
    20 : "왼발 상단 뒤후리기",
    21 : "오른발 중단 뒤후리기",
    22 : "오른발 상단 뒤후리기",
    23 : "왼발 중단 돌개차기",
    24 : "왼발 상단 돌개차기",
    25 : "오른발 중단 돌개차기",
    26 : "오른발 상단 돌개차기",
    27 : "왼손 정권",
    28 : "오른손 정권",
}

NEW_TAEKWONDO_LABEL_MAP_KR = {
    "준비" : 0,
    "왼발 중단 옆차기" : 1,
    "왼발 상단 옆차기" : 2,
    "오른발 중단 옆차기" : 3,
    "오른발 상단 옆차기" : 4,
    "왼발 중단 앞차기" : 5,
    "왼발 상단 앞차기" : 6,
    "오른발 중단 앞차기" : 7,
    "오른발 상단 앞차기" : 8,
    "왼발 내려차기" : 9,
    "오른발 내려차기" : 10,
    "왼발 중단 돌려차기" : 11,
    "왼발 상단 돌려차기" : 12,
    "오른발 중단 돌려차기" : 13,
    "오른발 상단 돌려차기" : 14,
    "왼발 중단 뒤차기" : 15,
    "왼발 상단 뒤차기" : 16,
    "오른발 중단 뒤차기" : 17,
    "오른발 상단 뒤차기" : 18,
    "왼발 중단 뒤후리기" : 19,
    "왼발 상단 뒤후리기" : 20,
    "오른발 중단 뒤후리기" : 21,
    "오른발 상단 뒤후리기" : 22,
    "왼발 중단 돌개차기" : 23,
    "왼발 상단 돌개차기" : 24,
    "오른발 중단 돌개차기" : 25,
    "오른발 상단 돌개차기" : 26,
    "왼손 정권" : 27,
    "오른손 정권" : 28,
}

MODEL_TRANSFORMER = 'transformer'
MODEL_LSTM = 'lstm'

MP2YOLO = {
    NOSE: 0,
    LEFT_EYE: 1,
    RIGHT_EYE: 2,
    LEFT_EAR: 3,
    RIGHT_EAR: 4,
    LEFT_SHOULDER: 5,
    RIGHT_SHOULDER: 6,
    LEFT_ELBOW: 7,
    RIGHT_ELBOW: 8,
    LEFT_WRIST: 9,
    RIGHT_WRIST: 10,
    LEFT_HIP: 11,
    RIGHT_HIP: 12,
    LEFT_KNEE: 13,
    RIGHT_KNEE: 14,
    LEFT_ANKLE: 15,
    RIGHT_ANKLE: 16,    
}

TAEKWONDO_LSTM_MAP_REVERSE_KR = {
    0 : "준비" ,
    1 : "옆차기", 
    2 : "앞차기"  ,
    3 : "내려차기" ,
    4 : "돌려차기" ,
    5 : "뒤차기" ,
    6 : "뒤후리기" ,
    7 : "돌개차기" ,
}

LABELING_BODY = {
    "nose": NOSE,
    "left_shoulder": LEFT_SHOULDER,
    "right_shoulder": RIGHT_SHOULDER,
    "left_elbow": LEFT_ELBOW,
    "right_elbow": RIGHT_ELBOW,
    "left_wrist": LEFT_WRIST,
    "right_wrist": RIGHT_WRIST,
    "left_hip": LEFT_HIP,
    "right_hip": RIGHT_HIP,
    "left_knee": LEFT_KNEE,
    "right_knee": RIGHT_KNEE,
    "left_ankle": LEFT_ANKLE,
    "right_ankle": RIGHT_ANKLE,
}

landmarkNumberList = {
            "Nose": 0,
            "Shoulder": 11,
            "Elbow": 13,
            "Wrist": 15,
            "Pinky": 17,
            "HandIndex": 19,
            "Thumb": 21,
            "Hip": 23,
            "Knee": 25,
            "Ankle": 27,
            "Heel": 29,
            "FootIndex": 31
        }