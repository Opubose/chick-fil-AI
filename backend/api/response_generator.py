import boto3
import os
import re
from order import Order
from dotenv import load_dotenv
load_dotenv()

dynamodb = boto3.resource('dynamodb', 
                        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
                        region_name='us-east-1')
menu = dynamodb.Table('CFA-Data')
order = Order()
    
def modify_order(entities):
    food_items = entities['food_items']
    quantities = entities['quantities']
    
    if not food_items:
        return "No food items were found to modify in your order."

    modified_items = []

    # If there are two food items: remove the first and add the second
    if len(food_items) == 2:
        food_item_to_remove = food_items[0]
        food_item_to_add = food_items[1]
        quantity_to_add = quantities[1] if len(quantities) > 1 else 1
        
        # Remove the first item
        response_remove = menu.get_item(Key={'Item': food_item_to_remove})
        if 'Item' in response_remove:
            matched_item_remove = response_remove['Item']
            price_remove = float(matched_item_remove['Price'])
            order.remove_item(food_item_to_remove, price_remove)
            modified_items.append(f"Removed {food_item_to_remove} from your order.")
        else:
            modified_items.append(f"Sorry, we couldn't find '{food_item_to_remove}' on the menu to remove.")

        # Add the second item
        response_add = menu.get_item(Key={'Item': food_item_to_add})
        if 'Item' in response_add:
            matched_item_add = response_add['Item']
            price_add = float(matched_item_add['Price'])
            order.add_item(food_item_to_add, price_add, quantity_to_add)
            modified_items.append(f"Added {food_item_to_add} to your order with quantity {quantity_to_add}.")
        else:
            modified_items.append(f"Sorry, we couldn't find '{food_item_to_add}' on the menu to add.")

    # If only one item: remove it from the order
    elif len(food_items) == 1:
        food_item_to_remove = food_items[0]
        response = menu.get_item(Key={'Item': food_item_to_remove})

        if 'Item' in response:
            matched_item_remove = response['Item']
            price_remove = float(matched_item_remove['Price'])
            order.remove_item(food_item_to_remove, price_remove)
            modified_items.append(f"Removed {food_item_to_remove} from your order.")
        else:
            modified_items.append(f"Sorry, we couldn't find '{food_item_to_remove}' on the menu to remove.")

    if modified_items:
        modified_string = ', '.join(modified_items[:-1]) + f", and {modified_items[-1]}" if len(modified_items) > 1 else modified_items[0]
        return f"{modified_string} Your order has been updated."
    else:
        return "No changes were made to your order."

def get_order_nutrition(entities):
    if not order.get_total_items():
        return "Your order is empty."
    properties = entities['properties']
    # Determine if we should gather all nutrition or specific properties
    if properties and properties[0] == 'nutrition':
        # List of all possible nutritional values
        requested_nutrients = ["Calories", "Fat", "Sat_Fat", "Trans_Fat", "Cholesterol", "Sodium", "Carbohydrates", "Fiber", "Sugar", "Protein"]
    elif properties:
        # Gather only the specific properties requested
        requested_nutrients = properties
    else:
        return "Invalid properties. Please specify 'nutrition' or a list of specific nutritional properties."

    # Initialize totals for each requested nutrient
    total_nutrition = {nutrient: 0 for nutrient in requested_nutrients}

    nutritional_info_list = []

    # Loop through each item in the order
    for food_item, quantity in order.get_total_items().items():
        try:
            # Query DynamoDB to get the item's details
            response = menu.get_item(Key={'Item': food_item})

            if 'Item' in response:
                item = response['Item']

                # Extract nutritional information
                nutritional_info = {"Food_item": food_item, "Quantity": quantity}
                for nutrient in requested_nutrients:
                    # Default to 0 if the nutrient is not found
                    nutrient_value = item.get(nutrient, 0)
                    nutritional_info[nutrient] = nutrient_value

                    # Add the value to the total nutrition (multiplied by quantity)
                    total_nutrition[nutrient] += float(nutrient_value) * quantity

                # Append the item's requested nutritional info to the list as a formatted string
                nutrient_details = ", ".join([f"{nutritional_info[n]}g {n}" for n in requested_nutrients])
                nutritional_info_list.append(f"{quantity}x {food_item}: {nutrient_details}")

            else:
                nutritional_info_list.append(f"Sorry, we couldn't find '{food_item}' on the menu.")

        except Exception as e:
            nutritional_info_list.append(f"Error retrieving info for '{food_item}': {str(e)}")

    # Build the final string response for both individual and total nutrition info
    if nutritional_info_list:
        total_nutrition_string = "\n".join([f"{nutrient}: {total:.2f}g" for nutrient, total in total_nutrition.items()])
        return (f"Total Nutritional Information:\n{total_nutrition_string}")
    else:
        return "No nutritional information found for your order."

def get_order_status():
    if not order.get_total_items():
        return "Your order is currently empty."
    
    order_items = order.get_total_items()
    order_details = []

    for item, quantity in order_items.items():
        order_details.append(f"{quantity} x {item}")

    order_summary = ", ".join(order_details)

    return f"Your current order is {order_summary}, with a total price of ${order.get_total_price():.2f}."

def place_order(entities):
    food_items = entities['food_items']
    quantities = entities['quantities']
    
    if not food_items:
        return "No food items were provided to place in your order."

    added_items = []

    for i, food_item in enumerate(food_items):
        quantity = quantities[i] if i < len(quantities) else 1
        
        # Check if the food item exists in the menu (DynamoDB)
        response = menu.get_item(Key={'Item': food_item})

        if 'Item' in response:
            matched_item = response['Item']
            price = float(matched_item['Price'])
            
            # Add the item to the order
            order.add_item(food_item, price, quantity)
            added_items.append(f"Added {food_item} to your order with quantity {quantity} at ${price:.2f} each.")
        else:
            # Handle case when item is not found in the menu
            added_items.append(f"Sorry, we couldn't find '{food_item}' on the menu.")

    if added_items:
        added_string = ', '.join(added_items[:-1]) + f", and {added_items[-1]}" if len(added_items) > 1 else added_items[0]
        return f"{added_string} Your order has been updated."
    else:
        return "No items were added to your order."

def cancel_order():
    order.clear_order()

    return "Okay, I have canceled your order."

#for entire menu: list out every menu item (not nutrition or calorie or ingredients etc)
#for dietary restrictions: query against a "vegan" or "vegetarian" tag (need to define intent scope for both of these (any other dietary restriction doesnt matter, dont worry about it for now)), and return all items that correspond to this tag
#for ingredients of an item, return every single ingredient
#for nutritional information of an item, return every single nutritional fact (calorie, saturated fat, trans fat, etc etc)
def list_entire_menu():
    try:
        response = menu.scan()
        items = response.get("Items", [])
        menu_items = [item["Item"] for item in items]
        return f"Absolutely! Here's the menu: {', '.join(menu_items)}"
    except Exception as e:
        return f"Exception {e}"
    
# Helper for dietary restrictions
def is_vegetarian(ingredients):
    non_vegetarian_items = [
        "chicken",
        "beef",
        "pork",
        "fish",
        "seafood",
        "lamb",
        "bacon",
        "ham",
        "duck",
        "turkey",
        "gelatin",
        "anchovy",
        "meat",
    ]
    words = re.findall(r"\b\w+\b", ingredients.lower())

    for item in non_vegetarian_items:
        if item in words:
            return False
    return True


# Helper for dietary restrictions
def is_vegan(ingredients):
    if not is_vegetarian(ingredients):
        return False
    non_vegan_items = [
        "milk",
        "cheese",
        "butter",
        "honey",
        "egg",
        "cream",
        "yogurt",
        "whey",
        "casein",
    ]
    words = re.findall(r"\b\w+\b", ingredients.lower())

    for item in non_vegan_items:
        if item in words:
            return False
    return True


def get_items_by_dietary_restriction(entities):
    if entities and "dietary" in entities:
        restriction = entities["dietary"].lower()
    else:
        return "Please specify a dietary restriction (e.g., vegetarian, vegan, dairy-free, soy-free, etc.)."

    try:
        response = menu.scan()
        items = response.get("Items", [])
        
        # If specific food items are provided, filter the items list
        if entities and "food_items" in entities and entities["food_items"]:
            food_items = [item.lower() for item in entities["food_items"]]
            items = [item for item in items if item.get("Item", "").lower() in food_items]
        
        matching_items = set()

        for item in items:
            ingredients = item.get("Ingredients", "").lower()
            
            # Vegan restriction check
            if restriction == "vegan":
                if is_vegan(ingredients):
                    matching_items.add(item["Item"])
                    
            # Vegetarian restriction check
            elif restriction == "vegetarian":
                if is_vegetarian(ingredients):
                    matching_items.add(item["Item"])
            
            # Checking for allergen-related restrictions
            elif restriction == "dairy":
                if item.get("Dairy") == 0:
                    matching_items.add(item["Item"])
            elif restriction == "soy":
                if item.get("Soy") == 0:
                    matching_items.add(item["Item"])
            elif restriction == "wheat":
                if item.get("Wheat") == 0:
                    matching_items.add(item["Item"])
            elif restriction == "tree_nuts":
                if item.get("Tree_Nuts") == 0:
                    matching_items.add(item["Item"])
            elif restriction == "fish":
                if item.get("Fish") == 0:
                    matching_items.add(item["Item"])
            elif restriction == "egg":
                if item.get("Egg") == 0:
                    matching_items.add(item["Item"])
            else:
                return "Currently, we only support 'vegan', 'vegetarian', and allergen-related dietary restrictions like 'dairy-free', 'soy-free', etc."
        
        # Handling specific food items and results formatting
        if entities and "food_items" in entities and entities["food_items"]:
            res = []
            for item in entities["food_items"]:
                if not matching_items or item not in matching_items:
                    if restriction == 'vegan' or restriction == 'vegetarian':
                        res.append(f"{item} is not {restriction}")
                    else:
                        res.append(f"{item} is not {restriction}-free")
                else:
                    if restriction == 'vegan' or restriction == 'vegetarian':
                        res.append(f"{item} is {restriction}")
                    else:
                        res.append(f"{item} is {restriction}-free")
            return '. '.join(res)
        else:
            if not matching_items:
                return f"No items found for dietary restriction: {restriction}."
            return f"Here are some of our {restriction}-free items: {', '.join(matching_items)}"
    except Exception as e:
        return f"Error retrieving items with restriction {restriction}: {str(e)}"


    
def get_ingredients(entities):
    if entities and "food_items" in entities and entities["food_items"]:
        food_item = entities["food_items"].lower()
    else:
        return "Please specify a single food item to get its ingredients"

    try:
        response = menu.get_item(Key={"Item": food_item})

        if "Item" not in response:
            return f"No item found with the name: {food_item}."

        item = response["Item"]
        ingredients = item.get("Ingredients", "No ingredients found for this item.")

        return f"Sure! Our {food_item} has {ingredients}."

    except Exception as e:
        return f"Error retrieving ingredients for '{food_item}': {str(e)}"
    
def get_nutritional_info(entities): # should add units (ex: grams)
    units = {
        "Fat": "G",
        "Sat. Fat": "G",
        "Trans Fat": "G",
        "Cholesterol": "MG",
        "Sodium": "MG",
        "Carbohydrates": "G",
        "Fiber": "G",
        "Sugar": "G",
        "Protein": "G"
    }

    # Check if the food item is specified
    if 'food_items' not in entities or not entities['food_items']:
        return "Please specify a food item to get its nutritional information."

    food_item = entities['food_items']
    # Handle if food_item is a list
    if isinstance(food_item, list):
        food_item = food_item[0]
    food_item = food_item.lower()

    properties = entities.get('properties', None)
    # Determine if we should gather all nutrition or specific properties
    if properties:
        if isinstance(properties, str):
            properties = [properties]
        if properties[0] == 'nutrition':
            # List of all possible nutritional values
            requested_nutrients = [
                "Calories", "Fat", "Sat_Fat", "Trans_Fat", "Cholesterol",
                "Sodium", "Carbohydrates", "Fiber", "Sugar", "Protein"
            ]
        else:
            # Gather only the specific properties requested
            requested_nutrients = properties
    else:
        return "Invalid properties. Please specify 'nutrition' or a list of specific nutritional properties."

    try:
        # Query DynamoDB to get the item's details
        response = menu.get_item(Key={'Item': food_item})

        if 'Item' not in response:
            return f"No item found with the name '{food_item}'."

        item = response['Item']

        # Extract nutritional information
        nutritional_info = {"Food_item": food_item.title()}
        for nutrient in requested_nutrients:
            # Default to "Data not available" if the nutrient is not found
            nutrient_value = item.get(nutrient, "Data not available")
            nutritional_info[nutrient] = nutrient_value

        # Format the nutritional information
        nutrient_details = "\n".join([
            f"{nutrient}: {nutritional_info[nutrient]:.2f}{units.get(nutrient, '')}"
            # f"{nutrient}: {nutritional_info[nutrient]:.2f}" if isinstance(nutritional_info[nutrient], (int, float))
            #else f"{nutrient}: {nutritional_info[nutrient]}"
            for nutrient in requested_nutrients
        ])

        return f"Nutritional Information for {food_item.title()}:\n{nutrient_details}"

    except Exception as e:
        return f"Error retrieving nutritional information for '{food_item}': {str(e)}"

def out_of_scope():
    return "Sorry, I can only help with queries related to the restaurant ordering system."

def get_help():
    return "Hi! I'm Chick-Fil-AI, a natural language processing powered chatbot created to help you handle ordering food at Chick-Fil-A.\nPlease let me know how I can assist you in one of the following areas: ordering related queries and menu related queries.\nUnfortunately, I'm unable to answer queries that are out of my domain knowledge, so please keep that in mind!"