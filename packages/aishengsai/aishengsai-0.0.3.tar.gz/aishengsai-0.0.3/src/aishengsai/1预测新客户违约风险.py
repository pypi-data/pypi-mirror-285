# createBy yyj
# createTime: 2024/6/26 10:12
# 导入所需的库
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
import matplotlib.pyplot as plt

# 步骤一：数据探索与清洗
# 读取数据集
data = pd.read_csv('resources/credit.csv')

# 填充空值
imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
data.fillna(imputer.fit_transform(data), inplace=True)

# 性别用0,1替换，省份用one-hot编码替换
data['gender'] = data['gender'].map({'female': 0, 'male': 1})
encoder = OneHotEncoder(sparse=False)
data_encoded = pd.DataFrame(encoder.fit_transform(data[['province']]))
data = pd.concat([data, data_encoded], axis=1)
data.drop('province', axis=1, inplace=True)

# 处理异常值（示例：限制年龄在合理范围内）
data = data[(data['age'] >= 18) & (data['age'] <= 90)]

# 步骤二：数据分析与挖掘
# 切分数据集
X = data.drop(['default'], axis=1)
y = data['default']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 建立模型
model = RandomForestClassifier()

# 步骤三：模型训练
model.fit(X_train, y_train)

# 参数调优（示例：使用网格搜索进行参数调优）
# 需要安装 GridSearchCV: pip install scikit-learn-extra
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [10, 20, None]
}
grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, scoring='f1')
grid_search.fit(X_train, y_train)

# 使用最佳参数的模型
best_model = grid_search.best_estimator_

# 模型评估
y_pred = best_model.predict(X_test)
f1 = f1_score(y_test, y_pred)

# 可视化（示例：违约情况的可视化）
# 假设我们根据'income'字段进行分组可视化
data['default'].value_counts().plot(kind='bar')
plt.title('Default Frequency')
plt.xlabel('Default')
plt.ylabel('Frequency')
plt.show()

