from transformers import pipeline
from sentence_transformers import SentenceTransformer
import spacy
import numpy as np
import boto3 as boto
from order import Order

binary_model = "/backend/resources/api-resources/models/scope_classifier"
binary_model_tokenizer = "/backend/resources/api-resources/models/scope_classifier"
scope_classifier = pipeline("text-classification", model=binary_model)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
llm_model = "meta-llama/Llama-2-7b-chat-hf"
llm_nlp = pipeline("text-classification", model=llm_model)
entity_nlp = spacy.load("en_core_web_sm")
dynamodb = boto.resource('dynamodb', 
                        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
                        region_name='us-east-1')
menu = dynamodb.Table('CFA-Data')
order = Order()

INTENTS = {
    "order": "placing an order for food or drinks",
    "menu": "asking about the available menu items",
    "cancel": "request to cancel the current order",
    "status": "checking the status of the current order",
    "modify": "request to modify an existing order",
    "help": "asking for help with using the chatbot",
    "nutrition": "asking about the nutritional information of items"
}

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
    global order
    food_items = entities['food_items']
    if not food_items:
        return "No food items were found in your order."

    modifiers = entities['modifiers']
    quantities = entities['quantities']

    items_added = []

    for i, food_item in enumerate(food_items):
        quantity = quantities[i] if i < len(quantities) else 1
        db_response = table.get_item(Key={'Item': food_item})

        if "Item" in db_response:
            matched_item = db_response['Item']
            order.add_item(matched_item['Item'], quantity=quantity)
            items_added.append(f"{quantity} {matched_item['Item']}")
        else:
            return f"Sorry. we don't have an item called {food_item} on the menu."
    
    total_price = order.get_total_price(menu)

    if items_added:
        if len(items_added) == 1:
            order_str = items_added[0]
        else:
            order_str = ', '.join(items_added[:-1]) + f", and {items_added[-1]}"
        return f"{item_string} have been added to your order. The total will be ${total_price:.2f}."
    else:
        return "No items were added to your order"


def modify_order(entities):
    global order
    food_items = entities['food_items']
    quantities = entities['quantities']

    if not food_items:
        return "No food items were found to modify in your order."
    
    modified_items = []

    for i, food_item in enumerate(food_items):
        quantity = quantities[i] if i < len(quantities) else 1

        response = table.get_item(Key={'Item': food_item})

        if 'Item' in response:
            matched_item = response['Item']
            
            if quantity == 0:
                order.remove_item(matched_item['Item'])
                modified_items.append(f"Removed {matched_item['Item']} from your order")
            else:
                order.modify_item(matched_item['Item'], quantity)
                modified_items.append(f"Updated {matched_item['Item']} to {quantity} in your order")
        else:
            # Handle case when item is not found in the menu
            return f"Sorry, we couldn't find '{food_item}' on the menu."
    
    if modified_items:
        modified_string = ', '.join(modified_items[:-1]) + f", and {modified_items[-1]}" if len(modified_items) > 1 else modified_items[0]
        return f"{modified_string}. Your order has been updated."
    else:
        return "No changes were made to your order."


def get_order_info(entities):
    global order

    if not order.get_total_items():
        return "You don't have anything in your order yet."
    
    nutritional_info = {}

    for item, quantity in order.get_total_items().items():
        response = table.get_item(Key={'Item': item})

        if 'Item' in response:
            menu_item = response['Item']

            nutritional_info[item] = {
                'Calories': menu_item['Calories'] * quantity,
                'Fat': menu_item['Fat'] * quantity,
                'Carbohydrates': menu_item['Carbohydrates'] * quantity,
                'Sugar': menu_item['Sugar'] * quantity,
                'Protein': menu_item['Protein'] * quantity,
            }
        else:
            return f"Sorry, we couldn't find nutritional information for '{item}'."
    
    summary_lines = []
    for item, info in nutritional_info.items():
        summary_lines.append(
            f"{item}: {info['Calories']} calories, {info['Fat']}g fat, "
            f"{info['Carbohydrates']}g carbohydrates, {info['Sugar']}g sugar, "
            f"{info['Protein']}g protein."
        )
    return "\n".join(summary_lines)


def get_order_status():
    global order

    if not order.get_total_items():
        return "Your order is currently empty."
    
    order_items = order.get_total_items()
    order_details = []

    for item, quantity in order_items.items():
        order_details.append(f"{quantity}x {item}")

    # Join all items into a single string
    order_summary = ", ".join(order_details)

    return f"Your current order is {order_summary}."


def cancel_order():
    global order

    order.clear_order()

    return "Okay, I have canceled your order."


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