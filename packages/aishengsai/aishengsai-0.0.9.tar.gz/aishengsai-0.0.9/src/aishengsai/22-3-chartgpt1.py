import os
import json
import random
from PIL import Image
import torch
from torchvision import transforms
from sklearn.model_selection import train_test_split

# 加载数据函数，将英文标签转换为整数编码，并划分为训练集和测试集
def load_data(data_dir, test_size=0.2, random_state=42):
    images = []
    labels = []
    label_map = {}  # 创建一个标签到整数的映射字典
    label_index = 0

    # 遍历文件夹中的每个 JSON 文件
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            json_file = os.path.join(data_dir, filename)
            with open(json_file, 'r') as f:
                data = json.load(f)

            # 解析每个 JSON 对象并加载图像和标签
            # for item in data:
                image_path = os.path.join(data_dir, data['imagePath'])
                label = data['shapes'][0]['label']

                # 如果标签不在映射字典中，将其添加到字典中
                if label not in label_map:
                    label_map[label] = label_index
                    label_index += 1

                # 将标签转换为整数编码
                label_id = label_map[label]

                # 加载图像
                image = Image.open(image_path).convert('RGB')

                images.append(image)
                labels.append(label_id)

    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=test_size, random_state=random_state)

    return X_train, X_test, y_train, y_test, label_map

# 示例用法
data_dir = '/Users/aresen/Downloads/22-3-drive'  # 修改为你的数据文件夹路径

# 加载数据并划分训练集和测试集
X_train, X_test, y_train, y_test, label_map = load_data(data_dir)

# 打印标签映射
print("Label map:")
print(label_map)

# 定义数据预处理步骤
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 创建数据集实例
class CustomDataset(torch.utils.data.Dataset):
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

# 创建训练集和测试集的数据集实例
train_dataset = CustomDataset(X_train, y_train, transform=transform)
test_dataset = CustomDataset(X_test, y_test, transform=transform)

# 创建 DataLoader
batch_size = 32
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# 示例模型定义和训练循环
class SimpleCNN(torch.nn.Module):
    def __init__(self, num_classes):
        super(SimpleCNN, self).__init__()
        self.conv1 = torch.nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1)
        self.relu = torch.nn.ReLU()
        self.pool = torch.nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc = torch.nn.Linear(16 * 112 * 112, num_classes)

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

model = SimpleCNN(num_classes=len(label_map))  # 根据标签映射的大小定义模型的输出类别数

# 定义损失函数和优化器
criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# 训练循环
num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for images, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    print(f"Epoch [{epoch+1}/{num_epochs}], Training Loss: {running_loss / len(train_loader)}")

#  保存模型
import torch

# 假设模型定义为 model

# 保存模型的文件路径
model_path = './drive.pth'

# 保存模型
torch.save(model, model_path)

print(f"Model saved to {model_path}")

# 加载模型进行使用 ====================
# 定义模型结构
model = SimpleCNN(num_classes=10)  # 示例中的模型结构，如果与原模型结构一致

# 加载保存的模型参数
# model_path = './drive.pth'
# model.load_state_dict(torch.load(model_path))

# 将模型设为评估模式
model.eval()

# 可以继续使用模型进行推理或其他操作
# ===================================================

# 在测试集上评估模型
model.eval()
correct = 0
total = 0
with torch.no_grad():
    for images, labels in test_loader:
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print(f"Accuracy on test set: {100 * correct / total}%")

print("Finished Training and Testing")

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
