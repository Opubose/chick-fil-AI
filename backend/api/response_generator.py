import boto3
import os
from order import Order

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