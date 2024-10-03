from transformers import pipeline
from sentence_transformers import SentenceTransformer
import spacy
import numpy as np

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
llm_model = "meta-llama/Llama-2-7b-chat-hf"
llm_nlp = pipeline("text-classification", model=llm_model)
entity_nlp = spacy.load("en_core_web_sm")

INTENTS = {
    "order": "placing an order for food or drinks",
    "menu": "asking about the available menu items",
    "cancel": "request to cancel the current order",
    "status": "checking the status of the current order",
    "modify": "request to modify an existing order",
    "help": "asking for help with using the chatbot",
    "nutrition": "asking about the nutritional information of items"
}

intent_embeddings = {intent: embedding_model.encode(description) for intent, description in INTENTS.items()}

def generate_response(customer_message):
    #embedding of the customer's message
    customer_message_embedding = embedding_model.encode(customer_message)

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
    # Calculate cosine similarity between user input and each predefined intent
    similarities = {intent: cosine_similarity(customer_message_embedding, intent_embedding) 
                    for intent, intent_embedding in intent_embeddings.items()}
    
    # Get the intent with the highest similarity score
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
    pass

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
    #just jsonify return "Hi, I'm Chick-Fil-AI" ill do the rest later
    pass



def cosine_similarity(vec1, vec2):
    # Cosine similarity between two vectors
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