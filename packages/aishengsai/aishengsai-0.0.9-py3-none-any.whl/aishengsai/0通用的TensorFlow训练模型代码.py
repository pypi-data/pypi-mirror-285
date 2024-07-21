# createBy yyj
# createTime: 2024/6/26 10:55
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam

# 假设模块D是一个简单的分类任务
# 定义模型
model = Sequential([
    Dense(128, activation='relu', input_shape=(input_feature_count,)),  # input_feature_count根据实际情况替换
    Dropout(0.5),
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')  # 用于二分类任务
])

# 编译模型
model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='binary_crossentropy',  # 用于二分类任务
    metrics=['accuracy']
)

# 假设已经有了训练数据和标签
# train_data, train_labels = ...  # 需要加载或生成训练数据和标签
# 假设数据已经预处理好，并且train_data是tf.data.Dataset类型

# 训练模型
history = model.fit(train_data, train_labels, epochs=10, batch_size=32)

# 评估模型
# 假设已经有了测试数据和标签
# test_data, test_labels = ...  # 需要加载或生成测试数据和标签
test_loss, test_acc = model.evaluate(test_data, test_labels)
print(f'Test accuracy: {test_acc * 100:.2f}%')

# 保存模型
model.save('module_d_model.h5')
