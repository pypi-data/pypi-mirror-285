import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset
from sklearn.metrics import accuracy_score
from peft import PeftModel
from peft import LoraConfig, TaskType, get_peft_model

test_dataset = load_dataset('json', data_files="/root/codes/self-llm/Qwen1.5/qa_test.jsonl", split='train')

config = LoraConfig(
    task_type=TaskType.CAUSAL_LM, 
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    inference_mode=False, # 训练模式
    r=8, # Lora 秩
    lora_alpha=32, # Lora alaph，具体作用参见 Lora 原理
    lora_dropout=0.1# Dropout 比例
)

model_path = '/root/models/qwen1.5-1.8b'
lora_path = '/root/codes/self-llm/Qwen1.5/output/Qwen1.5/checkpoint-687'


# 加载tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_path)

# 加载模型
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto",torch_dtype=torch.float16)

# 加载lora权重
model = PeftModel.from_pretrained(model, model_id=lora_path, config=config)

# 设置模型为评估模式
model.eval()


results = []

for question in test_dataset:
    sentence = question['input']
    system_prompt = "你是一名专业的语言学家，判断以下两句话是否表达相同的意思：请注意：如果两句话意思相同，请输出'1',如果意思不同请输出'0'，只要输出数字，不要输出任何其他内容。尤其不要输出'是'、'否'这样的汉字，完全输出数字。"
    
    messages = [
    {"role": "system", "content": f"system_prompt"},
    {"role": "user", "content": system_prompt + sentence}
    ]
    
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    model_inputs = tokenizer([text], return_tensors="pt")

    generated_ids = model.generate(
        model_inputs.input_ids.cuda(),
        max_new_tokens=10
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    results.append({
        "sentence": sentence,
        "labels": question['output'],
        "prediction": response
    })


import json
file_path = "./results.jsonl"
with open(file_path, 'w', encoding='utf-8') as file:
    for entry in results:
        json.dump(entry, file, ensure_ascii=False)
        file.write('\n')


rights = []
fault = []
for ele in results:
    pre = ele['prediction']
    label = ele['labels']
    
    if pre == label:
        rights.append({
            "sentence": ele['sentence'],
            "right": "yes"
        })

    else:
        fault.append(
            {
                "label": label,
                "prediction": pre
            }
        )
        
print(f"正确率为{len(rights)/len(results)}")