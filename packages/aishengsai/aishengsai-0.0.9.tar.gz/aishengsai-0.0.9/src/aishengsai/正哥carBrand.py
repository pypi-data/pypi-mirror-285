#图片分类；汽车品牌识别算法：根据图片识别图片中的车是什么品牌的车
import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from keras.utils import to_categorical
from keras.models import load_model
import tensorflow as tf
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input, decode_predictions

# 检查并设置GPU  
gpus = tf.config.list_physical_devices('GPU')  
if gpus:  
    try:  
        # 设置第一个GPU为可见设备  
        tf.config.set_visible_devices(gpus[0], 'GPU')  
        # 配置GPU内存分配  
        tf.config.experimental.set_per_process_gpu_memory_fraction(0.4)  
    except RuntimeError as e:  
        print(e) 
else:
    print("no gpu!")
# 数据预处理
def load_data(data_dir):
    X, y = [], []
    for root, dirs, files in os.walk(data_dir):
        for subdir in dirs:
            label = subdir
            for file in os.listdir(os.path.join(root, subdir)):
                if file.endswith('.jpg') or file.endswith('.png'):
                    img_path = os.path.join(root, subdir, file)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    img = cv2.resize(img, (64, 64))  # 假设所有图片都被缩放为64x64
                    X.append(img)
                    y.append(label)
    X = np.array(X) / 255.0  # 归一化
    y = LabelEncoder().fit_transform(y)  # 标签编码
    y = to_categorical(y)  # 多分类问题，需要one-hot编码
    return X, y

def preprocess_grayscale_image(img_array):  
    # 假设 img_array 是一个形状为 (height, width, 1) 的灰度图像数组  
    # 如果图像值在 0-255 范围内，则首先将其缩放到 0-1  
    img_array = img_array.astype('float32') / 255.0  
      
    # 如果需要进一步的归一化（比如减去均值），可以在这里添加代码  
    # 例如: img_array -= np.mean(img_array)  
      
    # 如果模型需要额外的维度（比如批量大小），可以在这里添加  
    # 例如: img_array = np.expand_dims(img_array, axis=0)  
      
    return img_array


# 划分训练集和测试集
def split_data(X, y, test_size=0.2):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    return X_train, X_test, y_train, y_test

# 构建CNN模型
def build_model(input_shape, num_classes):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dense(num_classes, activation='softmax'))
    return model

# 训练模型
def train_model(model, X_train, y_train, epochs=10, batch_size=32):
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size)

# 评估模型
def evaluate_model(model, X_test, y_test):
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f'Test Loss: {loss}, Test Accuracy: {accuracy}')

# 主函数
def main(data_dir):
    X, y = load_data(data_dir)
    X_train, X_test, y_train, y_test = split_data(X, y)
    input_shape = (64, 64, 1)  # 如果使用彩色图片，则为(64, 64, 3)
    num_classes = y.shape[1]
    model = build_model(input_shape, num_classes)
    train_model(model, X_train.reshape(-1, 64, 64, 1), y_train, epochs=10)
    evaluate_model(model, X_test.reshape(-1, 64, 64, 1), y_test)
    
    #save model
    # 保存模型  
    model.save('saved_model/car_model.h5')

#预测函数
def load_and_predict_image(model_path, img_path):  
    # 加载训练好的模型  
    model = load_model(model_path)
      
    # 加载并预处理图片  
    img = image.image_utils.load_img(img_path, color_mode='rgb',target_size=(64, 64))  # 假设模型需要64*64的图片
    # 使用PIL转换为灰度图像  
    gray_img = img.convert('L') 
    
    img_array = image.image_utils.img_to_array(gray_img) 

    expanded_img_array = np.expand_dims(img_array, axis=0)  # 添加一个维度以匹配模型的输入形状  
    
    preprocessed_img = preprocess_grayscale_image(expanded_img_array)  
      
    # 预测图片  
    predictions = model.predict(preprocessed_img)  
      
    # 如果这是一个分类模型，你可能希望将预测结果解码为人类可读的标签  
    # decoded_predictions = decode_predictions(predictions, top=3)  # 假设我们有一个解码函数  
      
    # 返回预测结果（这里直接返回预测的原始数组）  
    return predictions

# 假设你的数据集目录为'vehicle_dataset'
if __name__ == '__main__':
    #训练模型
    # main('vehicle_dataset') 
    #预测新结果
    # 使用函数  
    model_path = 'saved_model/car_model.h5'
    img_path = 'preditcar/46ac257a6bd70090b4be53bb9f872f3f.jpg'  
    predictions = load_and_predict_image(model_path, img_path)  
    print(predictions)