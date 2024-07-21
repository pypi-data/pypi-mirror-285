# 导入所需库
import cv2
import numpy as np
from image_classification_model import ImageClassificationModel
from object_detection_model import ObjectDetectionModel
from decision_making import DecisionMaking


# 将视频每一帧保存成图片===============begin ,也可以成为数据预处理
# pip install opencv-python
# import cv2
# import os

def save_frame(frame, output_folder, frame_id):
    # 保存帧到指定文件夹
    cv2.imwrite(f"{output_folder}/frame_{frame_id}.jpg", frame)

# 完整的读取视频流到保存图片
import cv2
import os

def save_video_frames(video_path, output_folder):
    # 创建输出文件夹，如果它还不存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 打开视频文件
    video_capture = cv2.VideoCapture(video_path)

    # 检查是否成功打开视频文件
    if not video_capture.isOpened():
        print("Error opening video file")
        return

    # 初始化帧计数器
    frame_count = 0

    while True:
        # 读取下一帧
        sleep_time = 0.1
        ret, frame = video_capture.read()

        # 如果读取帧失败，则表示到达视频末尾
        if not ret:
            break

        # 对帧进行归一化或其他预处理
        frame_normalized = normalize_frame(frame)

        # 构建输出文件名
        filename = f"frame_{frame_count:04d}.jpg"
        filepath = os.path.join(output_folder, filename)

        # 保存帧为图片
        cv2.imwrite(filepath, frame)

        # 更新帧计数器
        frame_count += 1

    # 释放视频捕获对象
    video_capture.release()

    print(f"Saved {frame_count} frames to {output_folder}")

# 使用函数
video_path = "/Users/aresen/Downloads/mp4素材.mp4"
output_folder = "/Users/aresen/Downloads/drive/out"
save_video_frames(video_path, output_folder)

# 将视频每一帧保存成图片===============end


# 将帧归一化预处理 ==========begin
import numpy as np

def normalize_frame(frame):
    """
    将图像帧归一化到0-1范围。

    参数:
    frame (np.array): 输入的图像帧，通常是一个三维numpy数组，形状为(height, width, channels)。

    返回:
    np.array: 归一化后的图像帧。
    """
    # 将图像转换为浮点类型，避免溢出
    float_frame = frame.astype(np.float32)

    # 归一化到0-1范围
    normalized_frame = float_frame / 255.0

    return normalized_frame
# 将帧归一化预处理 ==========end


# 把labelme标记的json式转化成yolov8支持的txt格式数据集格式源码分享： begin
import base64
import random
import shutil
from tqdm import tqdm
import math
import json
import os
import numpy as np
import PIL.Image
import PIL.ImageDraw
import cv2


class ConvertManager(object):
    def __init__(self):
        pass

    def base64_to_numpy(self, img_bs64):
        img_bs64 = base64.b64decode(img_bs64)
        img_array = np.frombuffer(img_bs64, np.uint8)
        cv2_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return cv2_img

    @classmethod
    def load_labels(cls, name_file):
        '''
        load names from file.one name one line
        :param name_file:
        :return:
        '''
        with open(name_file, 'r') as f:
            lines = f.read().rstrip('\n').split('\n')
        return lines

    def get_class_names_from_all_json(self, json_dir):
        classnames = []
        for file in os.listdir(json_dir):
            if not file.endswith('.json'):
                continue
            with open(os.path.join(json_dir, file), 'r', encoding='utf-8') as f:
                data_dict = json.load(f)
                for shape in data_dict['shapes']:
                    if not shape['label'] in classnames:
                        classnames.append(shape['label'])
        return classnames

    def create_save_dir(self, save_dir):
        images_dir = os.path.join(save_dir, 'images')
        labels_dir = os.path.join(save_dir, 'labels')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            os.mkdir(images_dir)
            os.mkdir(labels_dir)
        else:
            if not os.path.exists(images_dir):
                os.mkdir(images_dir)
            if not os.path.exists(labels_dir):
                os.mkdir(labels_dir)
        return images_dir + os.sep, labels_dir + os.sep

    def save_list(self, data_list, save_file):
        with open(save_file, 'w') as f:
            f.write('\n'.join(data_list))

    def __rectangle_points_to_polygon(self, points):
        xmin = 0
        ymin = 0
        xmax = 0
        ymax = 0
        if points[0][0] > points[1][0]:
            xmax = points[0][0]
            ymax = points[0][1]
            xmin = points[1][0]
            ymin = points[1][1]
        else:
            xmax = points[1][0]
            ymax = points[1][1]
            xmin = points[0][0]
            ymin = points[0][1]
        return [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]

    def convert_dataset(self, json_dir, json_list, images_dir, labels_dir, names, save_mode='train'):
        images_dir = os.path.join(images_dir, save_mode)+os.sep
        labels_dir = os.path.join(labels_dir, save_mode)+os.sep
        if not os.path.exists(images_dir):
            os.mkdir(images_dir)
        if not os.path.exists(labels_dir):
            os.mkdir(labels_dir)
        for file in tqdm(json_list):
            with open(os.path.join(json_dir, file), 'r', encoding='utf-8') as f:
                data_dict = json.load(f)
            image_file = os.path.join(json_dir, os.path.basename(data_dict['imagePath']))
            if os.path.exists(image_file):
                shutil.copyfile(image_file, images_dir + os.path.basename(image_file))
            else:
                imageData = data_dict.get('imageData')
                if not imageData:
                    imageData = base64.b64encode(imageData).decode('utf-8')
                    img = self.img_b64_to_arr(imageData)
                    PIL.Image.fromarray(img).save(images_dir + file[:-4] + 'png')
            # convert to txt
            width = data_dict['imageWidth']
            height = data_dict['imageHeight']
            line_list = []
            for shape in data_dict['shapes']:
                data_list = []
                data_list.append(str(names.index(shape['label'])))
                if shape['shape_type'] == 'rectangle':
                    points = self.__rectangle_points_to_polygon(shape['points'])
                    for point in points:
                        data_list.append(str(point[0] / width))
                        data_list.append(str(point[1] / height))


                elif shape['shape_type'] == 'polygon':
                    points = shape['points']
                    for point in points:
                        data_list.append(str(point[0] / width))
                        data_list.append(str(point[1] / height))
                line_list.append(' '.join(data_list))

            self.save_list(line_list, labels_dir + file[:-4] + "txt")

    def split_train_val_test_dataset(self, file_list, train_ratio=0.9, trainval_ratio=0.9, need_test_dataset=False,
                                     shuffle_list=True):
        if shuffle_list:
            random.shuffle(file_list)
        total_file_count = len(file_list)
        train_list = []
        val_list = []
        test_list = []
        if need_test_dataset:
            trainval_count = int(total_file_count * trainval_ratio)
            trainval_list = file_list[:trainval_count]
            test_list = file_list[trainval_count:]
            train_count = int(train_ratio * len(trainval_list))
            train_list = trainval_list[:train_count]
            val_list = trainval_list[train_count:]
        else:
            train_count = int(train_ratio * total_file_count)
            train_list = file_list[:train_count]
            val_list = file_list[train_count:]
        return train_list, val_list, test_list

    def start(self, json_dir, save_dir, names=None, train_ratio=0.9):
        images_dir, labels_dir = self.create_save_dir(save_dir)
        if names is None or len(names) == 0:
            print('class names will load from all json file')
            names = self.get_class_names_from_all_json(json_dir)
        print('find {} class names :'.format(len(names)), names)
        if len(names) == 0:
            return

        self.save_list(names, os.path.join(save_dir, 'labels.txt'))
        print('start convert')
        all_json_list = []
        for file in os.listdir(json_dir):
            if not file.endswith('.json'):
                continue
            all_json_list.append(file)
        train_list, val_list, test_list = self.split_train_val_test_dataset(all_json_list, train_ratio)
        self.convert_dataset(json_dir, train_list, images_dir, labels_dir, names, 'train')
        self.convert_dataset(json_dir, val_list, images_dir, labels_dir, names, 'val')


if __name__ == '__main__':
    cm = ConvertManager()
    cm.start(r'D:\torch1\yolov8-ultralytics-main\tomatoimg_jsonjpg', r'D:\torch1\yolov8-ultralytics-main\mydata')

# 把labelme标记的json式转化成yolov8支持的txt格式数据集格式源码分享：end


# 主函数
def main():
    # 加载模型
    image_classification_model = ImageClassificationModel()
    object_detection_model = ObjectDetectionModel()
    decision_making = DecisionMaking()

    # 从模拟平台获取视频数据
    # video_data = get_video_data_from_simulator()

    # 对视频数据进行预处理
    preprocessed_data = preprocess_data("path","filejpg",(224, 224))

    # 对每一帧图像进行处理
    for frame in preprocessed_data:
        # 图像分类
        classification_results = classify_image(frame, image_classification_model)

        # 目标检测
        detection_results = detect_objects(frame, object_detection_model)

        # 决策处理
        driving_commands = generate_driving_commands(classification_results, detection_results)

        # 行驶控制
        control_vehicle(driving_commands)

if __name__ == "__main__":
    main()
