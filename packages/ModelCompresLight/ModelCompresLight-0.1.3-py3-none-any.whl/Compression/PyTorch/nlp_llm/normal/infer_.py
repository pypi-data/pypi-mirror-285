# -*- coding: utf-8 -*- #
import torch
import json
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from torch.utils.data import Dataset, DataLoader


# 定义数据集类
class SentenceSimilarityDataset(Dataset):
    def __init__(self, data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        sentence1 = item["sentence1"]
        sentence2 = item["sentence2"]
        label = item["label"]
        id = item["id"]
        prompt = f"Human: 对下面文本进行比较，意思表达相同输出1，不同输出0。\n文本1：{sentence1}\n文本2：{sentence2}\n"
        return prompt, label, id


# 初始化模型和tokenizer
peft_model_path = "checkpoint-50"
config = PeftConfig.from_pretrained(peft_model_path)
inference_model = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path,trust_remote_code=True).to("cuda")
tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path,padding_side='left',trust_remote_code=True)
tokenizer.eos_token = "<|endoftext|>"
tokenizer.pad_token = tokenizer.eos_token
model = PeftModel.from_pretrained(inference_model, peft_model_path, trust_remote_code=True).to("cuda")

# 设置DataLoader
data_path = "test_jf.json"
batch_size = 1  # 根据您的硬件配置调整批处理大小
dataset = SentenceSimilarityDataset(data_path)
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

right_num = 0
num = 0

# 定义生成参数
generation_params = {
    "max_new_tokens": 5,
    "do_sample": False,
    "repetition_penalty": 1.3,

}

dic = {}
for prompts, labels, id in dataloader:
    print(prompts)
    generate_ids,history = model.chat(query=prompts[0],history=[],tokenizer=tokenizer)
    # 解码生成的文本
    print(generate_ids)
    # 处理生成的文本和标签
    for generated_text, label, id_num in zip(generate_ids, labels, id):
        try:
            generated_label = int(generated_text[-1])
        except ValueError:
            print("无法解析标签，跳过")
            generated_label = 1

        dic[id_num] = generated_label
        label = int(label)  # 假设生成文本格式为"Label: 0"
        print("生成标签：",generated_label, "实际标签：",label)
        if generated_label == label:
            right_num += 1

        num += 1
        print("正确数量", right_num,"\n总数", num)
with open("res.json", "w") as f:
    json.dump(dic, f)
print(f"Accuracy: {right_num / num}")