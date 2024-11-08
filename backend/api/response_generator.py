import os
import re
from order import Order
from pymongo import MongoClient
import certifi

uri = os.getenv("URI-MONGODB")
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client['CFA-Data']
menu = db['Menu-Info']
order = Order()

def modify_order(entities):
    food_items = entities["food_items"]
    discriminators = entities["discriminator"]
    quantities = entities["quantities"] if "quantities" in entities else []
    modifiers = entities["modifiers"] if "modifiers" in entities else []

    if not food_items or not discriminators:
        return "No food items or actions were found to modify in your order."

    for i in range(len(food_items)):
        food_item = food_items[i]
        discriminator = discriminators[i]
        quantity = quantities[i] if i < len(quantities) else 1
        modifier = modifiers[i] if i < len(modifiers) else None

        matched_item = menu.find_one({"Item": food_item})
        if matched_item:
            price = float(matched_item["Price"])

            if modifier:
                if discriminator == "Add":
                    order.add_modifier(food_item, f"add {modifier}")
                else:
                    order.add_modifier(food_item, f"no {modifier}")
            elif discriminator == "Add":
                order.add_item(food_item, price, quantity)
            elif discriminator == "Remove":
                order.remove_item(food_item, price, quantity)

    order_items = order.get_total_items()
    order_details = []

    for item, quantity in order_items.items():
        order_details.append(f"{quantity} x {item}" + (order.modifiers[item] if item in order.modifiers else ""))

    return f"Your order has been updated. Here is your order: {', '.join(order_details)}"


def get_order_nutrition(entities):
    if not order.get_total_items():
        return "Your order is empty."
    properties = entities["properties"]

    if properties and properties[0] == "nutrition":
        requested_nutrients = [
            "Calories", "Fat", "Sat_Fat", "Trans_Fat", "Cholesterol",
            "Sodium", "Carbohydrates", "Fiber", "Sugar", "Protein"
        ]
    elif properties:
        requested_nutrients = properties
    else:
        return "Invalid properties. Please specify 'nutrition' or a list of specific nutritional properties."

    total_nutrition = {nutrient: 0 for nutrient in requested_nutrients}
    nutritional_info_list = []

    for food_item, quantity in order.get_total_items().items():
        matched_item = menu.find_one({"Item": food_item})

        if matched_item:
            nutritional_info = {"Food_item": food_item, "Quantity": quantity}
            for nutrient in requested_nutrients:
                nutrient_value = matched_item.get(nutrient, 0)
                nutritional_info[nutrient] = nutrient_value
                total_nutrition[nutrient] += float(nutrient_value) * quantity

            nutrient_details = ", ".join(
                [f"{nutritional_info[n]}g {n}" for n in requested_nutrients]
            )
            nutritional_info_list.append(f"{quantity}x {food_item}: {nutrient_details}")
        else:
            nutritional_info_list.append(f"Sorry, we couldn't find '{food_item}' on the menu.")

    if nutritional_info_list:
        total_nutrition_string = "\n".join(
            [f"{nutrient}: {total:.2f}g" for nutrient, total in total_nutrition.items()]
        )
        return f"Total Nutritional Information:\n{total_nutrition_string}"
    else:
        return "No nutritional information found for your order."


def get_order_status():
    if not order.get_total_items():
        return "Your order is currently empty."

    order_items = order.get_total_items()
    order_details = [f"{quantity} x {item}" for item, quantity in order_items.items()]

    order_summary = ", ".join(order_details)
    return f"Your current order is {order_summary} for a total of ${order.get_total_price()}."


def place_order(entities):
    added_items = []

    for item in entities['item_detail']:
        food_item = item.get("food_items")
        quantity = int(item.get("quantities", 1))
        discriminator = item.get("discriminator")
        modifier = item.get("modifiers")

        matched_item = menu.find_one({"Item": food_item})
        
        if matched_item:
            price = float(matched_item["Price"])

            order.add_item(food_item, price, quantity)
            added_item_str = f"Added {quantity}x {food_item} to your order at ${price:.2f} each."

            if modifier and discriminator:
                order.add_modifier(food_item, discriminator, modifier)
                added_item_str += f" {discriminator.capitalize()} {modifier}."

            added_items.append(added_item_str)

    if added_items:
        added_string = (
            ", ".join(added_items[:-1]) + f", and {added_items[-1]}"
            if len(added_items) > 1
            else added_items[0]
        )
        return f"{added_string} Your order has been updated."
    else:
        return "No items were added to your order."


def cancel_order():
    order.clear_order()
    return "Okay, I have canceled your order."


def list_entire_menu():
    try:
        items = menu.find()
        menu_items = [item["Item"] for item in items]
        return f"Absolutely! Here's the menu: {', '.join(menu_items)}"
    except Exception as e:
        return f"Exception {e}"


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
        return f"Error retrieving for items with restriction {restriction}: {str(e)}"


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


def get_nutritional_info(entities):
    # Check if the food item is specified
    if "food_items" not in entities or not entities["food_items"]:
        return "Please specify a food item to get its nutritional information."

    food_item = entities["food_items"]
    # Handle if food_item is a list
    if isinstance(food_item, list):
        food_item = food_item[0]
    food_item = food_item.lower()

    properties = entities.get("properties", None)
    # Determine if we should gather all nutrition or specific properties
    if properties:
        if isinstance(properties, str):
            properties = [properties]
        if properties[0] == "nutrition":
            # List of all possible nutritional values
            requested_nutrients = [
                "Calories",
                "Fat",
                "Sat_Fat",
                "Trans_Fat",
                "Cholesterol",
                "Sodium",
                "Carbohydrates",
                "Fiber",
                "Sugar",
                "Protein",
            ]
        else:
            # Gather only the specific properties requested
            requested_nutrients = properties
    else:
        return "Invalid properties. Please specify 'nutrition' or a list of specific nutritional properties."

    try:
        # Query DynamoDB to get the item's details
        response = menu.get_item(Key={"Item": food_item})

        if "Item" not in response:
            return f"No item found with the name '{food_item}'."

        item = response["Item"]

        # Extract nutritional information
        nutritional_info = {"Food_item": food_item.title()}
        for nutrient in requested_nutrients:
            # Default to "Data not available" if the nutrient is not found
            nutrient_value = item.get(nutrient, "Data not available")
            nutritional_info[nutrient] = nutrient_value

        # Format the nutritional information
        nutrient_details = "\n".join(
            [
                (
                    f"{nutrient}: {nutritional_info[nutrient]:.2f}g"
                    if isinstance(nutritional_info[nutrient], (int, float))
                    else f"{nutrient}: {nutritional_info[nutrient]}"
                )
                for nutrient in requested_nutrients
            ]
        )

        return f"Nutritional Information for {food_item.title()}:\n{nutrient_details}"

    except Exception as e:
        return f"Error retrieving nutritional information for '{food_item}': {str(e)}"
    

def get_item_description(entities):
    food_item = entities["food_items"]
    try:
        response = menu.get_item(Key={"Item": food_item})
        if 'Item' in response:
            description = response['Item'].get('Description')
            return description if description else "Description not available."
    except Exception as e:
        return f"Error retrieving description for {food_item}"
    pass


def out_of_scope():
    return (
        "Sorry, I can only help with queries related to the restaurant ordering system."
    )


def get_help():
    return "Hi! I'm Chick-Fil-AI, a natural language processing powered chatbot created to help you handle ordering food at Chick-Fil-A.\nPlease let me know how I can assist you in one of the following areas: ordering related queries and menu related queries.\nUnfortunately, I'm unable to answer queries that are out of my domain knowledge, so please keep that in mind!"
