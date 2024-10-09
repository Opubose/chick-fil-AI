import boto3
import os

dynamodb = boto3.resource('dynamodb', 
                        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
                        region_name='us-east-1')
menu = dynamodb.Table('CFA-Data')

#for place: query database and add the items to an "order" --> need to think of how to handle an order. probably a seperate class called Order?
#for modify: update order and requery database to update accordingly (different nutritonal, ingredient) information --> will be useful for menu related queries
#for status: literally just return what the current order is
#for cancel: just scrap the entire order and jsonify return ("Ok, I've cancelled your order")
#for info: return the nutritional information (only main ones (calories, fat, carb, sugar, protein)) of the items currently in the order
def place_order(entities):
    return ""
def modify_order(entities):
    return ""
def get_order_info(entities):
    return ""
def get_order_status():
    return ""
def cancel_order():
    return ""

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
