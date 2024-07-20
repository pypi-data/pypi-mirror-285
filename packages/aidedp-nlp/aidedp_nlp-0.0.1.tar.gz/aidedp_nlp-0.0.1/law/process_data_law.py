import json
# 读取以.jsonl结尾的⽂件
json_data = []
with open('DISC-Law-SFT-Triplet-released.jsonl', 'r',encoding='utf-8') as file:
    for line in file:
        data = json.loads(line)
        json_data.append(data)
# 待填⼊的模板
template = []
# 遍历json数据集
for idx, data in enumerate(json_data):
    conversation = [
        {
            "from": "user",
            "value": data["input"]
        },
        {
            "from": "assistant",
            "value": data["output"]
        }
    ]
    template.append({"id": f"identity_{idx}","conversations": conversation})
# 输出模板中第三条数据（以索引2表⽰）的详细内容
print(json.dumps(template[2], ensure_ascii=False, indent=2))
# 将template写⼊到本地⽂件
output_file_path = "train_data_law.json"
with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(template, f, ensure_ascii=False, indent=2)
print(f"处理好的数据已写⼊到本地⽂件: {output_file_path}")