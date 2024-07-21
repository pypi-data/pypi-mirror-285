import torch
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification, AdamW, get_linear_schedule_with_warmup
from torch.utils.data import TensorDataset, DataLoader

# 检查是否有可用的GPU，如果有则使用第一个可用的GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Using device: {device}')

# 加载数据
train_data = pd.read_csv('./resources/22-1/aclImdb_train.csv')
test_data = pd.read_csv('./resources/22-1/aclImdb_test.csv')

# 分词器初始化
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# 准备数据集
def prepare_dataset(data, tokenizer, max_length):
    inputs = tokenizer(list(data['text']), padding=True, truncation=True, max_length=max_length, return_tensors='pt')
    labels = torch.tensor(data['label'].values)
    dataset = TensorDataset(inputs['input_ids'], inputs['attention_mask'], labels)
    return dataset

max_length = 128
train_dataset = prepare_dataset(train_data, tokenizer, max_length)
test_dataset = prepare_dataset(test_data, tokenizer, max_length)

# 创建数据加载器
batch_size = 32
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# 初始化BERT模型和分类器
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
model.to(device)

# 定义优化器和学习率调度器
optimizer = AdamW(model.parameters(), lr=2e-5, eps=1e-8)
epochs = 3
total_steps = len(train_loader) * epochs
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

# 训练模型
model.train()

for epoch in range(epochs):
    total_train_loss = 0

    for batch in train_loader:
        input_ids = batch[0].to(device)
        attention_mask = batch[1].to(device)
        labels = batch[2].to(device)

        model.zero_grad()
        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        total_train_loss += loss.item()

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()

    avg_train_loss = total_train_loss / len(train_loader)
    print(f'Epoch {epoch + 1}/{epochs}, Training Loss: {avg_train_loss:.4f}')

# 在测试集上评估模型
model.eval()
total_test_loss = 0
predictions = []
true_labels = []

for batch in test_loader:
    input_ids = batch[0].to(device)
    attention_mask = batch[1].to(device)
    labels = batch[2].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        logits = outputs.logits

    total_test_loss += loss.item()
    logits = logits.detach().cpu().numpy()
    label_ids = labels.to('cpu').numpy()
    predictions.extend(logits.argmax(axis=-1))
    true_labels.extend(label_ids)

avg_test_loss = total_test_loss / len(test_loader)
test_accuracy = (predictions == true_labels).mean()

print(f'Test Loss: {avg_test_loss:.4f}, Test Accuracy: {test_accuracy:.4f}')
