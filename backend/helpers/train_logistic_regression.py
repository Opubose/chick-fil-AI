import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import re
import joblib  # For saving the model

# Load the dataset from a CSV file
df = pd.read_csv('./backend/resources/api-resources/customer_messages.csv')

# Function to clean text
def clean_text(text):
    """
    Cleans the input text by converting to lowercase,
    removing punctuation, and stripping extra spaces.
    """
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

# Clean the messages in the DataFrame
df['message'] = df['message'].apply(clean_text)

# Ensure that intents are properly categorized
df['intent'] = df['intent'].apply(lambda x: x if x in ['order_place', 'order_modify', 'order_status', 
                                                          'order_cancel', 'order_nutrition', 'menu_entire', 
                                                          'menu_dietary', 'menu_ingredients', 'menu_nutrition'] 
                                    else 'out_of_scope')

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df['message'], df['intent'], 
                                                    test_size=0.2, random_state=42)

# Create a pipeline for intent classification
pipeline_intent = Pipeline([
    ('vect', CountVectorizer()),         # Convert text to word counts
    ('tfidf', TfidfTransformer()),       # Convert counts to TF-IDF
    ('clf', LogisticRegression())        # Classifier
])

# Train the intent classifier
pipeline_intent.fit(X_train, y_train)

# Predict on test data
y_pred = pipeline_intent.predict(X_test)

# Print classification report to evaluate model performance
print("Intent Classification Report:")
print(classification_report(y_test, y_pred))

# Save the trained model to a file for future use
joblib.dump(pipeline_intent, './backend/resources/api-resources/models/intent_classifier.joblib')
print("Model saved to 'intent_classifier.joblib'")