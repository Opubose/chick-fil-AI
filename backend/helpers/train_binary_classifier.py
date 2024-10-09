from datasets import load_dataset
import torch.backends
import torch.backends.mps
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
import torch

dataset = load_dataset('csv', data_files={'train': './backend/resources/api-resources/train_binary_classifier.csv', 'test': './backend/resources/api-resources/test_binary_classifier.csv'})

label_mapping = {"in_scope": 1, "out_of_scope": 0}
dataset = dataset.map(lambda example: {'label': label_mapping[example['label']]})

# Example data split into train/test
train_dataset = dataset['train']
test_dataset = dataset['test']

# Load the BERT tokenizer and model for binary classification
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

print("hi")
if torch.backends.mps.is_available():
    print("using m1 gpu")
    device = torch.device("mps")
else:
    print("using cpu")
    device = torch.device("cpu")
model.to(device)


# Tokenize the input text for the model
def tokenize_function(examples):
    return tokenizer(examples['text'], padding="max_length", truncation=True)

train_dataset = train_dataset.map(tokenize_function, batched=True)
test_dataset = test_dataset.map(tokenize_function, batched=True)

training_args = TrainingArguments(
    output_dir="./backend/resources/api-resources/model-logs",          # output directory
    evaluation_strategy="epoch",     # evaluate every epoch
    learning_rate=2e-5,              # learning rate
    per_device_train_batch_size=8,  # batch size for training
    per_device_eval_batch_size=16,   # batch size for evaluation
    num_train_epochs=3,              # number of epochs
    weight_decay=0.01,               # strength of weight decay
)

# Define the trainer
trainer = Trainer(
    model=model,                         # the model to train
    args=training_args,                  # training arguments
    train_dataset=train_dataset,         # training dataset
    eval_dataset=test_dataset            # evaluation dataset
)
print("training model")
# Fine-tune the model
trainer.train()

model.save_pretrained('./backend/resources/api-resources/models/scope_classifier')
tokenizer.save_pretrained('./backend/resources/api-resources/models/scope_classifier')