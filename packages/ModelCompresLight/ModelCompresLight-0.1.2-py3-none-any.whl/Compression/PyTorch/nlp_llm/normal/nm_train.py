# -*- coding: utf-8 -*- #
import torch
import transformers
from datasets import load_dataset, load_from_disk
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig,AutoModelForSeq2SeqLM
import bitsandbytes as bnb
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "1"
device = "cuda:0"  # the value needs to be a device name (e.g. cpu, cuda:0) or 'auto', 'balanced', 'balanced_low_0', 'sequential'
model_path = 'model'

CUTOFF_LEN = 256

def tokenize(prompt_in,prompt_out):
    result = tokenizer(
        prompt_in,
        truncation=True,
        max_length=CUTOFF_LEN,
        padding="max_length",
        return_tensors=None,
    )
    result_out = tokenizer(
        prompt_out,
        truncation=True,
        max_length=CUTOFF_LEN,
        padding="max_length",
        return_tensors=None,
    )

    result["labels"] = result_out["input_ids"].copy()

    return result


def generate_and_tokenize_prompt(data_point):
    instruction = "对下面文本进行比较，意思表达相似输出1，不同输出0。\n"
    input_text = "文本1：" + data_point["sentence1"] + "\n文本2：" + data_point["sentence2"]
    input_text = "user: " + instruction + input_text
    input_text = input_text
    target_text = "assistant:" + str(data_point["label"])+"<|endoftext|>"
    print("input_text:", input_text)
    print("target_text:", target_text)
    tokenized_full_prompt = tokenize(input_text,target_text)
    return tokenized_full_prompt

###int4量化配置
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,  # 或者 load_in_8bit=True，根据需要设置
    llm_int8_enable_fp32_cpu_offload=True,
    bnb_4bit_compute_dtype=torch.float16,  # 虽然我们以4位加载和存储模型，但我们在需要时会部分反量化他，并以16位精度进行计算
    bnb_4bit_quant_type="nf4",  # nf量化类型
    bnb_4bit_use_double_quant=True,  # 双重量化，量化一次后再量化，进一步解决显存
)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map=device, trust_remote_code=True,
                                             torch_dtype=torch.float16, quantization_config=quantization_config)
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True, use_fast=False,)
tokenizer.eos_token = "<|endoftext|>"
tokenizer.pad_token = tokenizer.eos_token

print(model)
model = prepare_model_for_kbit_training(model)

config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["c_attn","c_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"   # #SEQ_2_SEQ_LM  CAUSAL_LM
)



model = get_peft_model(model, config)
dataset = load_dataset('json', data_files={'train': 'jf.json'})  # 请替换为您的数据集脚本

dataset = dataset.map(generate_and_tokenize_prompt,
                      remove_columns=["sentence1", "sentence2", "label"])
print(dataset)

trainer = transformers.Trainer(
    model=model,
    train_dataset=dataset["train"],
    args=transformers.TrainingArguments(
        per_device_train_batch_size=8,
        gradient_accumulation_steps=4,
        num_train_epochs=1,
        warmup_steps=10,
        max_steps=2000,
        learning_rate=1e-4,
        fp16=True,
        logging_steps=1,
        output_dir="outputs/qlora_test20240717",
        optim="paged_adamw_8bit",
        save_strategy='steps',
        save_steps=20,
    ),
    data_collator=transformers.DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

model.config.use_cache = False  # silence the warnings. Please re-enable for inference!
trainer.train()

trainer.save_model(trainer.args.output_dir)
