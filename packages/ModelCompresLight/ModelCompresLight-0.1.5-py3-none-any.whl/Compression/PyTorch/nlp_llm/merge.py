# -*- coding: utf-8 -*- #

from transformers import AutoModelForCausalLM,BitsAndBytesConfig
from peft import AutoPeftModelForCausalLM,AutoPeftModel,PeftModelForFeatureExtraction,AutoPeftModelForCausalLM

model = AutoPeftModelForCausalLM.from_pretrained(
    'ine-tuned-model', # path to the output directory
    device_map="auto",
    trust_remote_code=True
).eval()

merged_model = model.merge_and_unload()
# max_shard_size and safe serialization are not necessary.
# They respectively work for sharding checkpoint and save the model to safetensors
merged_model.save_pretrained('fine-tuned-model_merge', max_shard_size="2048MB", safe_serialization=True)
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(
    'fine-tuned-model', # path to the output directory
    trust_remote_code=True
)
tokenizer.save_pretrained('fine-tuned-model_merge')