from datasets import load_dataset
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments

# Load the dataset from CSV files
dataset = load_dataset(
    'csv',
    data_files={
        'train': '/Users/AdityaKulkarni/Documents/UTD24-25/CS4485/chick-fil-AI/backend/resources/api-resources/train_binary_classifier.csv',
        'test': '/Users/AdityaKulkarni/Documents/UTD24-25/CS4485/chick-fil-AI/backend/resources/api-resources/test_binary_classifier.csv'
    }
)

# Example data split into train/test
train_dataset = dataset['train']
test_dataset = dataset['test']

# Preprocess labels (convert "in_scope" -> 1 and "out_of_scope" -> 0)
def preprocess_labels(examples):
    label_map = {"in_scope": 1, "out_of_scope": 0}
    
    # Map the string labels to integers
    examples["label"] = [label_map[label] for label in examples["label"]]
    
    return examples

# Apply label preprocessing to both the train and test datasets
train_dataset = train_dataset.map(preprocess_labels)
test_dataset = test_dataset.map(preprocess_labels)

# Load the BERT tokenizer and model for binary classification
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# Tokenize the input text for the model
def tokenize_function(examples):
    return tokenizer(examples['text'], padding="max_length", truncation=True)

# Apply tokenization to the train and test datasets
train_dataset = train_dataset.map(tokenize_function, batched=True)
test_dataset = test_dataset.map(tokenize_function, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="/Users/AdityaKulkarni/Documents/UTD24-25/CS4485/chick-fil-AI/backend/resources/api-resources/model-logs",  # output directory
    evaluation_strategy="epoch",     # evaluate every epoch
    learning_rate=2e-5,              # learning rate
    per_device_train_batch_size=16,  # batch size for training
    per_device_eval_batch_size=64,   # batch size for evaluation
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

# Print that the model is starting training
print("training model")

# Fine-tune the model
trainer.train()

# Save the trained model and tokenizer
model.save_pretrained('/Users/AdityaKulkarni/Documents/UTD24-25/CS4485/chick-fil-AI/backend/resources/api-resources/models/scope_classifier')
tokenizer.save_pretrained('/Users/AdityaKulkarni/Documents/UTD24-25/CS4485/chick-fil-AI/backend/resources/api-resources/models/scope_classifier')