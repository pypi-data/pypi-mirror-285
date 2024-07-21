import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 尝试使用不同的编码来读取文件
df = pd.read_excel('./resources/fake_job_postings.xlsx')  # 尝试GBK编码
# print(df.head())

# 查看数据集中的空值情况
print(df.isnull().sum())

# 填充空值
df['company_profile'].fillna('', inplace=True)  # 填充 'company_profile' 列的空值为 ''
df['description'].fillna('', inplace=True)      # 填充 'description' 列的空值为 ''
df['requirements'].fillna('', inplace=True)     # 填充 'requirements' 列的空值为 ''
df['benefits'].fillna('', inplace=True)         # 填充 'benefits' 列的空值为 ''

# 填充布尔类型的列
# df['telecommuting'].fillna(False, inplace=True)       # 填充 'telecommuting' 列的空值为 False
# df['has_company_logo'].fillna(False, inplace=True)    # 填充 'has_company_logo' 列的空值为 False
# df['has_questions'].fillna(False, inplace=True)       # 填充 'has_questions' 列的空值为 False

# 填充文本类型的列
df['employment_type'].fillna('Employment not available', inplace=True)   # 填充 'employment_type' 列的空值为 'Employment not available'
df['required_experience'].fillna('Experience not available', inplace=True)  # 填充 'required_experience' 列的空值为 'Experience not available'
df['required_education'].fillna('', inplace=True)   # 填充 'required_education' 列的空值为 'Education not available'
df['industry'].fillna('', inplace=True)             # 填充 'industry' 列的空值为 'Industry not available'
df['function'].fillna('', inplace=True)             # 填充 'function' 列的空值为 'Function not available'

# 填充新增的字段
df['location'].fillna('', inplace=True)   # 填充 'location' 列的空值为 'Location not available'
df['department'].fillna('', inplace=True)  # 填充 'department' 列的空值为 'Department not available'
df['salary_range'].fillna('', inplace=True)  # 填充 'salary_range' 列的空值为 'Salary range not available'

# 检查填充后的空值情况
print(df.isnull().sum())

# 如果需要保存填充后的数据集到文件，可以使用如下语句
# df.to_excel('filled_fake_job_postings.xlsx', index=False)

# 填充空值
df.fillna({
    'required_experience': 'Experience not available',
    'employment_type': 'Employment not available'
}, inplace=True)

# 查看数据框的列名，确认 'required_experience' 是否存在且拼写正确
# print(df.columns)

#过滤
# 使用布尔索引过滤非布尔型数据
filtered_df = df[df['telecommuting'].isin([0, 1])]
print(filtered_df)

# 设置中文字体为 Microsoft YaHei 或者其他支持中文的字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题
# 绘制特征条件下的非欺诈与欺诈情况
# plt.figure(figsize=(12, 6))
# sns.countplot(x='employment_type', hue='fraudulent', data=df)
# plt.title('Non-fraudulent vs. fraudulent postings by employment type')
# plt.xlabel('Employment Type')
# plt.ylabel('Count')
# plt.xticks(rotation=45)
# plt.legend(title='Fraudulent', labels=['No', 'Yes'])
# plt.tight_layout()
# plt.show()

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, LabelEncoder,OneHotEncoder
from sklearn.base import BaseEstimator, TransformerMixin

# 定义 ToStringTransformer
class ToStringTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

def transform(self, X):
    return X.astype(str)

# 划分训练集和测试集
X = filtered_df[['description', 'required_experience', 'employment_type','telecommuting','has_company_logo','has_questions'
    ,'benefits','requirements','company_profile','title','location','department','salary_range','required_education'
    ,'industry','function']]
y = filtered_df['fraudulent']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 定义文本特征提取器和其他特征处理器
# 优化 tfid
# 初始化 TfidfVectorizer，并设置参数
tfidf_vectorizer = TfidfVectorizer(
    max_features=5000,  # 最大特征数
    max_df=0.8,          # 最大文档频率
    min_df=5,            # 最小文档频率
    ngram_range=(1, 2),  # 使用 unigram 和 bigram
    stop_words='english' # 停用词设置为英语停用词表
    # 可以添加其他参数，如 tokenizer、token_pattern 等
)
# 定义文本处理和数值处理的变换器
text_transformer = Pipeline(steps=[
    ('to_string', ToStringTransformer()),
    ('tfidf', TfidfVectorizer())
])

numeric_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# 定义列处理器
preprocessor = ColumnTransformer(
    transformers=[
        ('text1', text_transformer, 'description'),
        ('text2', text_transformer, 'required_experience'),
        ('categorical', categorical_transformer, ['employment_type']),
        ('numeric1', numeric_transformer, []),
        # ('numeric2', numeric_transformer, ['has_company_logo']),
        # ('numeric3', numeric_transformer, ['has_questions']),
        ('text3', text_transformer, 'benefits'),
        ('text4', text_transformer, 'requirements'),
        ('text5', text_transformer, 'company_profile'),
        # ('text6', text_transformer, 'title'),
        # ('text7', text_transformer, 'location'),
        # ('text8', text_transformer, 'department'),
        # ('text9', text_transformer, 'salary_range'),
        # ('text10', text_transformer, 'required_education'),
        # ('text11', text_transformer, 'industry'),
        # ('text12', text_transformer, 'function'),
    ],
    remainder='drop'
)

# 建立管道，包括文本特征提取和分类器
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('clf', RandomForestClassifier(random_state=42))
])

# 拟合模型
pipeline.fit(X_train, y_train)

# 保存模型
import joblib
# 假设 pipeline 是您已经拟合好的 Pipeline 对象

# 定义保存模型的文件路径
model_file = 'pipeline_model.pkl'

# 使用 joblib 保存 Pipeline 模型
joblib.dump(pipeline, model_file)

print(f"Pipeline 模型已保存到 {model_file}")

# 加载 Pipeline 模型
loaded_pipeline = joblib.load(model_file)

# 使用加载的 Pipeline 模型进行预测
y_pred_loaded = loaded_pipeline.predict(X_test)

# 输出加载 Pipeline 模型的分类报告
print(classification_report(y_test, y_pred_loaded))

df_results = pd.read_excel('ainum1/results.xlsx')

# 查看数据集中的空值情况
print(df_results.isnull().sum())

# 填充空值
df_results['company_profile'].fillna('', inplace=True)  # 填充 'company_profile' 列的空值为 ''
df_results['description'].fillna('', inplace=True)      # 填充 'description' 列的空值为 ''
df_results['requirements'].fillna('', inplace=True)     # 填充 'requirements' 列的空值为 ''
df_results['benefits'].fillna('', inplace=True)         # 填充 'benefits' 列的空值为 ''

# 填充布尔类型的列
# df['telecommuting'].fillna(False, inplace=True)       # 填充 'telecommuting' 列的空值为 False
# df['has_company_logo'].fillna(False, inplace=True)    # 填充 'has_company_logo' 列的空值为 False
# df['has_questions'].fillna(False, inplace=True)       # 填充 'has_questions' 列的空值为 False

# 填充文本类型的列
df_results['employment_type'].fillna('Employment not available', inplace=True)   # 填充 'employment_type' 列的空值为 'Employment not available'
df_results['required_experience'].fillna('Experience not available', inplace=True)  # 填充 'required_experience' 列的空值为 'Experience not available'
df_results['required_education'].fillna('', inplace=True)   # 填充 'required_education' 列的空值为 'Education not available'
df_results['industry'].fillna('', inplace=True)             # 填充 'industry' 列的空值为 'Industry not available'
df_results['function'].fillna('', inplace=True)             # 填充 'function' 列的空值为 'Function not available'

# 填充新增的字段
df_results['location'].fillna('', inplace=True)   # 填充 'location' 列的空值为 'Location not available'
df_results['department'].fillna('', inplace=True)  # 填充 'department' 列的空值为 'Department not available'
df_results['salary_range'].fillna('', inplace=True)  # 填充 'salary_range' 列的空值为 'Salary range not available'

# 检查填充后的空值情况
print(df_results.isnull().sum())

# 获取模型训练时的特征列名
expected_columns = ['description', 'required_experience', 'employment_type','telecommuting','has_company_logo','has_questions'
    ,'benefits','requirements','company_profile','title','location','department','salary_range','required_education'
    ,'industry','function']
# 确保新数据按训练时的特征列名顺序排列
df_results = df_results[expected_columns]

# 使用加载的 Pipeline 模型进行预测
df_results_pred = loaded_pipeline.predict(df_results)

# 将预测结果添加到数据框中
df_results['fraudulent'] = df_results_pred

# 保存预测结果到新的文件
df_results.to_excel('ainum1/results_predit.xlsx', index=False)

# # 在测试集上进行预测
# y_pred = pipeline.predict(X_test)

# # 输出分类报告
# print(classification_report(y_test, y_pred))

# # 通过网格搜索（Grid Search）来优化模型的超参数，提高模型的性能。
# from sklearn.model_selection import GridSearchCV

# # 定义参数网格
# param_grid = {
#     'clf__n_estimators': [100, 200, 300],  # 调整随机森林中树的数量
#     'clf__max_depth': [None, 10, 20],  # 调整树的最大深度
#     'clf__min_samples_split': [2, 5, 10]  # 调整节点分裂的最小样本数
# }

# # 网格搜索
# grid_search = GridSearchCV(pipeline, param_grid=param_grid, cv=5, scoring='accuracy')
# grid_search.fit(X_train, y_train)

# # 输出最佳参数和交叉验证结果
# print("Best parameters found: ", grid_search.best_params_)
# print("Best cross-validation accuracy: {:.2f}".format(grid_search.best_score_))

# # 在测试集上评估最佳模型
# best_model = grid_search.best_estimator_
# y_pred = best_model.predict(X_test)
# print(classification_report(y_test, y_pred))
