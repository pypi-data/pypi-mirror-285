import cv2
import numpy as np

# pip install opencv-python

# 加载预训练的模型（例如，YOLOv3）
model = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3.weights')

# 加载类别标签
with open('coco.names', 'r') as f:
    labels = [line.strip() for line in f]

# 读取图像列表
image_files = ['image1.jpg', 'image2.jpg', 'image3.jpg']

# 创建一个空的结果列表
results = []

# 遍历图像列表
for image_file in image_files:
    # 读取图像
    image = cv2.imread(image_file)

    # 获取图像尺寸
    height, width, _ = image.shape

    # 将图像转换为blob格式
    blob = cv2.dnn.blobFromImage(image, 1 / 255, (416, 416), swapRB=True, crop=False)

    # 设置网络输入
    model.setInput(blob)

    # 运行前向传播以获取检测结果
    output_layers = model.getUnconnectedOutLayersNames()
    layer_outputs = model.forward(output_layers)

    # 解析检测结果
    detections = []
    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                # 获取边界框坐标
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                # 添加检测结果到列表中
                detections.append((labels[class_id], confidence, x, y, w, h))

    # 将检测结果添加到结果列表中
    results.append(detections)

# 将结果写入文件
with open('results.txt', 'w') as f:
    for i, detections in enumerate(results):
        f.write(f'Image {i + 1}:')
        for label, confidence, x, y, w, h in detections:
            f.write(f'{label}: {confidence:.2f}, ({x}, {y}, {w}, {h})')
        f.write('')
