# 1 基础环境搭建 - 文本生成
# conda create -n qwen python==3.10
# conda activate qwen

# 2 Qwen环境搭建
# pip install torch torchvision torchaudio
# pip install -r requirements.txt

# 查看数据集 xxx.jsonl
# head -n 1 xxx.jsonl
'''
qwen数据集所需格式
[
  {
    "id": "identity_0",
    "conversations": [
      {
        "from": "user",
        "value": "你好"
      },
      {
        "from": "assistant",
        "value": "我是一个语言模型，我叫通义千问。"
      }
    ]
  }
]
'''

# 转换数据 python process_data_law.py

# 3 微调安装依赖
# pip install "peft<0.8.0" deepspeed

# 4 启动微调
# 查看并修改./finetune/finetune_lora_single_gpu.sh⽂件
'''
    MODEL="模型地址"
    DATA="数据地址"
    python finetune.py \
    --model_name_or_path $MODEL \ # 模型的名称或路径，环境变量 MODEL 应包含具体的模型路径或标识
    --data_path $DATA \ # 数据路径，环境变量 DATA 应包含⽤于训练和评估的数据⽂件的路径
    --bf16 True \ # 使⽤ BF16 混合精度训练，可以提⾼训练速度并减少内存使⽤
    --output_dir output_qwen \ # 输出⽬录，⽤于存放训练后的模型和⽇志
    --num_train_epochs 5 \ # 训练的轮数
    --per_device_train_batch_size 4 \ # 每个设备的训练批次⼤⼩
    --per_device_eval_batch_size 1 \ # 每个设备的评估批次⼤⼩
    --gradient_accumulation_steps 8 \ # 梯度累积步数，⽤于在较⼩的批次上模拟较⼤批次的训练效果
    --evaluation_strategy "no" \ # 评估策略，这⾥设置为 "no" 表⽰不在训练过程中进⾏评估
    --save_strategy "steps" \ # 模型保存策略，这⾥设置为“steps" 表⽰每经过⼀定步数保存⼀次模型
    --save_steps 100 \ # 每 100 步保存模型⼀次
    --save_total_limit 10 \ # 最多保存 10 个训练过程中的模型
    --learning_rate 3e-4 \ # 学习率
    --weight_decay 0.1 \ # 权重衰减，⽤于防⽌过拟合
    --adam_beta2 0.95 \ # Adam 优化器的 beta2 参数
    --warmup_ratio 0.01 \ # 预热⽐例，初始训练阶段逐渐增加学习率
    --lr_scheduler_type "cosine" \ # 学习率调度器类型，这⾥使⽤余弦退⽕调度
    --logging_steps 1 \ # 每 1 步记录⼀次⽇志
    --report_to "none" \ # 报告⽅式，这⾥设置为 "none"不向任何外部服务报告
    --model_max_length 512 \ # 模型的最⼤输⼊⻓度
    --lazy_preprocess True \ # 延迟预处理，将数据预处理延迟到实际需要时进⾏，节约内存使⽤
    --gradient_checkpointing \ # 开启梯度检查点，减少内存使⽤但可能影响速度
    --use_lora # 开启 LORA 微调，通过低秩适配改进模型的参数
'''

# 执行微调 bash ./finetune/finetune_lora_single_gpu.sh

# 5 合并模型 python qwen_lora_merge.py

