import os
import shutil
import time
import glob
import gzip, pickle
import numpy as np
import cv2
import re, json, yaml
import tensorflow as tf
import struct, itertools
import matplotlib.pyplot as plt
from utils.const import *
from utils.poseMeasure import PoseMeasure
from utils.normarlize import getPoseEmbeddingList, getPoseSize
from utils.pose_util import Coordinate
from tqdm import tqdm
from distutils.dep_util import newer
import os
from PyQt6 import uic
from collections import defaultdict

def get_dance_audio_list():
    audio_list_path = DANCE_AUDIO_PATH
    sorted_list = sorted(os.listdir(audio_list_path))
    if 'common' in sorted_list:
        sorted_list.remove('common')
    return sorted(sorted_list)

def get_dance_audio(audio, speed=1.0):
    selected_auido = f"{audio}_{speed}.mp3"
    return f"{DANCE_AUDIO_PATH}/{audio}/{selected_auido}"

def dump_json_data(json_path, data):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent="\t")

def dumps_json_data(json_path, data):
    with open(json_path, 'w', encoding='UTF-8-sig') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent = 4, sort_keys = True))

def get_json_data_all(json_path) -> dict:
    with open(json_path, 'r') as f:
        data =  json.load(f)
    return data

def get_json_data(json_path, audio_name):
    with open(json_path, 'r') as f:
        data =  json.load(f)
    return data[audio_name]

def write_json_data(json_path, data):
    with open(json_path, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_audio_name(audio_path):
    return audio_path.split("/")[-1].split(".")[0].split("_")[0]

def add_infomation_circle(img, text):
    mask = img.copy()
    cv2.circle(mask, (150,150), 150, (0, 0, 0), -1)
    cv2.putText(mask, text, (60, 220), cv2.FONT_HERSHEY_SIMPLEX, 8, (255, 255, 255), 5)
    return cv2.addWeighted(img, 0.3, mask, 0.7, 0)

def get_speed(audio_path):
    p = re.compile("[0-9].[0-9]*")
    audio_speed = float(p.findall(audio_path)[0]) if p.findall(audio_path) else 1
    return audio_speed

def current_milli_time():
    return round(time.time() * 1000)

def sort_list_dir(path):
    dir_list = os.listdir(path)
    dir_list.sort()
    return dir_list

def time_jpg_priority(x):
    return int(x.split('/')[-1].split('.')[0])

def create_directory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            shutil.rmtree(directory)
            os.makedirs(directory)
    except OSError:
        print("Error: Failed to create the directory.")

def get_sync_time(origin_time, video_time):
    x = 0
    while origin_time != (video_time + x):
        if origin_time > video_time:
            x += 1
        else:
            x -= 1
    print(x)
    return x

def load_pickle_dance(name):
    with gzip.open(f"{DANCE_PICKLE_PATH}/{name}.pickle") as f:
        pickle_data = pickle.load(f)
    return pickle_data

def load_pickle_path(path):
    with gzip.open(path) as f:
        pickle_data = pickle.load(f)
    return pickle_data

def load_img_list(path):
    img_list = sorted(glob.glob(f"{path}/*.jpg"), key=lambda x: int(x.split("/")[-1].replace(".jpg", "")))
    return img_list

def search_timetable(origin_timetable, compare_timetable, origin_num, compare_num):
    sync_num = 0
    origin_time = origin_timetable[origin_num]
    compare_time = compare_timetable[compare_num]
    while origin_time >= compare_time:
        sync_num += 1
        compare_time = compare_timetable[compare_num + sync_num]
    prev_compare_time = compare_timetable[compare_num + sync_num -1]
    if abs(origin_time - compare_time) < abs(origin_time - prev_compare_time):
        return int(compare_num + sync_num), compare_time
    else :
        return int(compare_num + sync_num - 1), prev_compare_time
    
def rewind_search_timetable(origin_timetable, compare_timetable, origin_num, compare_num):
    sync_num = 0
    origin_time = origin_timetable[origin_num]
    compare_time = compare_timetable[compare_num]
    while origin_time <= compare_time:
        sync_num -= 1
        compare_time = compare_timetable[compare_num + sync_num]
    prev_compare_time = compare_timetable[compare_num + sync_num + 1]
    if abs(origin_time - compare_time) < abs(origin_time - prev_compare_time):
        return int(compare_num + sync_num), compare_time
    else :
        return int(compare_num + sync_num + 1), prev_compare_time
    
def load_tflite_model(path):
    model = tf.lite.Interpreter(model_path=path)
    model.allocate_tensors()
    input_index = model.get_input_details()[0]['index']
    output_index = model.get_output_details()[0]['index']
    return model, input_index, output_index

def inference_tflite_model(model, input, input_index, output_index):
    model.set_tensor(input_index, input)
    model.invoke()
    return model.get_tensor(output_index)

def get_input_for_mlp(pose, embedding, side, standardJoint=None, standardCoord=None, standardEquation=None):
    poseMeasure = PoseMeasure(pose)
    if side:
        if poseMeasure.getCoord(pose[eval(standardJoint)], standardCoord) < poseMeasure.getCoord(pose[eval(standardJoint)+1], standardCoord):
            if standardEquation == "MINUS":
                inputs = getPoseEmbeddingList(pose, embedding.upper() + "LEFT")
            else:
                inputs = getPoseEmbeddingList(pose, embedding.upper() + "RIGHT")
        else:
            if standardEquation == "MINUS":
                inputs = getPoseEmbeddingList(pose, embedding.upper() + "RIGHT")
            else:
                inputs = getPoseEmbeddingList(pose, embedding.upper() + "LEFT")
    else:
        inputs = getPoseEmbeddingList(pose, embedding.upper())
    return np.expand_dims(np.array(inputs).astype(np.float32), axis=0)

def get_emaSmoothing_for_mlp(history, window_size, factor, ratio):
    results = history[-window_size:]
    emaSmoothing = defaultdict(int)
    for i in results[::-1]:
        emaSmoothing[i] = round(emaSmoothing[i] + factor, 2)
        factor *= ratio
    return sorted(emaSmoothing.items(), key=lambda x: x[1], reverse=True)[0][0], emaSmoothing

def process(file):
    unpack_data = []
    with open(file, "rb") as f:
        data = f.read()
    for cell in range(0, int(len(data)), 4):
        unpack_data.append(struct.unpack('i', data[cell: cell+4])[0])
    return unpack_data

def plot_confusion_matrix(cm, model_path, target_names=None, cmap=None, normalize=True, labels=True, title='Confusion matrix'):
    accuracy = np.trace(cm) / float(np.sum(cm))
    misclass = 1 - accuracy
    if cmap is None:
        cmap = plt.get_cmap('Blues')
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    plt.figure(figsize=(8, 8))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    thresh = cm.max() / 1.5 if normalize else cm.max() / 2
    if target_names is not None:
        tick_marks = np.arange(len(target_names))
        plt.xticks(tick_marks, target_names)
        plt.yticks(tick_marks, target_names)
    if labels:
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            if normalize:
                plt.text(j, i, "{:0.4f}".format(cm[i, j]),
                         horizontalalignment="center",
                         color="white" if cm[i, j] > thresh else "black")
            else:
                plt.text(j, i, "{:,}".format(cm[i, j]),
                         horizontalalignment="center",
                         color="white" if cm[i, j] > thresh else "black")
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label\naccuracy={:0.4f}; misclass={:0.4f}'.format(accuracy, misclass))
    plt.savefig(f"{model_path}/confusion_matrix.png")

def flip(frames, width=640):
    flip_data = []
    for frame in frames:
        temp = [Coordinate(0, 0, 0) for i in range(len(frame))]
        for idx, coord in enumerate(frame):
            if idx == 0:
                temp[idx] = Coordinate(width-frame[idx].x, frame[idx].y, frame[idx].z)
            elif idx <= 10:
                temp[idx] = coord
            else:
                flip_coord = Coordinate(width-frame[idx].x, frame[idx].y, frame[idx].z)
                if idx % 2 == 1:
                    temp[idx+1] = flip_coord
                else:
                    temp[idx-1] = flip_coord
        flip_data.append(temp)
    return flip_data

def inferece_lstm(model_path, json_path, embeddings):
    json_data = get_json_data_all(json_path)
    windowSize, interval = json_data["windowSize"], json_data["interval"]
    model, input_index, output_index = load_tflite_model(model_path)

    labels = [[] for _ in range(len(embeddings))]
    idx = 0
    while idx + ((windowSize - 1) * interval) < len(embeddings):
        lstm_input = [embeddings[idx + (i * interval)] for i in range(windowSize)]
        input = np.expand_dims(np.array(lstm_input).astype(np.float32), axis=0)
        result = inference_tflite_model(model, input, input_index, output_index)[0][0]
        predict = "EXERCISING" if result < 0.5 else "RESTING"
        
        for i in range(windowSize):
            labels[idx+(i*interval)].append(predict)
        idx += 1
    
    labels = ["EXERCISING" if i.count("EXERCISING") >= i.count("RESTING") else "RESTING" for i in labels]
    return labels

def get_embedding_for_tflite_with_label(poses, embedding, labels, side, joint, coord, equation):
    embedding_data = []
    pose_data = []
    label_data = []
    for label, pose in zip(labels, poses):
        try:
            if side:
                poseMeasure = PoseMeasure(pose)
                if poseMeasure.getCoord(pose[joint], coord) < poseMeasure.getCoord(pose[joint+1], coord):
                    if equation == "MINUS":
                        embedding_data.append(getPoseEmbeddingList(pose, embedding.upper() + "LEFT"))
                    else:
                        embedding_data.append(getPoseEmbeddingList(pose, embedding.upper() + "RIGHT"))
                else:
                    if equation == "MINUS":
                        embedding_data.append(getPoseEmbeddingList(pose, embedding.upper() + "RIGHT"))
                    else:
                        embedding_data.append(getPoseEmbeddingList(pose, embedding.upper() + "LEFT"))
            else:
                embedding_data.append(getPoseEmbeddingList(pose, embedding.upper()))
            pose_data.append(pose)
            label_data.append(label)
        except Exception as e:
            print(e)
            pass
    return pose_data, embedding_data, label_data

def get_embedding_for_tflite_with_label_taekwondo(poses, embeddingType, dimension="3d"):
    embedding_data = []
    pose_data = []
    valid_idx = []
    if embeddingType != "TAEKWONDO":
        for idx, pose in enumerate(poses):
            try:
                embedding_data.append(getPoseEmbeddingList(pose, embeddingType.upper(), dimension))
                pose_data.append(pose)
                valid_idx.append(idx)
            except Exception as e:
                print(e)
                pass
    else:
        for idx, pose in enumerate(poses[:-4]):
            try:
                poseSize = 100 / getPoseSize(pose)
                post_pose = poses[idx+3]
                vector = []
                for body, (i, j) in enumerate(zip(post_pose, pose)):
                    if body in TAEKWONDO_EMBEDDING:
                        vector.append((i.x-j.x) * poseSize)
                        vector.append((i.y-j.y) * poseSize)
                        vector.append((i.z-j.z) * poseSize)
                embedding_data.append(vector)
                pose_data.append(pose)
                valid_idx.append(idx)
            except Exception as e:
                pass
    return pose_data, embedding_data, valid_idx

def getEmbeddingMLP(poses, embedding, selectorSide):
    embeddings = []
    directionSide = selectorSide.split(', ')[-1]
    selectorSide = selectorSide.replace(f"{directionSide}", "")
    isMinus = directionSide == "MINUS"
    print(embedding, selectorSide, isMinus)
    for key, value in landmarkNumberList.items():
        if key in selectorSide:
            selectorSide = selectorSide.replace(key, f"{value}")
    for pose in poses:
        if selectorSide != "":
            poseMeasure = PoseMeasure(pose)
            left = poseMeasure.getData(selectorSide + "LEFT")
            right = poseMeasure.getData(selectorSide + "RIGHT")
            if isMinus:
                if left < right:
                    embeddings.append(getPoseEmbeddingList(pose, embedding.upper() + "LEFT"))
                else:
                    embeddings.append(getPoseEmbeddingList(pose, embedding.upper() + "RIGHT"))
            else:
                if left > right:
                    embeddings.append(getPoseEmbeddingList(pose, embedding.upper() + "LEFT"))
                else:
                    embeddings.append(getPoseEmbeddingList(pose, embedding.upper() + "RIGHT"))
        else:
            embeddings.append(getPoseEmbeddingList(pose, embedding.upper()))
    return embeddings

def getInputForMlp(pose, embedding, side, selectorSide):
    inputs = []
    print(embedding, side, selectorSide)
    for key, value in landmarkNumberList.items():
        if key in selectorSide:
            selectorSide = selectorSide.replace(key, f"{value}")
    if side == "TRUE":
        poseMeasure = PoseMeasure(pose)
        directionSide = selectorSide.split(', ')[-1]
        selectorSide = selectorSide.replace(f"{directionSide}", "")
        isMinus = directionSide == "MINUS"
        left = poseMeasure.getData(selectorSide + "LEFT")
        right = poseMeasure.getData(selectorSide + "RIGHT")
        if isMinus:
            if left < right:
                inputs = getPoseEmbeddingList(pose, embedding.upper() + "LEFT")
            else:
                inputs = getPoseEmbeddingList(pose, embedding.upper() + "RIGHT")
        else:
            if left > right:
                inputs = getPoseEmbeddingList(pose, embedding.upper() + "LEFT")
            else:
                inputs = getPoseEmbeddingList(pose, embedding.upper() + "RIGHT")
    else:
        inputs = getPoseEmbeddingList(pose, embedding.upper())
    return np.expand_dims(np.array(inputs).astype(np.float32), axis=0)

def get_embedding_for_tflite(poses, embedding, side, joint, coord, equation):
    embedding_data = []
    pose_data = []
    for pose in poses:
        try:
            if side:
                poseMeasure = PoseMeasure(pose)
                if poseMeasure.getCoord(pose[joint], coord) < poseMeasure.getCoord(pose[joint+1], coord):
                    if equation == "MINUS":
                        embedding_data.append(getPoseEmbeddingList(pose, embedding.upper() + "LEFT"))
                    else:
                        embedding_data.append(getPoseEmbeddingList(pose, embedding.upper() + "RIGHT"))
                else:
                    if equation == "MINUS":
                        embedding_data.append(getPoseEmbeddingList(pose, embedding.upper() + "RIGHT"))
                    else:
                        embedding_data.append(getPoseEmbeddingList(pose, embedding.upper() + "LEFT"))
            else:
                embedding_data.append(getPoseEmbeddingList(pose, embedding.upper()))
            pose_data.append(pose)
        except Exception as e:
            print(e)
            pass
    return pose_data, embedding_data

def get_embedding_for_tflite_taekwondo(poses, embedding, labels):
    embedding_data = []
    if embedding != "TAEKWONDO":
        for label, pose in zip(labels, poses):
            try:
                embedding_data.append(getPoseEmbeddingList(pose, embedding.upper()))
            except Exception as e:
                pass
    else:
        for idx, pose in enumerate(poses[:-4]):
            try:
                poseSize = 100 / getPoseSize(pose)
                post_pose = poses[idx+3]
                vector = []
                for body, (i, j) in enumerate(zip(post_pose, pose)):
                    if body in TAEKWONDO_EMBEDDING:
                        vector.append((i.x-j.x) * poseSize)
                        vector.append((i.y-j.y) * poseSize)
                        vector.append((i.z-j.z) * poseSize)
                embedding_data.append(vector)
            except Exception as e:
                print(e)
                pass
    return embedding_data

def mlp_auto_labeling(poseMeasure, angleSelect, upMiddle, downMiddle):
    func, *inputs = angleSelect.split(",")
    angle = getattr(poseMeasure, func)(*inputs)
    if downMiddle < upMiddle:
        if angle < downMiddle:
            label = "DOWN"
        elif angle >= downMiddle and angle <= upMiddle:
            label = "MIDDLE"
        else:
            label = "UP"
    else:
        if angle > downMiddle:
            label = "DOWN"
        elif angle <= downMiddle and angle >= upMiddle:
            label = "MIDDLE"
        else:
            label = "UP"
    return label

def get_mlp_label(content, shortTerm, files):
    for file in tqdm(files):
        type = file.split("/")[-2]
        pickle_data = load_pickle_path(file)

        data_path = sorted(glob.glob(f"{MLP_PATH}/model/{content}/{shortTerm}/*/*.json"))[-1]        
        json_data = get_json_data_all(data_path)
        
        poses = pickle_data["pose"]
        embedding, side, angleSelect = json_data["embedding"], json_data["side"], json_data["angleSelect"]
        upMiddle, downMiddle = json_data["upMiddle"], json_data["downMiddle"]
        joint, coord, equation = "", "", ""
        if side:
            joint, coord, equation = eval(json_data["standardJoint"]), json_data["standardCoord"], json_data["standardEquation"]
        poses, _ = get_embedding_for_tflite(poses, embedding, side, joint, coord, equation)
        mlp_label = []
        for pose in poses:
            poseMeasure = PoseMeasure(pose)
            mlp_label.append(mlp_auto_labeling(poseMeasure, angleSelect, upMiddle, downMiddle))

        lstm_label = [None for i in range(len(poses))]
        new_pickle_data = {
        "pose": poses,
            "mlp_label": mlp_label,
            "lstm_label": lstm_label,
            "width": pickle_data["width"],
            "height": pickle_data["height"]
        }
        pickle_name = file.split("/")[-1]
        os.makedirs(f"{MLP_PATH}/label/{content}/{shortTerm}/{type}", exist_ok=True)
        with gzip.open(f"{MLP_PATH}/label/{content}/{shortTerm}/{type}/{pickle_name}", 'w') as f:
            pickle.dump(new_pickle_data, f)

def load_tensorflow_model(path):
    return tf.keras.models.load_model(path)
    # return tf.saved_model.load

def get_string_model_summary(model):
    stringlist = []
    model.summary(print_fn=lambda x: stringlist.append(x))
    short_model_summary = "\n".join(stringlist)
    return short_model_summary

def getHipCenter(pose):
    pose_measure = PoseMeasure(pose)
    return pose_measure.getHipCenterPoint().x

def getPoseHeight(pose, dimension=XYZ):
    pose_measure = PoseMeasure(pose)
    nose_shoulder = pose_measure.getNoseShoulderCenterDistance(dimension)
    shoulder_hip = pose_measure.getShoulderCenterHipCenterDistance(dimension)
    hip_knee = pose_measure.getHipKneeMinusDistance(dimension)
    knee_ankle = pose_measure.getKneeAnkleMinusDistance(dimension)
    return nose_shoulder + shoulder_hip + hip_knee + knee_ankle

def get_embedding_for_tflite_taekwondo_live(poses, embeddingType, dimension="3d"):
    embedding_data = []
    for pose in poses:
        try:
            embedding_data.append(getPoseEmbeddingList(pose, embeddingType.upper(), dimension))
        except Exception as e:
            print(e)
            pass
    return embedding_data

def get_embedding_for_tflite_taekwondo_single(pose, embeddingType, dimension):
    try:
        return getPoseEmbeddingList(pose, embeddingType.upper(), dimension)
    except Exception as e:
        return None

def getFootHeelPosition(pose, dimension=Y):
    pose_measure = PoseMeasure(pose)
    foot = pose_measure.getFootindexPorint(dimension, AVG)
    heel = pose_measure.getHeelPorint(dimension, AVG)
    return (foot + heel)/2

def getAnklePosition(pose,  dimension=Y):
    pose_measure = PoseMeasure(pose)
    ankle = pose_measure.getAnklePoint(dimension, AVG)
    return ankle

def check_option_json_file(path):
    if os.path.isfile(path):
        return get_json_data_all(path)
    else:
        last_path = path.split('/')[-1]
        defalut_path = f'./data/defalut/{last_path}'
        data = get_json_data_all(defalut_path)
        dump_json_data(path, data)
        return data

def ui_auto_complete(ui_file, ui_to_py_file):
    encoding = 'utf-8'
    # UI 파일이 존재하지 않으면 아무 작업도 수행하지 않는다.
    if not os.path.isfile(ui_file):
        return
    # UI 파일이 업데이트 됬는지 확인하고, 업데이트 되었으면 *.py로 변환한다
    if newer(ui_file, ui_to_py_file):
        print(f"{ui_file.split('/')[-1]} has changed")
        # ui 파일이 업데이트 되었다, py파일을 연다.
        fp = open(ui_to_py_file, "w", encoding=encoding)
        # ui 파일을 py파일로 컴파일한다.
        uic.compileUi(ui_file, fp, execute=True, indent=4)
        fp.close()
    else:
        print(f"{ui_file.split('/')[-1]} has not changed")

def remove_trash_pose(poses):
    newPoses = []
    for pose in poses:
        try:
            inputs = getPoseEmbeddingList(pose, "UPPER")
            newPoses.append(pose)
        except:
            continue
    return newPoses

def save_yaml(path, data):
    data = json.loads(json.dumps(data))
    with open(path, 'w') as f:
        yaml.dump(data, f, indent=4, sort_keys=False)    

def save_pickle(path, data):
    with gzip.open(path, 'w') as f:
        pickle.dump(data, f)

def load_yaml(path):
    with open(path, "r") as f:
        data = yaml.full_load(f)
    return data
        
def load_md(path):
    with open(path, "r") as f:
        data = f.read()
    return data
    
def save_md(path, data):
    with open(path, "w") as f:
        f.write(data)

def find_version_from_md(data):
    versionPattern = "### (\d+\.\d+)"
    versionMatches = re.findall(versionPattern, data)
    return versionMatches

def find_commit_from_md(data):
    commitPattern = "- 커밋 : ([^\n]+)"
    commitMatches = re.findall(commitPattern, data)
    return commitMatches