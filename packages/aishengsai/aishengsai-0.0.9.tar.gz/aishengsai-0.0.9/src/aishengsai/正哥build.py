import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models.detection import FasterRCNN
from torchvision.models.detection.rpn import AnchorGenerator
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models import resnet50
from torchvision.ops import MultiScaleRoIAlign


# 定义自定义目标检测模型
class CustomFasterRCNN(nn.Module):
    def __init__(self, num_classes):
        super(CustomFasterRCNN, self).__init__()

        # Load a pre-trained ResNet-50 model
        backbone = resnet50(pretrained=True)
        # Remove the classification head
        backbone = nn.Sequential(*list(backbone.children())[:-2])
        backbone.out_channels = 2048  # ResNet-50's output channels

        # Define an anchor generator
        anchor_generator = AnchorGenerator(
            sizes=((32, 64, 128, 256, 512),),
            aspect_ratios=((0.5, 1.0, 2.0),) * 5
        )

        # Define the ROI pooling layers
        # roi_pooler = nn.AdaptiveMaxPool2d(output_size=(7, 7))
        box_roi_pool = MultiScaleRoIAlign(featmap_names=['0'], output_size=7, sampling_ratio=2)

        # Create the FasterRCNN model
        self.model = FasterRCNN(
            backbone,
            num_classes=num_classes,
            rpn_anchor_generator=anchor_generator,
            box_roi_pool=box_roi_pool
        )

    def forward(self, images, targets=None):
        return self.model(images, targets)

# 实例化模型
num_classes = 4  # 目标类别数量（包括背景）
model = CustomFasterRCNN(num_classes=num_classes)

import torch
import torch.optim as optim
from torch.utils.data import DataLoader

# 准备数据集
# 这里需要定义一个数据集类，继承自torch.utils.data.Dataset
import torch
from torch.utils.data import Dataset
from pycocotools.coco import COCO
import numpy as np
import cv2


#定义了一个CocoDataset类，用于从COCO格式的标注文件加载数据
class CocoDataset(Dataset):
    def __init__(self, coco_json, image_dir, transform=None):
        self.coco = COCO(coco_json)
        self.image_dir = image_dir
        self.transform = transform
        self.ids = list(self.coco.imgs.keys())
        self.classes = self.coco.loadCats(self.coco.getCatIds())
        self.class_to_id = {cat['name']: cat['id'] for cat in self.classes}

    def __getitem__(self, index):
        img_id = self.ids[index]
        print(f"Trying to load image with ID: {img_id}")
        img_info = self.coco.loadImgs(img_id)[0]
        img_path = f"{self.image_dir}/{img_info['file_name']}"

        # Load image
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Load annotations
        ann_ids = self.coco.getAnnIds(imgIds=img_id)
        annotations = self.coco.loadAnns(ann_ids)

        boxes = []
        labels = []
        for ann in annotations:
            x, y, w, h = ann['bbox']
            boxes.append([x, y, x + w, y + h])
            labels.append(ann['category_id'])

        boxes = torch.tensor(boxes, dtype=torch.float32)
        labels = torch.tensor(labels, dtype=torch.int64)

        target = {'boxes': boxes, 'labels': labels}

        if self.transform:
            image, target = self.transform(image, target)

        return image, target

    def __len__(self):
        return len(self.ids)


#定义一个数据转换类
from torchvision.transforms import functional as F


class CustomTransform:
    def __call__(self, image, target):
        # 将图像转换为Tensor
        image = F.to_tensor(image)
        return image, target


from torch.utils.data import DataLoader


def collate_fn(batch):
    images, targets = zip(*batch)
    images = list(images)
    targets = list(targets)
    return images, targets


# 数据集路径 todo
train_coco_json = '../labelme/coco/coco.json'
val_coco_json = '../labelme/coco/coco.json'
image_dir = '../images'

# 创建数据集和数据加载器
train_dataset = CocoDataset(coco_json=train_coco_json, image_dir=image_dir, transform=CustomTransform())
val_dataset = CocoDataset(coco_json=val_coco_json, image_dir=image_dir, transform=CustomTransform())

# 数据加载器
train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True, collate_fn=collate_fn)
val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False, collate_fn=collate_fn)

# 定义优化器
optimizer = optim.SGD(model.parameters(), lr=0.005, momentum=0.9, weight_decay=0.0005)

# 训练模型
num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    for images, targets in train_loader:
        optimizer.zero_grad()
        loss_dict = model(images, targets)
        losses = sum(loss for loss in loss_dict.values())
        losses.backward()
        optimizer.step()

    # 验证模型
    model.eval()
    with torch.no_grad():
        for images, targets in val_loader:
            loss_dict = model(images, targets)
            # 计算验证集的指标

import matplotlib.pyplot as plt
from torchvision.transforms import functional as F

# 推理
model.eval()
with torch.no_grad():
    for images, _ in val_loader:
        predictions = model(images)
        for image, prediction in zip(images, predictions):
            image = F.to_pil_image(image[0])
            plt.imshow(image)
            plt.title('Predictions')
            plt.show()
            # 可视化预测结果
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def visualize_predictions(image, predictions):
    fig, ax = plt.subplots(1)
    ax.imshow(image)

    for box in predictions['boxes']:
        rect = patches.Rectangle(
            (box[0], box[1]), box[2] - box[0], box[3] - box[1],
            linewidth=1, edgecolor='r', facecolor='none'
        )
        ax.add_patch(rect)

    plt.show()