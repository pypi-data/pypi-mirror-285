import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

# 步骤一：数据探索
# 读取数据
data = pd.read_csv('credit.csv')

# 填充空值
data.fillna(data.mean(), inplace=True)

# 处理性别和省份字段
data['gender'] = data['gender'].map({'M': 0, 'F': 1})
encoder = OneHotEncoder()
province_encoded = encoder.fit_transform(data[['province']]).toarray()
province_df = pd.DataFrame(province_encoded, columns=encoder.get_feature_names(['province']))
data = pd.concat([data.drop(['province'], axis=1), province_df], axis=1)

# 处理异常值（这里假设已经处理）


# 步骤二：数据分析与挖掘
# 画图展示违约情况（这里省略具体绘图代码）

# 切分数据集
X = data.drop('default', axis=1)
y = data['default']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 标准化特征
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 建立模型
model = LogisticRegression()
model.fit(X_train, y_train)

# 步骤三：调参与优化
# 模型参数调优（这里假设已经调优）

# 预测并计算f1分数
y_pred = model.predict(X_test)
f1 = f1_score(y_test, y_pred)
print("F1 Score:", f1)