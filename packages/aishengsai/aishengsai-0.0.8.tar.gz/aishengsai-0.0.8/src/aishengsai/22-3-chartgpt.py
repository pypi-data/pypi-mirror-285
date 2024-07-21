


# 通过labelme标注后生成json文件,通过读取该文件生成图片和标签
import os
import json
from PIL import Image
def load_data(data_dir):
    images = []
    labels = []

    # 遍历文件夹中的每个JSON文件
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            json_file = os.path.join(data_dir, filename)
            with open(json_file, 'r') as f:
                data = json.load(f)

            # for item in data:
                image_path = os.path.join(data_dir, data['imagePath'])
                label = data['shapes'][0]['label']

                # 加载图像
                image = Image.open(image_path).convert('RGB')

                images.append(image)
                labels.append(label)

    return images, labels


# =================================
# 2数据预处理
# 数据集划分为训练集和测试集
# 这里假设你有一个函数可以加载和处理数据，具体实现根据你的数据格式而定
from sklearn.model_selection import train_test_split

# 假设你有一个函数 load_data() 返回 (images, labels) 的格式
images, labels = load_data('/Users/aresen/Downloads/22-3-drive')

# 划分数据集，80% 用于训练，20% 用于测试
train_images, test_images, train_labels, test_labels = train_test_split(images, labels, test_size=0.2, random_state=42)

# 数据增强（这里只是示例，具体的增强方法可以根据需求选择和实现）
# 可以使用 torchvision.transforms 进行数据增强
from torchvision import transforms

transform = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 使用 DataLoader 加载数据
# 可以使用 PyTorch 的 DataLoader 加载数据，批量处理和数据增强
from torch.utils.data import Dataset, DataLoader

class CustomDataset(Dataset):
    def __init__(self, images, labels, transform=None):
        self.images = images
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image = self.images[idx]
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return image, label

# 创建训练集和测试集的 DataLoader
train_dataset = CustomDataset(train_images, train_labels, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

test_dataset = CustomDataset(test_images, test_labels, transform=transform)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)


# ========================================
# 3模型选择和训练
import torch
import torch.nn as nn
import torch.optim as optim

# 简单的卷积神经网络模型示例
class SimpleCNN(nn.Module):
    def __init__(self, num_classes):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc = nn.Linear(16 * 112 * 112, num_classes)

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

# 初始化模型
model = SimpleCNN(num_classes=len(set(train_labels)))

# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 训练模型
num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for inputs, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {running_loss / len(train_loader)}")

print("Finished Training")

# ============================================
# 4模型评估和预测
# 评估模型
# 在测试集上评估模型
model.eval()
correct = 0
total = 0
with torch.no_grad():
    for inputs, labels in test_loader:
        outputs = model(inputs)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print(f"Accuracy on test set: {100 * correct / total}%")

# 测试图片自动标注
# 假设你有一个单独的测试图片，需要预测其标签

model.eval()
# 对测试图片进行预处理（与训练时相同的预处理步骤）
test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def annotate_images(test_folder):
    annotated_results = []

    # 遍历测试文件夹中的每张图片
    for filename in os.listdir(test_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(test_folder, filename)
            # 对单张图片进行预测
            with torch.no_grad():
                # 对单张图片进行预测
                test_image = Image.open(image_path).convert('RGB')
                input_tensor = test_transform(test_image).unsqueeze(0)
                outputs = model(input_tensor)
                _, predicted = torch.max(outputs, 1)
                predicted_class = predicted.item()

            print(f"Predicted class index: {predicted_class}")
    return annotated_results

result = annotate_images('/Users/aresen/Downloads/22-3-drive/test')
print(result)




