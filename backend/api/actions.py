from transformers import pipeline
from sentence_transformers import SentenceTransformer
from huggingface_hub import login
import spacy
import numpy as np

# Step 1: Login to Hugging Face using the token
# Replace 'hf_YourGeneratedTokenHere123456789' with your actual Hugging Face token.
login("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")

# Use the absolute path to your saved model directory
trained_model_path = "../resources/api-resources/models/scope_classifier"

# Load your trained model and tokenizer using pipeline
scope_classifier = pipeline("text-classification", model=trained_model_path, tokenizer=trained_model_path)

# Load SentenceTransformer for intent detection
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load the LLaMA model with authentication using the token
# llm_model = "meta-llama/Llama-2-7b-chat-hf"
llm_model = "distilbert-base-uncased"

# Step 2: Pass `use_auth_token=True` for gated model access
llm_nlp = pipeline("text-classification", model=llm_model, use_auth_token=True)

# Load spaCy for entity extraction
entity_nlp = spacy.load("en_core_web_sm")

# Define intents and corresponding descriptions
INTENTS = {
    "order": "placing an order for food or drinks",
    "menu": "asking about the available menu items",
    "cancel": "request to cancel the current order",
    "status": "checking the status of the current order",
    "modify": "request to modify an existing order",
    "help": "asking for help with using the chatbot",
    "nutrition": "asking about the nutritional information of items"
}

# Create embeddings for each intent description using SentenceTransformer
intent_embeddings_map = {intent: embedding_model.encode(description) for intent, description in INTENTS.items()}

def get_intent_and_entities(customer_message):
    #embedding of the customer's message
    customer_message_embedding = embedding_model.encode(customer_message)

    #ensure query is in scope
    if not is_in_scope(customer_message):
        return {
            'intent': 'invalid',
            'entities': None
        }
    
    #get intent using cossim
    intent = detect_intent(customer_message_embedding)

    #get entities using spacy
    entities = extract_entities(customer_message)

    return {
        'intent': intent,
        'entities': entities
    }

'''
initial high level intent detection for:
order, menu, or help
'''
def detect_intent(customer_message_embedding):
    #calculate vector similarity for each intent vs the customer message
    similarities = {intent: cosine_similarity(customer_message_embedding, intent_embedding)
                    for intent, intent_embedding in intent_embeddings_map.items()}
    
    #get the best one
    detected_intent = max(similarities, key=similarities.get)
    return detected_intent

'''
low level intent detection for one of the following relating to orders: 
place, modify, get status, cancel, info
'''
def order_handler(low_level_intent, entities):
    if low_level_intent == 'place':
        return place_order(entities)
    elif low_level_intent == 'modify':
        return modify_order(entities)
    elif low_level_intent == 'status':
        return get_order_status()
    elif low_level_intent == 'cancel':
        return cancel_order()
    elif low_level_intent == 'nutrition':
        return get_order_info(entities)
    else:
        return "Invalid order intent."
    #for place: query database and add the items to an "order" --> need to think of how to handle an order. probably a seperate class called Order?
    #for modify: update order and requery database to update accordingly (different nutritonal, ingredient) information --> will be useful for menu related queries
    #for status: literally just return what the current order is
    #for cancel: just scrap the entire order and jsonify return ("Ok, I've cancelled your order")
    #for info: return the nutritional information (only main ones (calories, fat, carb, sugar, protein)) of the items currently in the order

def place_order(entities):
    pass
def modify_order(entities):
    pass
def get_order_info(entities):
    pass
def get_order_status():
    pass
def cancel_order():
    pass


'''
low level intent detection for one of the following relating to providing menu information: 
entire menu, dietary restrictions, ingredients, nutritional information
'''
def menu_handler():
    #for entire menu: list out every menu item (not nutrition or calorie or ingredients etc)
    #for dietary restrictions: query against a "vegan" or "vegetarian" tag (need to define intent scope for both of these (any other dietary restriction doesnt matter, dont worry about it for now)), and return all items that correspond to this tag
    #for ingredients of an item, return every single ingredient
    #for nutritional information of an item, return every single nutritional fact (calorie, saturated fat, trans fat, etc etc)
    pass

'''
simple message that tells what the bot can answer and an example of how to use it
'''
def get_help():
    return """Hi! I'm Chick-Fil-AI, a natural language processing powered chatbot 
    created to help you handle ordering food at Chick-Fil-A. Please let me know how I 
    can assist you in one of the following areas: ordering related queries and menu 
    related queries. Unfortunately, I'm unable to answer queries that are out of 
    my domain knowledge, so please keep that in mind!"""









#############################################################################
#############################################################################
######################      HELPER FUNCTIONS        #########################
#############################################################################
#############################################################################
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def extract_entities(customer_message):
    doc = entity_nlp(customer_message)
    entities = {
        'food_items': [],
        'modifiers': [],
        'quantities': [],
    }
    
    for ent in doc.ents:
        if ent.label_ in ["FOOD", "PRODUCT"]:
            entities['food_items'].append(ent.text)
        elif ent.label_ == "CARDINAL":
            entities['quantities'].append(ent.text)
        elif ent.label_ == "ADJ":
            entities['modifiers'].append(ent.text)
    
    return entities

def is_in_scope(customer_message):
    result = scope_classifier(customer_message)
    return result[0]['label'] == 'in_scope'