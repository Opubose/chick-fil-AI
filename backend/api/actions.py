from transformers import pipeline
from sentence_transformers import SentenceTransformer
import spacy
import boto3
import numpy as np

from response_generator import menu

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
def menu_handler(low_level_intent, entities):
    #for entire menu: list out every menu item (not nutrition or calorie or ingredients etc)
    #for dietary restrictions: query against a "vegan" or "vegetarian" tag (need to define intent scope for both of these (any other dietary restriction doesnt matter, dont worry about it for now)), and return all items that correspond to this tag
    #for ingredients of an item, return every single ingredient
    #for nutritional information of an item, return every single nutritional fact (calorie, saturated fat, trans fat, etc etc)
    if low_level_intent == "entire_menu":
        return list_entire_menu()
    elif low_level_intent == "dietary_restrictions":
        return get_items_by_dietary_restriction(entities)
    elif low_level_intent == "ingredients":
        return get_ingredients(entities)
    elif low_level_intent == "nutrition":
        return get_nutritional_info(entities)
    else:
        return "Invalid menu intent."


def list_entire_menu():
    try:
        response = menu.scan()
        items = response.get('Items', [])
        menu_items = [item['Item_index'] for item in items]
        return {"menu_items": menu_items}
    except Exception as e:
        return {"error": str(e)}


def get_items_by_dietary_restriction(entities): # doesnt work
    if entities and 'modifiers' in entities:
        restriction = entities['modifiers'][0].lower()
    else:
        return "Please specify a dietary restriction (e.g., vegetarian, vegan)."

    try:
        if restriction == "vegan":
            response = menu.scan(
                FilterExpression="Vegan_Index = :v",
                ExpressionAttributeValues={":v": 1}
            )
        elif restriction == "vegetarian":
            response = menu.scan(
                FilterExpression="Vegetarian_Index = :v",
                ExpressionAttributeValues={":v": 1}
            )
        else:
            return "Currently, we only support 'vegan' and 'vegetarian' dietary restrictions."

        items = response.get('Items', [])
        matching_items = [item['Item_index'] for item in items]
        
        if not matching_items:
            return f"No items found for dietary restriction: {restriction}."
        
        return {"items_matching_dietary_restriction": matching_items}
    
    except Exception as e:
        return {"error": str(e)}


def get_ingredients(entities):
    if entities and 'food_items' in entities:
        food_item = entities['food_items'][0]
    else:
        return "Please specify a food item."

    try:
        response = menu.get_item(
            Key={'Item': food_item}
        )

        if 'Item' not in response:
            return f"No item found with the name: {food_item}."

        item = response['Item']
        ingredients = item.get('Ingredients', "No ingredients found for this item.")
        
        return {"food_item": food_item, "ingredients": ingredients}

    except Exception as e:
        return {"error": str(e)}


def get_nutritional_info(entities):
    if entities and 'food_items' in entities:
        food_item = entities['food_items'][0]
    else:
        return "Please specify a food item."

    try:
        response = menu.get_item(
            Key={'Item': food_item}
        )

        if 'Item' not in response:
            return f"No item found with the name: {food_item}."

        item = response['Item']

        nutritional_info = {
            "Serving_size": item.get("Serving_size", "No serving size found."),
            "Calories": item.get("Calories", "No calorie information found."),
            "Fat": item.get("Fat", "No fat information found."),
            "Sat_Fat": item.get("Sat_Fat", "No saturated fat information found."),
            "Trans_Fat": item.get("Trans_Fat", "No trans fat information found."),
            "Cholesterol": item.get("Cholesterol", "No cholesterol information found."),
            "Sodium": item.get("Sodium", "No sodium information found."),
            "Carbohydrates": item.get("Carbohydrates", "No carbohydrate information found."),
            "Fiber": item.get("Fiber", "No fiber information found."),
            "Sugar": item.get("Sugar", "No sugar information found."),
            "Protein": item.get("Protein", "No protein information found.")
        }
        
        return {"food_item": food_item, "nutritional_info": nutritional_info}

    except Exception as e:
        return {"error": str(e)}





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