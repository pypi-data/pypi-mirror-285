# createBy yyj
# createTime: 2024/6/26 10:47
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from datasets import load_dataset

# 步骤1: 数据预处理
# 加载数据集
dataset = load_dataset("path_to_your_dataset_script")  # 需要替换为实际数据集脚本路径

# 对数据集进行预处理，这里需要根据具体数据集格式进行调整
# 例如，分割训练集和验证集，数据清洗等

# 步骤2: 加载预训练模型和分词器
model_name = "gemma-2b"  # 根据实际使用的模型进行替换
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)  # num_labels根据任务调整

# 步骤3: 模型微调
# 准备训练参数
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,              # 小心调整
    per_device_train_batch_size=16,   # 小心调整
    per_device_eval_batch_size=64,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
)

# 将数据集转换为模型可接受的格式
def preprocess_function(examples):
    return tokenizer(examples["text"], truncation=True)

# 训练和评估
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    tokenizer=tokenizer,
    # 如果需要在训练中使用数据集的预处理功能，可以在这里添加
    # preprocess_train_dataset=dataset["train"].map(preprocess_function, batched=True),
    # preprocess_eval_dataset=dataset["validation"].map(preprocess_function, batched=True),
)

# 训练模型
trainer.train()

# 在测试集上进行推理
eval_results = trainer.evaluate()

# 打印评估结果
print(eval_results)

# 保存模型
model.save_pretrained("./saved_model")
tokenizer.save_pretrained("./saved_model")
