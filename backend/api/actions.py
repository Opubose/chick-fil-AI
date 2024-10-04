from transformers import pipeline
from sentence_transformers import SentenceTransformer
import spacy
import numpy as np
import response_generator

binary_model = "./backend/resources/api-resources/models/scope_classifier"
binary_model_tokenizer = "./backend/resources/api-resources/models/scope_classifier"
scope_classifier = pipeline("text-classification", model=binary_model)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
entity_nlp = spacy.load("en_core_web_sm")
llama_model = "meta-llama/Llama-2-7b-chat-hf"
#llm_nlp = pipeline("text-generation", model=llama_model)

INTENTS = {
    "order": "placing an order for food or drinks",
    "menu": "asking about the available menu items",
    "help": "asking for help with using the chatbot",
}

intent_embeddings_map = {intent: embedding_model.encode(description) for intent, description in INTENTS.items()}

def get_intent_and_entities(customer_message):
    #embedding of the customer's message
    customer_message_embedding = embedding_model.encode(customer_message)

    #ensure query is in scope
    #if not is_in_scope(customer_message):
    #    return {
    #        'intent': 'invalid',
    #        'entities': None
    #    }
    
    #get intent using cossim
    intent = detect_intent(customer_message_embedding)

    #get entities using spacy
    entities = extract_entities(customer_message)

    return {
        'intent': intent,
        'entities': entities
    }

#need to implement order low level intent detection
def order_handler(low_level_intent, entities):
    if low_level_intent == 'place':
        return response_generator.place_order(entities)
    elif low_level_intent == 'modify':
        return response_generator.modify_order(entities)
    elif low_level_intent == 'status':
        return response_generator.get_order_status()
    elif low_level_intent == 'cancel':
        return response_generator.cancel_order()
    elif low_level_intent == 'nutrition':
        return response_generator.get_order_info(entities)
    else:
        return "Error!"

#need to implement menu low level intent detection
def menu_handler(low_level_intent, entities):
    if low_level_intent == "entire_menu":
        return response_generator.list_entire_menu()
    elif low_level_intent == "dietary_restrictions":
        return response_generator.get_items_by_dietary_restriction(entities)
    elif low_level_intent == "ingredients":
        return response_generator.get_ingredients(entities)
    elif low_level_intent == "nutrition":
        return response_generator.get_nutritional_info(entities)
    else:
        return "Error!"

def get_help():
    return "Hi! I'm Chick-Fil-AI, a natural language processing powered chatbot created to help you handle ordering food at Chick-Fil-A.\nPlease let me know how I can assist you in one of the following areas: ordering related queries and menu related queries.\nUnfortunately, I'm unable to answer queries that are out of my domain knowledge, so please keep that in mind!"

#############################################################################
#############################################################################
######################      HELPER FUNCTIONS        #########################
#############################################################################
#############################################################################

def detect_intent(customer_message_embedding):
    #calculate vector similarity for each intent vs the customer message
    similarities = {intent: cosine_similarity(customer_message_embedding, intent_embedding)
                    for intent, intent_embedding in intent_embeddings_map.items()}
    
    #get the best one
    detected_intent = max(similarities, key=similarities.get)
    return detected_intent

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

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def is_in_scope(customer_message):
    result = scope_classifier(customer_message)
    print(result)
    return result[0]['label'] == 'LABEL_0'