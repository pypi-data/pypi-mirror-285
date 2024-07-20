
#######加载模型
import torch
from transformers import LlamaTokenizer, LlamaForCausalLM
from peft import PeftModel

base_model_dir ='./chinese-llama-2-1.3b-hf'
lora_model_dir ='./llama-2-7b-finetuned'


tokenizer = LlamaTokenizer.from_pretrained(base_model_dir, trust_remote_code=True)
#先加载基座模型，再加入finetune后的参数
model = LlamaForCausalLM.from_pretrained(base_model_dir, device_map='auto', torch_dtype=torch.float16)
#model = PeftModel.from_pretrained(model, lora_model_dir)



test_prompt ='''下面是一个指示：我们如何在日常生活中减少用水?'''

input = tokenizer(test_prompt, return_tensors='pt')

input_ids = input["input_ids"].to("cpu")
model.eval()
with torch.no_grad():
    res = model.generate(input_ids,
    #do_sample = True,
    #temperature = 0.1,
    return_dict_in_generate=False,
    max_length=100)
    print(res.shape)
    print(tokenizer.decode(res[0],skip_special_tokens=True))

    # for i, output_sequence in enumerate(res.sequences):
    #     output_text = tokenizer.decode(output_sequence, skip_special_tokens=True)
    #     print(f"Generated sequence {i + 1}: {output_text}")
