import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 尝试使用不同的编码来读取文件
df = pd.read_excel('ainum1/fake_job_postings.xlsx')  # 尝试GBK编码
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

# =====================================================================================================================
# 2、大模型微调：示例
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset

# 加载数据集
imdb_dataset = load_dataset('imdb')

# 加载本地预训练模型和分词器
model_path = "/path/to/local/llama-2b"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path, num_labels=2)

# 数据预处理
def preprocess_function(examples):
        return tokenizer(examples['text'], truncation=True, padding='max_length')

encoded_imdb = imdb_dataset.map(preprocess_function, batched=True)

# 训练设置
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy='epoch',
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=encoded_imdb['train'],
    eval_dataset=encoded_imdb['test'],
    tokenizer=tokenizer,
)

# 开始训练
trainer.train()

# 评估模型
trainer.evaluate()


import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from cityscapesscripts.helpers.annotation import Annotation

# 数据预处理
def preprocess_data():
        # 实现数据加载和预处理
    pass

# U-Net 模型定义
def unet_model(input_size=(256, 256, 3)):
        inputs = layers.Input(input_size)
    # 编码器
    c1 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(inputs)
    c1 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(c1)
    p1 = layers.MaxPooling2D((2, 2))(c1)

    c2 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(p1)
    c2 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(c2)
    p2 = layers.MaxPooling2D((2, 2))(c2)

    c3 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(p2)
    c3 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(c3)
    p3 = layers.MaxPooling2D((2, 2))(c3)

    c4 = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(p3)
    c4 = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(c4)
    p4 = layers.MaxPooling2D((2, 2))(c4)

    # 瓶颈层
    c5 = layers.Conv2D(1024, (3, 3), activation='relu', padding='same')(p4)
    c5 = layers.Conv2D(1024, (3, 3), activation='relu', padding='same')(c5)

    # 解码器
    u6 = layers.Conv2DTranspose(512, (2, 2), strides=(2, 2), padding='same')(c5)
    u6 = layers.concatenate([u6, c4])
    c6 = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(u6)
    c6 = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(c6)

    u7 = layers.Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same')(c6)
    u7 = layers.concatenate([u7, c3])
    c7 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(u7)
    c7 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(c7)

    u8 = layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(c7)
    u8 = layers.concatenate([u8, c2])
    c8 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(u8)
    c8 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(c8)

    u9 = layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(c8)
    u9 = layers.concatenate([u9, c1], axis=3)
    c9 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(u9)
    c9 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(c9)

    outputs = layers.Conv2D(1, (1, 1), activation='sigmoid')(c9)

    model = models.Model(inputs=[inputs], outputs=[outputs])
    return model

# 模型编译和训练
def train_model():
        model = unet_model()
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # 数据加载
    train_images, train_labels = preprocess_data()
    val_images, val_labels = preprocess_data()

    # 训练模型
    model.fit(train_images, train_labels, validation_data=(val_images, val_labels), epochs=50, batch_size=16)

    return model

if __name__ == "__main__":
        model = train_model()
    model.save('cityscapes_unet_model.h5')


# pytorch示例：
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image
import os

# 定义 U-Net 模型
class UNet(nn.Module):
        def __init__(self):
            super(UNet, self).__init__()
        self.enc1 = self.conv_block(3, 64)
        self.enc2 = self.conv_block(64, 128)
        self.enc3 = self.conv_block(128, 256)
        self.enc4 = self.conv_block(256, 512)
        self.bottleneck = self.conv_block(512, 1024)
        self.upconv4 = self.upconv_block(1024, 512)
        self.upconv3 = self.upconv_block(512, 256)
        self.upconv2 = self.upconv_block(256, 128)
        self.upconv1 = self.upconv_block(128, 64)
        self.final = nn.Conv2d(64, 1, kernel_size=1)

    def conv_block(self, in_channels, out_channels):
            return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
        )

    def upconv_block(self, in_channels, out_channels):
            return nn.Sequential(
            nn.ConvTranspose2d(in_channels, out_channels, kernel_size=2, stride=2),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
            enc1 = self.enc1(x)
        enc2 = self.enc2(nn.functional.max_pool2d(enc1, kernel_size=2))
        enc3 = self.enc3(nn.functional.max_pool2d(enc2, kernel_size=2))
        enc4 = self.enc4(nn.functional.max_pool2d(enc3, kernel_size=2))
        bottleneck = self.bottleneck(nn.functional.max_pool2d(enc4, kernel_size=2))
        up4 = self.upconv4(bottleneck)
        up4 = torch.cat([up4, enc4], dim=1)
        up3 = self.upconv3(up4)
        up3 = torch.cat([up3, enc3], dim=1)
        up2 = self.upconv2(up3)
        up2 = torch.cat([up2, enc2], dim=1)
        up1 = self.upconv1(up2)
        up1 = torch.cat([up1, enc1], dim=1)
        return torch.sigmoid(self.final(up1))

# 数据集定义
class CityscapesDataset(Dataset):
        def __init__(self, image_dir, mask_dir, transform=None):
            self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.transform = transform
        self.images = os.listdir(image_dir)

    def __len__(self):
            return len(self.images)

    def __getitem__(self, idx):
            img_path = os.path.join(self.image_dir, self.images[idx])
        mask_path = os.path.join(self.mask_dir, self.images[idx].replace('leftImg8bit', 'gtFine_labelIds'))
        image = Image.open(img_path).convert("RGB")
        mask = Image.open(mask_path)
        if self.transform:
                image = self.transform(image)
            mask = self.transform(mask)
        return image, mask

# 数据预处理
transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
])

# 数据集加载
train_dataset = CityscapesDataset(image_dir='path/to/train/images', mask_dir='path/to/train/masks', transform=transform)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

val_dataset = CityscapesDataset(image_dir='path/to/val/images', mask_dir='path/to/val/masks', transform=transform)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

# 训练模型
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = UNet().to(device)
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

num_epochs = 50
for epoch in range(num_epochs):
        model.train()
    train_loss = 0
    for images, masks in train_loader:
            images, masks = images.to(device), masks.to(device)
        outputs = model(images)
        loss = criterion(outputs, masks)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    model.eval()
    val_loss = 0
    with torch.no_grad():
            for images, masks in val_loader:
                images, masks = images.to(device), masks.to(device)
            outputs = model(images)
            loss = criterion(outputs, masks)
            val_loss += loss.item()

    # print(f'Epoch {epoch+1}/{num_epochs}, Train Loss: {train_loss/len(train_loader)}, Val Loss: {val_loss/len(val_loader)}')

# 保存模型
torch.save(model.state_dict(), 'cityscapes_unet_model.pth')
