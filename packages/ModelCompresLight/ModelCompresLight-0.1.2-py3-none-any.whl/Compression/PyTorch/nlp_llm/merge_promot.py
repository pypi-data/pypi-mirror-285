# -*- coding: utf-8 -*- #
from transformers import AutoModelForCausalLM, AutoTokenizer,BitsAndBytesConfig
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from transformers import TrainingArguments, Trainer
from torch.utils.data import Dataset
import transformers
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import torch
from transformers.trainer_pt_utils import LabelSmoother
IGNORE_TOKEN_ID = LabelSmoother.ignore_index
import json

quantization_config = BitsAndBytesConfig(
load_in_4bit=True,

bnb_4bit_compute_dtype=torch.float16
)
model = AutoModelForCausalLM.from_pretrained(""
                                             ,trust_remote_code=True
                                             # ,quantization_config=quantization_config
                                             )
tokenizer = AutoTokenizer.from_pretrained("",trust_remote_code=True,
                                          # padding_side="right",
padding=True,
                                          use_fast=False,
                                          )

tokenizer.eos_token = "<|endoftext|>"
tokenizer.pad_token = tokenizer.eos_token
# tokenizer.pad_token_id = tokenizer.eod_id


peft_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["c_attn", "c_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",   #SEQ_2_SEQ_LM  CAUSAL_LM
)
model = get_peft_model(model, peft_config)


model.print_trainable_parameters()
print(model)

def tokenize(prompt_in,prompt_out):
    result = tokenizer(
        prompt_in,
        truncation=True,
        max_length=256,
        padding="max_length",
        return_tensors=None,
    )
    result_out = tokenizer(
        prompt_out,
        truncation=True,
        max_length=256,
        padding="max_length",
        return_tensors=None,
    )

    result["labels"] = result_out["input_ids"].copy()

    return result



def preprocess(data_point):
    data_point=data_point[0]
    instruction = "对下面文本进行比较，意思表达相似输出1，不同输出0。\n"
    input_text = "文本1：" + data_point["sentence1"] + "\n文本2：" + data_point["sentence2"]
    input_text = "user: " + instruction + input_text
    input_text = input_text
    target_text = "assistant:" + str(data_point["label"])+"<|endoftext|>"
    # print("input_text:", input_text)
    # print("target_text:", target_text)
    tokenized_full_prompt = tokenize(input_text,target_text)
    return tokenized_full_prompt


class SupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""

    def __init__(self, raw_data, tokenizer: transformers.PreTrainedTokenizer, max_len: int):
        super(SupervisedDataset, self).__init__()


        sources = [example["conversations"] for example in raw_data]
        data_dict = preprocess(sources,)

        self.input_ids = data_dict["input_ids"]
        self.labels = data_dict["labels"]
        self.attention_mask = data_dict["attention_mask"]

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, i) :
        return dict(
            input_ids=self.input_ids[i],
            labels=torch.tensor(self.labels[i],dtype=torch.int64),
            attention_mask=self.attention_mask[i],
        )


class LazySupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""

    def __init__(self, raw_data, tokenizer: transformers.PreTrainedTokenizer, max_len: int):
        super(LazySupervisedDataset, self).__init__()
        self.tokenizer = tokenizer
        self.max_len = max_len


        self.tokenizer = tokenizer
        self.raw_data = raw_data
        self.cached_data_dict = {}

    def __len__(self):
        return len(self.raw_data)

    def __getitem__(self, i) :
        # if i in self.cached_data_dict:
        #     return self.cached_data_dict[i]

        ret = preprocess([self.raw_data[i]])
        # print(len(ret["attention_mask"]))
        # ret = dict(
        #     input_ids=ret["input_ids"],
        #     labels=torch.tensor(ret["labels"],dtype=torch.int64),
        #     attention_mask=ret["attention_mask"],
        # )
        # self.cached_data_dict[i] = ret

        return ret


train_json = json.load(open('in_jf.json', "r"))

train_dataset = LazySupervisedDataset(train_json, tokenizer=tokenizer, max_len=256)



training_args = TrainingArguments(
    per_device_train_batch_size=8,
    gradient_accumulation_steps=4,
    num_train_epochs=1,
    warmup_steps=10,
    max_steps=2000,
    learning_rate=1e-4,
    # fp16=True,
    logging_steps=1,
    output_dir="outputs/lora_20240717",
    optim="paged_adamw_8bit",
    save_strategy='steps',
    save_steps=50,
)


trainer = Trainer(
    model=model,
    # tokenizer=tokenizer,
    args=training_args,
    train_dataset=train_dataset,
    # eval_dataset=train_dataset,
)
trainer.train()


trainer.save_state()

trainer._save("fine-tuned-model")