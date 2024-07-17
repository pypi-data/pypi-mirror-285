# -*- coding: utf-8 -*- #
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import json
import torch

# ------------------------------------------------------------------
from transformers import AutoModelForCausalLM, AutoTokenizer,BitsAndBytesConfig
from transformers.generation import GenerationConfig


quantization_config = BitsAndBytesConfig(
load_in_4bit=True,
bnb_4bit_compute_dtype=torch.float16
)
tokenizer = AutoTokenizer.from_pretrained("checkpoint-380", trust_remote_code=True)

model = AutoModelForCausalLM.from_pretrained(
    "/checkpoint-120",
    device_map="auto",
quantization_config=quantization_config,

    trust_remote_code=True
).eval()



pre=[]
true_=[]

json_res=[]

jsonresults={}
with open('est22.csv','r',encoding='gbk') as fw:
    lines = fw.readlines()
    for idx, line in enumerate(lines):
        if idx == 0:
            continue
        # if idx >10:
        #     break
        p_ = line.strip().split(',')

        # response, history = model.chat(tokenizer, "怎么获取免息 。 如何获取7天免息券。。 上述两句话表达的意思是否相同,如果意思相同则输出1，反之则输出0。", history=None)
        # tokern=f"{p_[1]}。{p_[2]} 。  上述两句话表达的意思是否相同,如果意思相同response则为1，如果意思不相同response则为0。"
        tokern=f"You are a helpful assistant. <|im_start|>user {p_[1]}。{p_[2]} "

        # tokern = f"{p_[1]},精简总结这句话"
        response, history = model.chat(tokenizer, tokern, history=None)
        print('response----',response)
        print('tokern----',tokern)

        jsonresults[p_[0]] = response

res_ = json.dumps(jsonresults, indent=4, ensure_ascii=False)

with open('result1_2.json', 'w', encoding='utf-8') as fw:
    fw.write(res_)
