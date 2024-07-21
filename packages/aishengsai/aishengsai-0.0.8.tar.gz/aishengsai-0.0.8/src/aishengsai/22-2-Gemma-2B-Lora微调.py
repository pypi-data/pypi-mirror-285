# 基础环境配置
# python -m pip install --upgrade pip
# # 更换 pypi 源加速库的安装
# pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
#
# pip install modelscope==1.9.5
# pip install "transformers>=4.40.0"
# pip install streamlit==1.24.0
# pip install sentencepiece==0.1.99
# pip install accelerate==0.29.3
# pip install datasets==2.19.0
# pip install peft==0.10.0
#
# MAX_JOBS=8 pip install flash-attn --no-build-isolation
#

# 模型下载
import torch
from modelscope import snapshot_download, AutoModel, AutoTokenizer
import os

model_dir = snapshot_download('Lucachen/gemma2b', cache_dir='./resources/22-2/autodl-tmp', revision='master')

# 导入环境
from datasets import Dataset
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, DataCollatorForSeq2Seq, TrainingArguments, Trainer, GenerationConfig


# 将JSON文件转换为CSV文件
df = pd.read_json('./huanhuan.json')
ds = Dataset.from_pandas(df)

ds[:3]


# 处理数据集
tokenizer = AutoTokenizer.from_pretrained('./resources/22-2/autodl-tmp/Lucachen/gemma2b', use_fast=False, trust_remote_code=True)

def process_func(example):
    MAX_LENGTH = 384    # Llama分词器会将一个中文字切分为多个token，因此需要放开一些最大长度，保证数据的完整性
    input_ids, attention_mask, labels = [], [], []
    instruction = tokenizer(f"<start_of_turn>system\n现在你要扮演皇帝身边的女人--甄嬛<end_of_turn>\n<start_of_turn>user\n{example['instruction'] + example['input']}<end_of_turn>\n<start_of_turn>model\n", add_special_tokens=False)
    #response = tokenizer(f"{example['output']}", add_special_tokens=False)
    response = tokenizer(f"{example['output']}<end_of_turn>model", add_special_tokens=False)
    input_ids = instruction["input_ids"] + response["input_ids"]
    attention_mask = instruction["attention_mask"] + response["attention_mask"] + [1]  # 因为eos token咱们也是要关注的所以 补充为1
    labels = [-100] * len(instruction["input_ids"]) + response["input_ids"]
    if len(input_ids) > MAX_LENGTH:  # 做一个截断
        input_ids = input_ids[:MAX_LENGTH]
        attention_mask = attention_mask[:MAX_LENGTH]
        labels = labels[:MAX_LENGTH]
    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels
    }

tokenized_id = ds.map(process_func, remove_columns=ds.column_names)
tokenized_id

print(tokenizer.decode(tokenized_id[0]['input_ids']))


tokenizer.decode(list(filter(lambda x: x != -100, tokenized_id[1]["labels"])))


# 创建模型
import torch

model = AutoModelForCausalLM.from_pretrained('./resources/22-2/autodl-tmp/Lucachen/gemma2b', device_map="auto",torch_dtype=torch.bfloat16)
model

model.enable_input_require_grads() # 开启梯度检查点时，要执行该方法

model.dtype


# 模型微调-lora

from peft import LoraConfig, TaskType, get_peft_model

# TrainingArguments这个类的源码也介绍了每个参数的具体作用，当然大家可以来自行探索，这里就简单说几个常用的。
#
# output_dir：模型的输出路径
# per_device_train_batch_size：顾名思义 batch_size
# gradient_accumulation_steps: 梯度累加，如果你的显存比较小，那可以把 batch_size 设置小一点，梯度累加增大一些。
# logging_steps：多少步，输出一次log
# num_train_epochs：顾名思义 epoch
# gradient_checkpointing：梯度检查，这个一旦开启，模型就必须执行model.enable_input_require_grads()，这个原理大家可以自行探索，这里就不细说了。

config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    inference_mode=False, # 训练模式
    r=8, # Lora 秩
    lora_alpha=32, # Lora alaph，具体作用参见 Lora 原理
    lora_dropout=0.1# Dropout 比例
)

model = get_peft_model(model, config)

model.print_trainable_parameters()


# 配置训练参数
args = TrainingArguments(
    output_dir="./output/gemma2b",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    logging_steps=10,
    num_train_epochs=3,
    save_steps=100,
    learning_rate=1e-4,
    save_on_each_node=True,
    gradient_checkpointing=True
)

class ModifiedTrainer(Trainer):
    # 根据输入计算 Loss
    def compute_loss(self, model, inputs, return_outputs=False):
        return model(
            input_ids=inputs["input_ids"],
            labels=inputs["labels"],
        ).loss

    # 保存模型
    def save_model(self, output_dir=None, _internal_call=False):
        from transformers.trainer import TRAINING_ARGS_NAME

        os.makedirs(output_dir, exist_ok=True)
        torch.save(self.args, os.path.join(output_dir, TRAINING_ARGS_NAME))
        saved_params = {
            k: v.to("cpu") for k, v in self.model.named_parameters() if v.requires_grad
        }
        torch.save(saved_params, os.path.join(output_dir, "adapter_model.bin"))

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_id,
    data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, padding=True),
)


trainer.train()

# 保存lora和tokenizer结果

peft_model_id="./gemma2b_lora"
trainer.model.save_pretrained(peft_model_id)
tokenizer.save_pretrained(peft_model_id)


# 加载lora权重推理
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from peft import PeftModel

mode_path = './resources/22-2/autodl-tmp/Lucachen/gemma2b'
lora_path = './gemma2b_lora'

# 加载tokenizer
tokenizer = AutoTokenizer.from_pretrained(mode_path)

# 加载模型
model = AutoModelForCausalLM.from_pretrained(mode_path, device_map="auto",torch_dtype=torch.bfloat16)

# 加载lora权重
model = PeftModel.from_pretrained(model, model_id=lora_path, config=config)

#  使用新的模型进行对话==================无意义的事
# prompt = "你是谁？"
# messages = [
#     # {"role": "system", "content": "现在你要扮演皇帝身边的女人--甄嬛"},
#     {"role": "user", "content": prompt}
# ]
#
# text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
#
# model_inputs = tokenizer([text], return_tensors="pt").to('cuda')
#
# generated_ids = model.generate(
#     model_inputs.input_ids,
#     max_new_tokens=512
# )
# generated_ids = [
#     output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
# ]
#
# response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
#
# print(response)

# 对新模型进行评估
import torch
from transformers import GPT2Tokenizer, GPT2ForSequenceClassification
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import accuracy_score

# 测试集数据（假设已经准备好）
test_texts = [...]  # 测试文本列表
test_labels = [...]  # 对应的标签列表，如果有的话

# 根据tokenizer将文本转换为模型可接受的输入格式
tokenized_texts = tokenizer(test_texts, padding=True, truncation=True, return_tensors="pt")

# 创建数据集和数据加载器
test_dataset = TensorDataset(tokenized_texts['input_ids'], tokenized_texts['attention_mask'])
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# 开始模型评估
model.eval()
predictions = []
true_labels = test_labels if test_labels else None

with torch.no_grad():
    for batch in test_loader:
        input_ids = batch[0].to(model.device)
        attention_mask = batch[1].to(model.device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1)
        predicted_labels = torch.argmax(probabilities, dim=-1)

        predictions.extend(predicted_labels.cpu().numpy())

# 计算准确率
if true_labels:
    accuracy = accuracy_score(true_labels, predictions)
    print(f"准确率：{accuracy:.4f}")
else:
    print("未提供真实标签，无法计算准确率。")



