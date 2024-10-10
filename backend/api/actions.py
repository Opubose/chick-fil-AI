from dotenv import load_dotenv
import os
import spacy
from google.cloud import dialogflow_v2 as dialogflow
from google.protobuf.json_format import MessageToDict
import response_generator
load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./dialogflow-credentials.json"

entity_nlp = spacy.load("en_core_web_sm")
model = "meta-llama/llama-3.2-3b-instruct:free"

def get_intent_and_entities(customer_message):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path('chickfilai-bot-tyen', 'session1')

    text_input = dialogflow.types.TextInput(text=customer_message, language_code='en')
    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(session=session, query_input=query_input)
    
    intent = response.query_result.intent.display_name
    entities = {}
    
    for entity in response.query_result.parameters:
        entities[entity] = response.query_result.parameters[entity]
    
    print("Intent:", intent)
    print("Extracted Entities:", entities)
    return {
        'intent': intent,
        'entities': entities
    }

def extract_entities(entities):
    extracted_entities = {
        'food_items': [],
        'modifiers': [],
        'quantities': [],
        'properties': []
    }

    for key, value in entities.items():
        if key == "food_items":
            extracted_entities['food_items'].append(value)
        elif key == "modifiers":
            extracted_entities['modifiers'].append(value)
        elif key == "quantities":
            extracted_entities['quantities'].append(value)
        elif key == "properties":
            extracted_entities['properties'].append(value)

    return extracted_entities

def menu_dietary(entities):
    # original_intent = "menu dietary information"
    # extracted_entities = extract_entities(entities)
    # database_information = response_generator.get_items_by_dietary_restriction(entities)

    # return construct_output_response(original_intent, extracted_entities, database_information)
    return "menu dietary"

def menu_entire():
    # original_intent = "entire menu information"
    # extracted_entities = extract_entities(entities)
    # database_information = response_generator.list_entire_menu()

    # return construct_output_response(original_intent, extracted_entities, database_information)
    return "menu entire"

def menu_ingredients(entities):
    # original_intent = "ingredients of a menu item"
    # extracted_entities = extract_entities(entities)
    # database_information = response_generator.get_ingredients(entities)

    # return construct_output_response(original_intent, extracted_entities, database_information)
    return "menu ingredients"

def menu_nutrition(entities):
    # original_intent = "nutritional information of a menu item"
    # extracted_entities = extract_entities(entities)
    # database_information = response_generator.get_nutritional_info(entities)

    # return construct_output_response(original_intent, extracted_entities, database_information)
    return "menu nutrition"

def order_cancel(entities):
    original_intent = "cancelling an order"
    extracted_entities = extract_entities(entities)
    database_information = response_generator.cancel_order()

    return construct_output_response(original_intent, extracted_entities, database_information)

def order_modify(entities):
    original_intent = "modifying or changing an order"
    extracted_entities = extract_entities(entities)
    database_information = response_generator.modify_order(entities)

    return construct_output_response(original_intent, extracted_entities, database_information)

def order_nutrition(entities):
    original_intent = "getting the full nutritional information of the current order"
    extracted_entities = extract_entities(entities)
    database_information = response_generator.get_order_nutrition(entities)

    return construct_output_response(original_intent, extracted_entities, database_information)

def order_place(entities):
    original_intent = "placing an order"
    extracted_entities = extract_entities(entities)
    database_information = response_generator.place_order(entities)

    return construct_output_response(original_intent, extracted_entities, database_information)

def order_status():
    original_intent = "retrieving the current status of an order"
    database_information = response_generator.get_order_status()

    return construct_output_response(original_intent, [], database_information)

def construct_output_response(original_intent, extracted_entities, database_information):
    return database_information

# def construct_output_response(original_intent, extracted_entities, database_information):
#     pass
#     ''' TODO ADITYA
#     use client
#     '''