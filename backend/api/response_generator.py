import boto3
import os
from order import Order

dynamodb = boto3.resource('dynamodb', 
                        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
                        region_name='us-east-1')
menu = dynamodb.Table('CFA-Data')
order = Order()

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
        db_response = menu.get_item(Key={'Item': food_item})

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
        return f"{order_str} have been added to your order. The total will be ${total_price:.2f}."
    else:
        return "No items were added to your order"
    
def modify_order(entities):
    food_items = entities['food_items']
    quantities = entities['quantities']
    modifiers = entities['modifiers']
    
    if not food_items:
        return "No food items were found to modify in your order."

    modified_items = []

    for i, food_item in enumerate(food_items):
        # Default to 1 if no quantity specified
        quantity = quantities[i] if i < len(quantities) else 1
        
        # Check if the food item exists in the menu (DynamoDB)
        response = menu.get_item(Key={'Item': food_item})

        if 'Item' in response:
            matched_item = response['Item']
            price = float(matched_item['Price'])
            print(matched_item, price)
            
            # Check the modifier for the current food item
            if modifiers and modifiers[0].lower() == "want":
                # If the modifier indicates to add or change the quantity
                order.add_item(food_item, price, quantity)
                modified_items.append(f"Ok, sure. We added {food_item} to your order.");
                # modified_items.append(f"Added {food_item} to your order with quantity {quantity} at ${price:.2f} each. Your order includes {order.items.items()}")
            else:
                # If the modifier indicates to remove the item
                order.remove_item(food_item, price)
                modified_items.append(f"Removed {food_item} from your order.")
        else:
            # Handle case when item is not found in the menu
            modified_items.append(f"Sorry, we couldn't find '{food_item}' on the menu.")
    print(order.items.items())
    print(order.total_price)
    if modified_items:
        modified_string = ', '.join(modified_items[:-1]) + f", and {modified_items[-1]}" if len(modified_items) > 1 else modified_items[0]
        return f"{modified_string} Your order has been updated."
    else:
        return "No changes were made to your order."
    
def get_order_info():
    global order

    if not order.get_total_items():
        return "You don't have anything in your order yet."
    
    nutritional_info = {}

    for item, quantity in order.get_total_items().items():
        response = menu.get_item(Key={'Item': item})

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

def get_order_nutrition():
    pass

def get_order_status():
    if not order.get_total_items():
        return "Your order is currently empty."
    
    order_items = order.get_total_items()
    order_details = []

    for item, quantity in order_items.items():
        order_details.append(f"{quantity} x {item}")

    order_summary = ", ".join(order_details)

    return f"Your current order is {order_summary}."

def place_order():
    pass

def cancel_order():
    global order

    order.clear_order()

    return "Okay, I have canceled your order."

#for entire menu: list out every menu item (not nutrition or calorie or ingredients etc)
#for dietary restrictions: query against a "vegan" or "vegetarian" tag (need to define intent scope for both of these (any other dietary restriction doesnt matter, dont worry about it for now)), and return all items that correspond to this tag
#for ingredients of an item, return every single ingredient
#for nutritional information of an item, return every single nutritional fact (calorie, saturated fat, trans fat, etc etc)
def list_entire_menu():
    try:
        response = menu.scan()
        items = response.get('Items', [])
        menu_items = [item['Item_index'] for item in items]
        return {"menu_items": menu_items}
    except Exception as e:
        return {"error": str(e)}
    
def get_items_by_dietary_restriction(entities):
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

def out_of_scope():
    return "Sorry, I can only help with queries related to the restaurant ordering system."

def get_help():
    return "Hi! I'm Chick-Fil-AI, a natural language processing powered chatbot created to help you handle ordering food at Chick-Fil-A.\nPlease let me know how I can assist you in one of the following areas: ordering related queries and menu related queries.\nUnfortunately, I'm unable to answer queries that are out of my domain knowledge, so please keep that in mind!"