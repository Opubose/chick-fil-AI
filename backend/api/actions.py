from dotenv import load_dotenv
import os
import spacy
import requests
from google.cloud import dialogflow_v2 as dialogflow
import response_generator
load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
#OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

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

def menu_dietary(entities):
    original_intent = "menu dietary information"
    database_information = response_generator.get_items_by_dietary_restriction(entities)

    return construct_output_response(original_intent, entities, database_information)

def menu_entire():
    original_intent = "entire menu information"
    database_information = response_generator.list_entire_menu()

    return construct_output_response(original_intent, "", database_information)

def menu_ingredients(entities):
    original_intent = "ingredients of a menu item"
    database_information = response_generator.get_ingredients(entities)

    return construct_output_response(original_intent, entities, database_information)

def menu_nutrition(entities):
    original_intent = "nutritional information of a menu item"
    database_information = response_generator.get_nutritional_info(entities)

    return construct_output_response(original_intent, entities, database_information)

def order_cancel(entities):
    original_intent = "cancelling an order"
    database_information = response_generator.cancel_order()

    return construct_output_response(original_intent, entities, database_information)

def order_modify(entities):
    original_intent = "modifying or changing an order"
    database_information = response_generator.modify_order(entities)

    return construct_output_response(original_intent, entities, database_information)

def order_nutrition(entities):
    original_intent = "getting the full nutritional information of the current order"
    database_information = response_generator.get_order_nutrition(entities)

    return construct_output_response(original_intent, entities, database_information)

def order_place(entities):
    original_intent = "placing an order"
    database_information = response_generator.place_order(entities)

    return construct_output_response(original_intent, entities, database_information)

def order_status():
    original_intent = "retrieving the current status of an order"
    database_information = response_generator.get_order_status()

    return construct_output_response(original_intent, "", database_information)

def construct_output_response(original_intent, extracted_entities, database_information):
    return database_information

'''
def construct_output_response(original_intent, entities, output_string):
    prompt = f"""You are a Chick-Fil-A AI chatbot assistant that helps users with their orders.
                The intent of the message is: "{original_intent}"
                The extracted entities are: {entities}
                The initial response generated is: "{output_string}"

                Please provide a corrected and user-friendly response based on the intent and entities, ensuring that the information is accurate and the response is well-formatted in plain text. Do not use markdown or anything like that.
                Be somewhat concise as well, don't talk TOO much but talk enough to be friendly and nice. Also, if there's something very weird in the initial response, you are good to get rid of it ONLY if you evaluate and make sure it doesn't make sense/fit into the context.
                For instance, if the initial response is "Sorry, we couldn't find 'sure' on the menu., and Added large fries to your order with quantity 1 at $2.95 each. Your order has been updated.", obviously 'sure' isn't a menu item. You can completely disregard it in the response, and only say that large fries were added.
                Also, do not "remember" things that are not relevant to the immediate query. If you know the full nutritonal information of an item, but the customer specifically asks for the calories (from the initial response), you will not list the entire nutrition, only the calories or whatever small part.
                Do not include starting or ending sentences such as "Sure! Here's a corrected output...". This is strictly only for constructing an AI chatbot that repsond to users.
            """

    # Prepare the API request
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    # Choose the model you want to use
    # For example, to use Llama 2:
    model = "meta-llama/llama-3.2-3b-instruct:free"

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150,
        "temperature": 0.7,
        "top_p": 0.9
    }
    print(output_string)
    # Make the API request
    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"OpenRouter API request failed with status code {response.status_code}: {response.text}")

    response_data = response.json()

    # Extract the assistant's reply
    corrected_response = response_data['choices'][0]['message']['content'].strip()

    return corrected_response
'''