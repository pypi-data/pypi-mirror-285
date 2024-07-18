# createBy yyj
# createTime: 2024/6/26 10:54
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from your_dataset import YourDataset  # 假设你已经定义了自己的数据集类

# 数据预处理
def preprocess_input(x):
    # 这里可以添加数据预处理的步骤，例如归一化等
    return x / 255.0  # 示例：将像素值归一化到[0,1]

# 加载数据集
train_dataset = YourDataset(preprocess_input=preprocess_input)
test_dataset = YourDataset(preprocess_input=preprocess_input, train=False)

# 构建模型
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(256, 256, 3)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(512, activation='relu'),
    Dropout(0.5),
    Dense(2, activation='softmax')  # 假设是二分类问题
])

# 编译模型
model.compile(optimizer=Adam(learning_rate=0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# 训练模型
history = model.fit(train_dataset, epochs=10)  # 假设train_dataset返回了训练数据和标签

# 评估模型
test_loss, test_acc = model.evaluate(test_dataset)
print(f'Test accuracy: {test_acc * 100:.2f}%')

# 保存模型
model.save('my_autopilot_model.h5')
