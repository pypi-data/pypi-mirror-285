from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset

# 加载数据集
imdb_dataset = load_dataset('imdb')

# 加载本地预训练模型和分词器
model_path = "/path/to/local/llama-2b"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path, num_labels=2)


# 数据预处理
def preprocess_function(examples):
    return tokenizer(examples['text'], truncation=True, padding='max_length')


encoded_imdb = imdb_dataset.map(preprocess_function, batched=True)

# 训练设置
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy='epoch',
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=encoded_imdb['train'],
    eval_dataset=encoded_imdb['test'],
    tokenizer=tokenizer,
)

# 开始训练
trainer.train()

# 评估模型
trainer.evaluate()
