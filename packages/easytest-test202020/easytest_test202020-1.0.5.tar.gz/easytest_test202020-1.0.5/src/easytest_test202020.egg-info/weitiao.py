# 大语言 微调
import torch
from peft import LoraConfig, get_peft_model
from transformers import TrainingArguments, AutoModelForCausalLM, AutoTokenizer
from datasets import Dataset
from trl import SFTTrainer
import json


with open('./data/alpaca_data_zh_51k.json','r',encoding='utf-8') as f:
#with open('./data/alpaca_data_val.json', 'r', encoding='utf-8') as f:
    train_dataset = json.loads(f.read())
with open('./data/alpaca_data_val.json','r',encoding='utf-8') as f:
    test_dataset = json.loads(f.read())


prompt = '''### input：{instruction}, {input}, \n### output:{output} </s>'''
##data = [{'text': 'xxxx'}, {'text': 'xxxx'}, {'text': 'xxxx'}, ...]
#{'text': ['Translate English to chinese:\nInput:good morning\noutput:早上好</s>', 'Translate English to chinese:\nInput:good morning\noutput:早上好</s>']}
train_dataset = [{'text':prompt.format(instruction=dic['instruction'], input=dic['input'], output=dic['output'])} for dic in train_dataset]
test_dataset = [{'text':prompt.format(instruction=dic['instruction'], input=dic['input'], output=dic['output'])} for dic in test_dataset]
#print(test_dataset)
train_dataset = Dataset.from_dict({key: [dic[key] for dic in train_dataset] for key in train_dataset[0]})
test_dataset = Dataset.from_dict({key: [dic[key] for dic in test_dataset] for key in test_dataset[0]})


# 配置lora参数

peft_config = LoraConfig(
    r=32,#r：更新矩阵的秩，也称为Lora注意力维度。较低的秩导致具有较少可训练参数的较小更新矩阵。增加r（不超过32）将导致更健壮的模型，但同时会导致更高的内存消耗
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"],
    bias="none",
    task_type="CAUSAL_LM",
)

output_dir = './'
training_aruments = TrainingArguments(
        output_dir=output_dir,# 模型输出的目录per_device_train_batch_size=64,
        optim='adamw_torch',
        learning_rate=10e-4,
        save_steps=200,
        logging_steps=20,
        group_by_length=False,
        num_train_epochs=1,# 训练的epoch数，和下面的max_steps二选-max_steps=200,
        gradient_accumulation_steps=1,
        gradient_checkpointing=True,
        max_grad_norm=0.3,
        bf16=True,
        lr_scheduler_type ='cosine',
        warmup_steps=100)

model_name = './chinese-llama-2-1.3b-hf'
model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,load_in_8bit=True,
                device_map='auto')
# model.gradient_checkpointing_enable()# 和下面的enable_input_require_grads()均可
model.enable_input_require_grads()
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()
model.config.use_cache = False
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token_id = 0
tokenizer.padding_side = 'right'

# get trainer
trainer = SFTTrainer(
    model = model,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    dataset_text_field="text",
    max_seq_length=512,
    tokenizer=tokenizer,
    args=training_aruments
    )

# train
trainer.train()

trainer.model.save_pretrained('./llama-2-7b-finetuned')
