import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer


# #数据准备与预处理=============================
# 加载数据集
data = pd.read_csv('./resources/22-1/aclImdb_train.csv')  # 替换为您的数据集路径

# 分词器初始化
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# 文本编码和分词
def tokenize_text(text, tokenizer, max_length):
    tokenized = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=max_length,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt'
    )
    return tokenized['input_ids'], tokenized['attention_mask']



# 应用分词器并划分训练集和验证集
max_length = 128  # 句子的最大长度
input_ids = []
attention_masks = []

for text in data['text']:
    encoded_text, att_mask = tokenize_text(text, tokenizer, max_length)
    input_ids.append(encoded_text)
    attention_masks.append(att_mask)

labels = data['label'].values

# 划分训练集和验证集
train_inputs, val_inputs, train_labels, val_labels = train_test_split(
    input_ids, labels, random_state=2022, test_size=0.1
)

train_masks, val_masks, _, _ = train_test_split(
    attention_masks, labels, random_state=2022, test_size=0.1
)



# 2微调BERT模型===========================
import torch
from transformers import BertForSequenceClassification, AdamW
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from transformers import BertForSequenceClassification, AdamW, get_linear_schedule_with_warmup

# 转换为Tensor
train_inputs = torch.cat(train_inputs, dim=0)
val_inputs = torch.cat(val_inputs, dim=0)
train_labels = torch.tensor(train_labels)
val_labels = torch.tensor(val_labels)
train_masks = torch.cat(train_masks, dim=0)
val_masks = torch.cat(val_masks, dim=0)

# 创建数据加载器
batch_size = 32
train_data = TensorDataset(train_inputs, train_masks, train_labels)
train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
val_data = TensorDataset(val_inputs, val_masks, val_labels)
val_loader = DataLoader(val_data, batch_size=batch_size, shuffle=False)

# 初始化BERT模型和分类器
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# 定义优化器和学习率调度器
optimizer = AdamW(model.parameters(), lr=2e-5, eps=1e-8)
epochs = 3
total_steps = len(train_loader) * epochs
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

# 训练模型
for epoch in range(epochs):
    model.train()
    total_train_loss = 0

    for batch in train_loader:
        b_input_ids = batch[0].to(device)
        b_input_mask = batch[1].to(device)
        b_labels = batch[2].to(device)

        model.zero_grad()
        outputs = model(b_input_ids, attention_mask=b_input_mask, labels=b_labels)
        loss = outputs.loss
        total_train_loss += loss.item()

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()

    avg_train_loss = total_train_loss / len(train_loader)

    # 在验证集上评估
    model.eval()
    total_val_loss = 0
    predictions = []
    true_labels = []

    for batch in val_loader:
        b_input_ids = batch[0].to(device)
        b_input_mask = batch[1].to(device)
        b_labels = batch[2].to(device)

        with torch.no_grad():
            outputs = model(b_input_ids, attention_mask=b_input_mask, labels=b_labels)
            loss = outputs.loss
            logits = outputs.logits

        total_val_loss += loss.item()
        logits = logits.detach().cpu().numpy()
        label_ids = b_labels.to('cpu').numpy()
        predictions.extend(logits.argmax(axis=-1))
        true_labels.extend(label_ids)

    avg_val_loss = total_val_loss / len(val_loader)

    # 计算验证集上的准确率
    val_accuracy = (predictions == true_labels).mean()

    print(f'Epoch {epoch + 1}/{epochs}')
    print(f'Training Loss: {avg_train_loss:.4f} | Validation Loss: {avg_val_loss:.4f} | Validation Accuracy: {val_accuracy:.4f}')


# 3.测试集推理===========================
# 加载并处理测试集
test_data = pd.read_csv('./resources/22-1/aclImdb_test.csv')  # 替换为您的测试集路径

# 应用相同的分词器和处理步骤
test_input_ids = []
test_attention_masks = []

for text in test_data['text']:
    encoded_text, att_mask = tokenize_text(text, tokenizer, max_length)
    test_input_ids.append(encoded_text)
    test_attention_masks.append(att_mask)

test_input_ids = torch.cat(test_input_ids, dim=0)
test_attention_masks = torch.cat(test_attention_masks, dim=0)

test_dataset = TensorDataset(test_input_ids, test_attention_masks)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# 在测试集上进行推理
model.eval()
predictions = []

for batch in test_loader:
    b_input_ids = batch[0].to(device)
    b_input_mask = batch[1].to(device)

    with torch.no_grad():
        outputs = model(b_input_ids, attention_mask=b_input_mask)
        logits = outputs.logits

    logits = logits.detach().cpu().numpy()
    predictions.extend(logits.argmax(axis=-1))

# 假设您有测试集的真实标签，可以计算测试集的准确率等指标
# test_labels = test_data['label'].values
# test_accuracy = (predictions == test_labels).mean()
# print(f'Test Accuracy: {test_accuracy:.4f}')

