from datasets import Dataset
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, DataCollatorForSeq2Seq, TrainingArguments, Trainer, GenerationConfig

import jsonlines

# * 加载训练集
import datasets
ds = datasets.load_dataset('json', data_files="./qa_train.jsonl", split="train")

# * 模型初始化，加载模型
tokenizer = AutoTokenizer.from_pretrained('/root/models/qwen-1.8b/', use_fast=False, trust_remote_code=True)
tokenizer.pad_token_id = tokenizer.eod_id


model = AutoModelForCausalLM.from_pretrained('/root/models/qwen-1.8b/', device_map="auto",torch_dtype=torch.float32, trust_remote_code=True)

# model.enable_input_require_grads() # 开启梯度检查点时，要执行该方法  

# * Lora配置
from peft import LoraConfig, TaskType, get_peft_model

#  loraConfig
config = LoraConfig(
    task_type=TaskType.CAUSAL_LM, 
    target_modules=["c_attn", "c_proj", "w1", "w2"],  # 这个不同的模型需要设置不同的参数，需要看模型中的attention层
    inference_mode=False, # 训练模式
    r=8, # Lora 秩
    lora_alpha=32, # Lora alaph，具体作用参见 Lora 原理
    lora_dropout=0.1# Dropout 比例
)

model = get_peft_model(model, config)
model.print_trainable_parameters()

# * 数据集处理
def process_func(example):
    MAX_LENGTH = 384    # Llama分词器会将一个中文字切分为多个token，因此需要放开一些最大长度，保证数据的完整性
    input_ids, attention_mask, labels = [], [], []
    instruction = tokenizer(f"<|im_start|>system\n<|im_end|>\n<|im_start|>user\n{example['instruction'] + example['input']}<|im_end|>\n<|im_start|>assistant\n", add_special_tokens=False)  # add_special_tokens 不在开头加 special_tokens
    response = tokenizer(f"{example['output']}", add_special_tokens=False)
    input_ids = instruction["input_ids"] + response["input_ids"] + [tokenizer.pad_token_id]
    attention_mask = instruction["attention_mask"] + response["attention_mask"] + [1]  # 因为eos token咱们也是要关注的所以 补充为1
    labels = [-100] * len(instruction["input_ids"]) + response["input_ids"] + [tokenizer.pad_token_id]  
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

# * 配置训练参数
args = TrainingArguments(
    output_dir="./output/qwen1.8",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=1,
    logging_steps=10,
    num_train_epochs=3,
    save_steps=100,
    learning_rate=1e-4,
    save_on_each_node=True,
    gradient_checkpointing=False,
    fp16=False,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_id,
    data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, padding=True),
)

# * 模型训练
trainer.train()


