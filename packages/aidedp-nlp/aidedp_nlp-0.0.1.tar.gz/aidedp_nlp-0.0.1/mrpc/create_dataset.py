import jsonlines
import pandas as pd

# 定义文件路径
train_file = "/root/dataset/train.jsonl"
test_file = "/root/dataset/test.jsonl"

output_train_file = './qa_train.jsonl'
output_test_file = './qa_test.jsonl'

# 加载jsonl文件
def load_jsonl(file_path):
    data = []
    with jsonlines.open(file_path) as reader:
        for obj in reader:
            data.append(obj)
    return pd.DataFrame(data)

# 加载训练集和测试集
train_data = load_jsonl(train_file)
test_data = load_jsonl(test_file)

# 将数据转换为需要的格式
def convert_to_qa_format(data):
    qa_data = []

    for _, row in data.iterrows():
        sentence1 = row['text1']
        sentence2 = row['text2']
        label = row['label']
        
        instruction = "你是一名专业的语言学家，请你判断以下两句话是否表达相同的意思：请注意：1. 你是需要回答‘1’或者‘0’，不要有任何多余的输出。'1'代表意思相同,‘0’代表意思不同。2. 你的回答应该尽可能准确。"
        input_text = f"句子1: {sentence1}\n句子2: {sentence2}"
        output_text = "1" if label == 1 else "0"
        
        qa_data.append({
            "instruction": instruction,
            "input": input_text,
            "output": output_text
        })
    
    return qa_data

# 转换训练集和测试集
qa_train = convert_to_qa_format(train_data)
qa_test = convert_to_qa_format(test_data)

# 将转换后的数据保存为jsonl文件
def save_to_jsonl(data, file_path):
    with jsonlines.open(file_path, mode='w') as writer:
        writer.write_all(data)

save_to_jsonl(qa_train, output_train_file)
save_to_jsonl(qa_test, output_test_file)

# 打印转换后的部分训练集数据
print(qa_train[:1])
# 打印转换后的部分测试集数据
print(qa_test[:1])