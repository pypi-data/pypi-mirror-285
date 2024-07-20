import os
import pandas as pd

def load_data(folder):
    data = []
    for label in ['pos', 'neg']:
        sentiment = 1 if label == 'pos' else 0
        path = os.path.join(folder, label)
        for filename in os.listdir(path):
            with open(os.path.join(path, filename), 'r', encoding='utf-8') as file:
                text = file.read()
                data.append({'text': text, 'label': sentiment})
    return data

# 加载训练集和测试集数据
train_data = load_data('/Users/aresen/3.Work/8866.Learn/PythonProject/1.learnPython/shengsai/src/aishengsai/resources/22-1/aclImdb/train')
test_data = load_data('/Users/aresen/3.Work/8866.Learn/PythonProject/1.learnPython/shengsai/src/aishengsai/resources/22-1/aclImdb/test')

# 转换为DataFrame并保存为CSV文件
train_df = pd.DataFrame(train_data)
test_df = pd.DataFrame(test_data)

train_df.to_csv('./resources/22-1/aclImdb_train.csv', index=False)
test_df.to_csv('./resources/22-1/aclImdb_test.csv', index=False)
