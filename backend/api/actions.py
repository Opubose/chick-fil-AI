from openai import OpenAI
from dotenv import load_dotenv
import os
import spacy
import dialogflow_v2 as dialogflow
from google.protobuf.json_format import MessageToDict
import response_generator
load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
DIALOGFLOW_PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

entity_nlp = spacy.load("en_core_web_sm")
client = OpenAI(
    base_url=os.getenv("OR_BASE_URL"),
    api_key=os.getenv("OR_API_KEY")
)
model = "meta-llama/llama-3.2-3b-instruct:free"


def get_intent_and_entities(customer_message):
    #get intent using dialogflow
    ''' TODO
    intent = get_intent(customer_message)
    '''

    #get entities using spacy
    entities = extract_entities(customer_message)

    return {
        'intent': "intent", #replace with intent
        'entities': entities
    }

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

def menu_dietary(entities):
    original_intent = "menu dietary information"
    extracted_entities = extract_entities(entities)
    database_information = response_generator.get_items_by_dietary_restriction(entities)

    return construct_output_response(original_intent, extracted_entities, database_information)

def menu_entire(entities):
    original_intent = "entire menu information"
    extracted_entities = extract_entities(entities)
    database_information = response_generator.get_items_by_dietary_restriction(entities)

    return construct_output_response(original_intent, extracted_entities, database_information)

def menu_ingredients(entities):
    original_intent = "ingredients of a menu item"
    extracted_entities = extract_entities(entities)
    database_information = response_generator.get_items_by_dietary_restriction(entities)

    return construct_output_response(original_intent, extracted_entities, database_information)

def menu_nutrition(entities):
    original_intent = "nutritional information of a menu item"
    extracted_entities = extract_entities(entities)
    database_information = response_generator.get_items_by_dietary_restriction(entities)

    return construct_output_response(original_intent, extracted_entities, database_information)

def order_cancel(entities):
    original_intent = "cancelling an order"
    extracted_entities = extract_entities(entities)
    database_information = response_generator.get_items_by_dietary_restriction(entities)

    return construct_output_response(original_intent, extracted_entities, database_information)

def order_modify(entities):
    original_intent = "modifying or changing an order"
    extracted_entities = extract_entities(entities)
    database_information = response_generator.get_items_by_dietary_restriction(entities)

    return construct_output_response(original_intent, extracted_entities, database_information)

def order_nutrition(entities):
    original_intent = "getting the full nutritional information of the current order"
    extracted_entities = extract_entities(entities)
    database_information = response_generator.get_items_by_dietary_restriction(entities)

    return construct_output_response(original_intent, extracted_entities, database_information)

def order_place(entities):
    original_intent = "placing an order"
    extracted_entities = extract_entities(entities)
    database_information = response_generator.get_items_by_dietary_restriction(entities)

    return construct_output_response(original_intent, extracted_entities, database_information)

def order_status(entities):
    original_intent = "retrieving the current status of an order"
    extracted_entities = extract_entities(entities)
    database_information = response_generator.get_items_by_dietary_restriction(entities)

    return construct_output_response(original_intent, extracted_entities, database_information)

def construct_output_response(original_intent, extracted_entities, database_information):

    pass
    ''' TODO ADITYA
    '''