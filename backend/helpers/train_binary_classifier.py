from datasets import load_dataset
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
import torch

# Check if GPU is available and print the GPU being used
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Training on: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")

# Load the dataset from CSV files
dataset = load_dataset(
    'csv',
    data_files={
        'train': '../resources/api-resources/train_binary_classifier.csv',
        'test': '../resources/api-resources/test_binary_classifier.csv'
    }
)

# Convert string labels to integers (e.g., "in_scope" → 1, "out_of_scope" → 0)
label_mapping = {"in_scope": 1, "out_of_scope": 0}
dataset = dataset.map(lambda example: {'label': label_mapping[example['label']]})

# Example data split into train/test
train_dataset = dataset['train']
test_dataset = dataset['test']

# Load the BERT tokenizer and model for binary classification
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# Move model to GPU if available
model.to(device)

# Tokenize the input text for the model
def tokenize_function(examples):
    return tokenizer(examples['text'], padding="max_length", truncation=True)

# Tokenize train and test datasets
train_dataset = train_dataset.map(tokenize_function, batched=True)
test_dataset = test_dataset.map(tokenize_function, batched=True)

# Set the format for PyTorch compatibility
train_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])
test_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])

# Define training arguments for GPU utilization
training_args = TrainingArguments(
    output_dir="../resources/model-logs",  # Output directory
    evaluation_strategy="epoch",           # Evaluate every epoch
    learning_rate=2e-5,                    # Learning rate
    per_device_train_batch_size=16,        # Batch size for training
    per_device_eval_batch_size=64,         # Batch size for evaluation
    num_train_epochs=3,                    # Number of epochs
    weight_decay=0.01,                     # Strength of weight decay
    logging_dir="../resources/logs",       # Directory for storing logs
    logging_steps=10,                      # Log every 10 steps
    report_to="none",                      # Disable reporting to online services like Weights & Biases
    fp16=True,                             # Enable mixed-precision training for faster performance
)

# Define the trainer
trainer = Trainer(
    model=model,                         # The model to train
    args=training_args,                  # Training arguments
    train_dataset=train_dataset,         # Training dataset
    eval_dataset=test_dataset            # Evaluation dataset
)

# Fine-tune the model
trainer.train()

# Save the fine-tuned model and tokenizer
model.save_pretrained('../resources/api-resources/models/scope_classifier')
tokenizer.save_pretrained('../resources/api-resources/models/scope_classifier')
