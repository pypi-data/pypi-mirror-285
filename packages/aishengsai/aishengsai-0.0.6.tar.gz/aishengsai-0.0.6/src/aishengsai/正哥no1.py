
##############客户流失预测
# 某电信公司希望通过数据分析与挖掘，
# 预测哪些客户可能会在未来的几个月内流失，
# 从而提前采取措施进行挽留。公司提供了一份客户数据集，其中包含了客户的基本信息、服务使用情况和历史流失情况等。
##############
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------数据清洗和可视化-----------------------
# 读取数据
data = pd.read_csv('./before1/customer_data.csv')

# 显示数据基本信息
print(data.info())

# 处理缺失值
data = data['gender'].fillna('',inplace=True)

# 转换数据类型
data['total_charges'] = pd.to_numeric(data['total_charges'], errors='coerce')
data = data.dropna()

# 数据可视化
# 性别比例
sns.countplot(data['gender'])
plt.title('Gender Distribution')
plt.show()

# 不同合同类型的流失率
# plt.plot(x='contract', hue='churn', data=data)
sns.countplot(x='contract', hue='churn', data=data)
plt.title('Churn Rate by Contract Type')
plt.show()
# ----------------数据清洗和可视化-----------------------end
# ----------------数据集划分与模型训练-----------------------
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score,confusion_matrix,classification_report
from sklearn.linear_model import LogisticRegression

#优化1 ：使用过采样方法 
from imblearn.over_sampling import SMOTE

# 特征选择
features = ['tenure', 'monthly_charges', 'total_charges']
X = data[features]
#y 是目标变量（标签），通过将Churn列的值转换为二进制格式（"Yes" 变为 1，"No" 变为 0）来创建
y = data['churn'].apply(lambda x: 1 if x == 'Yes' else 0)

# 确保 X 是一个 DataFrame
X = pd.DataFrame(X, columns=features)

# 数据集划分
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42)

#-------------模型优化:过采样-------------------------
# 使用 SMOTE 进行过采样
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# 标准化处理
scaler = StandardScaler()
X_train_resampled = scaler.fit_transform(X_train_resampled)
X_test = scaler.transform(X_test)

# 训练模型
model = LogisticRegression()
model.fit(X_train_resampled, y_train_resampled)

#--------------------------------方法1----------------------------
print(X.shape,y.shape)
# 标准化处理
# scaler = StandardScaler()
# X_train = scaler.fit_transform(X_train)
# X_test = scaler.transform(X_test)

#训练模型
# model = LogisticRegression()
# model.fit(X_train,y_train)

# ----------------数据集划分与模型训练-----------------------end

#-----------------采用随机森林模型-------------
# 训练随机森林模型
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train_resampled, y_train_resampled)

# 评估模型
y_pred_rf = rf_model.predict(X_test)
print(f"Random Forest Accuracy: {accuracy_score(y_test, y_pred_rf)}")
print(confusion_matrix(y_test, y_pred_rf))
print(classification_report(y_test, y_pred_rf, zero_division=0))

#-----------------采用随机森林模型-------------end

#-----------------采用XGBoost模型-------------
import xgboost as xgb
# 使用 XGBoost 训练模型
xgb_model = xgb.XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss')
xgb_model.fit(X_train_resampled, y_train_resampled)

# 评估 XGBoost 模型
y_pred_xgb = xgb_model.predict(X_test)
print(f"XGBoost Accuracy: {accuracy_score(y_test, y_pred_xgb)}")
print(confusion_matrix(y_test, y_pred_xgb))
print(classification_report(y_test, y_pred_xgb, zero_division=0))
#-----------------采用XGBoost模型------------- end

#在验证集上输出结果
y_pred = model.predict(X_test)
print(f'accuracy_score:{accuracy_score(y_test,y_pred)}')
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred,zero_division=0))

# 模型评估与可视化 ROC（Receiver Operating Characteristic）曲线是一个用于评估分类模型的工具，
# 它显示了模型在不同阈值下的表现。ROC 曲线的 x 轴表示假阳性率（False Positive Rate, FPR），y 轴表示真正率（True Positive Rate, TPR）。
from sklearn.metrics import roc_curve,roc_auc_score
#绘制ROC曲线
fpr,tpr,thresholds = roc_curve(y_test,model.predict_proba(X_test)[:,1])

plt.plot(fpr,tpr,label='ROC curve')
plt.xlabel('false positive rate')
plt.xlabel('true positive rate')
plt.title('ROC curve')
plt.show()


#计算AUC分数 越接近1 AUC（Area Under the Curve）分数是ROC曲线下的面积，用于量化模型的整体性能。AUC值范围从0到1，值越大表示模型的性能越好
print(f"AUC Score:{roc_auc_score(y_test,model.predict_proba(X_test)[:,1])}")



#----------------模型调优-网格搜索------------------------
from sklearn.model_selection import GridSearchCV

# 定义参数网格
# param_grid: 这是一个字典，其中包含了要调优的超参数及其可能的值。
# C: 正则化强度的倒数，较小的值会导致更强的正则化。常用的值包括 0.1, 1, 10, 和 100。
# solver: 优化算法的类型，这里选择了 liblinear，它是一个适用于小数据集的优化算法。对于更大的数据集，通常选择 lbfgs 或 saga。
param_grid = {
    'C': [0.1, 1, 10, 100],
    'solver': ['liblinear'],
    'class_weight': ['balanced', None]  # 添加 class_weight 参数
}

# 网格搜索
# GridSearchCV: 这是一个用于系统化调参的工具，通过指定的参数网格在训练数据上进行交叉验证，以找到最佳的超参数组合。
# LogisticRegression(): 要调优的模型。
# param_grid: 定义了要搜索的参数及其值。
# cv=5: 使用5折交叉验证来评估每组参数组合的性能。
# scoring='accuracy': 评价指标是准确率。
# fit 方法将模型训练在训练数据集上，并根据交叉验证的结果选择最佳的超参数组合。
grid_search = GridSearchCV(LogisticRegression(), param_grid, cv=5, scoring='accuracy')
# grid_search.fit(X_train, y_train)
grid_search.fit(X_train_resampled, y_train_resampled)

# 最优参数与最优模型
# best_params: 获取在网格搜索过程中表现最佳的超参数组合。
# best_model: 获取使用最佳参数训练后的模型。
best_params = grid_search.best_params_
best_model = grid_search.best_estimator_

# 评估调优后的模型
# best_model.predict(X_test): 使用最佳模型对测试数据进行预测。
# accuracy_score(y_test, y_pred_optimized): 计算调优后模型在测试数据上的准确率。
# confusion_matrix(y_test, y_pred_optimized): 计算混淆矩阵，显示预测结果与真实标签之间的关系。
# classification_report(y_test, y_pred_optimized): 生成分类报告，包括精确度（Precision）、召回率（Recall）、F1分数（F1-score）等评估指标。
y_pred_optimized = best_model.predict(X_test)
print(f"Optimized Accuracy: {accuracy_score(y_test, y_pred_optimized)}")
print(confusion_matrix(y_test, y_pred_optimized))
print(classification_report(y_test, y_pred_optimized))