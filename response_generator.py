import os
import re
from order import Order
from pymongo import MongoClient
import certifi
import random
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv("URI-MONGODB")
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client["CFA-Data"]
menu = db["Menu-Info"]
order = Order()


units = {
    "Calories": "",
    "Fat": "G",
    "Sat. Fat": "G",
    "Trans Fat": "G",
    "Cholesterol": "MG",
    "Sodium": "MG",
    "Carbohydrates": "G",
    "Fiber": "G",
    "Sugar": "G",
    "Protein": "G",
}

modify_place_order_strings = [
    "Of course! I've updated your order accordingly, which now includes the following: ",
    "Great choice. Your order has been updated successfully, and it contains: ",
    "All set! I've updated your order accordingly: ",
]
order_nutrition_strings = [
    "Here's a full breakdown of your order's nutritional value:\n",
    "Here's everything you need to know about the nutrition in your order:\n",
    "Here's the nutritional info for everything in your order:\n",
]
cancel_order_strings = [
    "Got it! Your order has been cleared. Please let me know if you need anything else.",
    "Done! Your order is now empty. I'm happy to help with a new order whenever you're ready.",
    "Understood - I've emptied your order. If you need anything else, please let me know!",
]
order_menu_strings = [
    "Absolutely! Here's our current menu:\n",
    "Sure thing! Here's what we have on the menu today:\n",
    "Here's a full view of our menu:\n",
]
menu_restriction_strings = [
    "Of course. Here are some of our menu items that are",
    "No problem! Here's what we can offer that's",
    "Understood. Here's a selection of items that are",
]
menu_ingredient_strings = [
    "Of course! Here's what's in our",
    "Here's a quick look at what goes into our",
    "We use the following ingredients in our",
]
menu_nutrition_strings = [
    "Here's all the nutritional information you requested for the",
    "Here's the nutritional profile requested for the",
    "Got it! Here's the nutritional information requested for the",
]
order_status_strings = [
    "Of course. Your current order is:",
    "Here's your current order:",
    "This is your order as of now:",
]


def modify_order(entities):
    item_details = entities["item_detail"]
    discriminators = entities["discriminator"]

    if not item_details:
        return "No items were provided to modify in your order."

    for i, item in enumerate(item_details):
        food_item = item.get("food_items")
        modifier = item.get("modifiers")
        quantity = int(item.get("quantities", 0))
        item_discriminator = item.get("discriminator")
        discriminator = (
            discriminators[i] if i < len(discriminators) else discriminators[-1]
        )

        matched_item = menu.find_one({"Item": food_item})
        if not matched_item:
            continue

        price = float(matched_item["Price"])
        if discriminator == "Add":
            if modifier and item_discriminator:
                order.add_item(
                    food_item, price, quantity, f"{item_discriminator} {modifier}"
                )
            else:
                order.add_item(food_item, price, quantity)
        elif discriminator == "Remove":
            if modifier and item_discriminator:
                order.remove_item(
                    food_item, quantity, f"{item_discriminator} {modifier}"
                )
            else:
                order.remove_item(food_item, quantity)

    index = random.randint(0, 50) % 3
    return f"{modify_place_order_strings[index]}{order.to_string()}"


def get_order_nutrition(entities):
    if not order.get_total_items():
        return "Your order is empty."
    properties = entities["properties"]

    if properties and properties[0] == "nutrition":
        requested_nutrients = [
            "Calories",
            "Fat",
            "Sat. Fat",
            "Trans Fat",
            "Cholesterol",
            "Sodium",
            "Carbohydrates",
            "Fiber",
            "Sugar",
            "Protein",
        ]
    elif properties:
        requested_nutrients = properties
    else:
        return "Invalid properties. Please specify 'nutrition' or a list of specific nutritional properties."

    total_nutrition = {nutrient: 0 for nutrient in requested_nutrients}
    nutritional_info_list = []

    for food_item in order.get_total_items():
        matched_item = menu.find_one({"Item": food_item})

        if matched_item:
            nutritional_info = {"Food_item": food_item}
            for nutrient in requested_nutrients:
                nutrient_value = matched_item.get(nutrient, 0)
                nutritional_info[nutrient] = nutrient_value
                total_nutrition[nutrient] += float(nutrient_value)

            nutrient_details = '
'.join(
                [f"{nutritional_info[n]}{units[n]} {n}" for n in requested_nutrients]
            )
            nutritional_info_list.append(f"{food_item}: {nutrient_details}")

    if nutritional_info_list:
        total_nutrition_string = "\n".join(
            [f"{nutrient}: {total:.2f}g" for nutrient, total in total_nutrition.items()]
        )
        index = random.randint(0, 50) % 3
        return f"{order_nutrition_strings[index]}{total_nutrition_string}"
    else:
        return "I'm sorry, I wasn't able to find any nutritional information for your order."


def get_order_status():
    index = random.randint(0, 50) % 3
    return f"{order_status_strings[index]} {order.to_string()}"


def place_order(entities):
    for item in entities["item_detail"]:
        food_item = item.get("food_items")
        quantity = int(item.get("quantities", 1))
        discriminator = item.get("discriminator")
        modifier = item.get("modifiers")

        matched_item = menu.find_one({"Item": food_item})

        if matched_item:
            price = float(matched_item["Price"])

            if modifier and discriminator:
                order.add_item(
                    food_item, price, quantity, f"{discriminator} {modifier}"
                )
            else:
                order.add_item(food_item, price, quantity)

    index = random.randint(0, 50) % 3
    return f"{modify_place_order_strings[index]}{order.to_string()}"


def cancel_order():
    order.clear_order()
    index = random.randint(0, 50) % 3
    return cancel_order_strings[index]


def list_entire_menu():
    try:
        items = menu.find()
        menu_items = [item["Item"] for item in items]
        index = random.randint(0, 50) % 3
        return f"{order_menu_strings[index]}" + '
'.join(menu_items)
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
        response = list(menu.find({}))  # Convert cursor to list for processing
        items = response if response else []

        # Filter items by specified food items if provided
        if "food_items" in entities and entities["food_items"]:
            food_items = [item.lower() for item in entities["food_items"]]
            items = [
                item for item in items if item.get("Item", "").lower() in food_items
            ]

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
                    if restriction == "vegan" or restriction == "vegetarian":
                        res.append(f"{item} is not {restriction}")
                    else:
                        res.append(f"{item} is not {restriction}-free")
                else:
                    if restriction == "vegan" or restriction == "vegetarian":
                        res.append(f"{item} is {restriction}")
                    else:
                        res.append(f"{item} is {restriction}-free")
            return ". ".join(res)
        else:
            if not matching_items:
                return f"No items found for dietary restriction: {restriction}."
            index = random.randint(0, 50) % 3
            return f"{menu_restriction_strings[index]} {restriction}-free: {', '.join(matching_items)}."
    except Exception as e:
        return f"Error retrieving for items with restriction {restriction}: {str(e)}"


def get_ingredients(entities):
    if entities and "food_items" in entities and entities["food_items"]:
        food_item = entities["food_items"].lower()
    else:
        return "Please specify a single food item to get its ingredients"

    try:
        item = menu.find_one({"Item": food_item})

        if not item:
            return f"No item found with the name: {food_item}."
        ingredients = item.get("Ingredients", "No ingredients found for this item.")

        index = random.randint(0, 50) % 3
        return f"{menu_ingredient_strings[index]} {food_item}: {ingredients}."

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
                "Sat. Fat",
                "Trans Fat",
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
        # Query MongoDB to get the item's details
        item = menu.find_one({"Item": food_item})
        if not item:
            return f"No item found with the name '{food_item}'."
        nutritional_info = {
            nutrient: item.get(nutrient, "Data not available")
            for nutrient in requested_nutrients
        }

        # Format the nutritional information
        nutrient_details = '
'.join(
            [
                (
                    f"{nutrient}: {nutritional_info[nutrient]:.2f}{units[nutrient]}"
                    if isinstance(nutritional_info[nutrient], (int, float))
                    else f"{nutrient}: {nutritional_info[nutrient]}"
                )
                for nutrient in requested_nutrients
            ]
        )

        index = random.randint(0, 50) % 3
        return f"{menu_nutrition_strings[index]} {food_item.title().lower()}:\n{nutrient_details}."

    except Exception as e:
        return f"Error retrieving nutritional information for '{food_item}': {str(e)}"


def get_type_list(entities):
    if "type" not in entities or not entities["type"]:
        return "Please specify a type of item (e.g., 'salads', 'sandwiches') to list."

    valid_types = {"drink", "side", "sandwich", "dessert", "chicken", "salad"}

    item_type = entities["type"].lower()

    if item_type not in valid_types:
        return f"Sorry, I don't understand the '{item_type}' type."
    try:
        # Query MongoDB for items of the specified type
        matching_items = menu.find({"Type": item_type})
        item_names = [item["Item"] for item in matching_items]

        matching_items = menu.find({item_type: 1})
        item_names = [item["Item"] for item in matching_items]

        if not item_names:
            return f"Sorry, no items found for type '{item_type}'."

        # Format and return the list of items
        index = random.randint(0, 50) % 3
        str1 = f"Here's a list of the {item_type}s we have:"
        str2 = f"These are all the {item_type}s available for you to choose from:"
        str3 = f"Of course! Take a look at the {item_type}s we have for you:"
        type_list_strings = [str1, str2, str3]

        return f"{type_list_strings[index]} {', '.join(item_names)}."

    except Exception as e:
        return f"Error retrieving items for type '{item_type}': {str(e)}"


def get_item_description(entities):
    if "food_items" not in entities or not entities["food_items"]:
        return "Please specify a food item to get its description."
    food_item = entities["food_items"]
    item = menu.find_one({"Item": food_item})
    if item:
        description = item.get("Description", "Description not available.")

        index = random.randint(0, 50) % 3
        str1 = f"Here's a summary of our popular {item['Item']}:"
        str2 = f"This is everything you need to know about our {item['Item']}:"
        str3 = f"Sure! Our {item['Item']} is described as:"
        item_description_strings = [str1, str2, str3]

        return f"{item_description_strings[index]} {description}"

    return f"Error retrieving description for {food_item}"


def get_item_price(entities):
    if "food_items" not in entities or not entities["food_items"]:
        return "Please specify a food item to get its cost."
    food_item = entities["food_items"]
    try:
        # Query MongoDB for the item's details
        item = menu.find_one({"Item": food_item})
        if not item:
            return f"No item found with the name '{food_item}'."

        # Extract the cost/price of the item
        cost = item.get("Price", None)
        if cost is None:
            return f"The cost for '{food_item}' is not available."

        index = random.randint(0, 50) % 3
        str1 = f"Our {food_item} is priced at $"
        str2 = f"The cost for our {food_item} is just $"
        str3 = f"You can get our {food_item} for $"
        food_item_strings = [str1, str2, str3]

        return f"{food_item_strings[index]}{cost:.2f}."

    except Exception as e:
        return f"Error retrieving cost for '{food_item}': {str(e)}"


def out_of_scope():
    return (
        "Sorry, I can only help with queries related to the restaurant ordering system."
    )


def get_help():
    return "Hi! I'm Chick-Fil-AI, a natural language processing powered chatbot created to help you handle ordering food at Chick-Fil-A.\nPlease let me know how I can assist you in one of the following areas: ordering related queries and menu related queries.\nUnfortunately, I'm unable to answer queries that are out of my domain knowledge, so please keep that in mind!"
