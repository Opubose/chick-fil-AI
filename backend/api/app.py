from flask import Flask, request, jsonify
from flask_cors import CORS
import actions
import response_generator

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.route('/chat', methods=['POST'])
def get_bot_response():
    customer_message = request.json.get('customer_message')
    if customer_message:
        bot_response = actions.get_intent_and_entities(customer_message) #returns {'intent': 'intent', 'entities' [entites]}

        #ensure query in scope
        if bot_response['intent'] == 'out_of_scope':
            bot_message = response_generator.out_of_scope()
            return jsonify({"bot_message": bot_message}), 200
        if bot_response['intent'] == 'menu_dietary':
            bot_message = actions.menu_dietary(bot_response['entities'])
            return jsonify({'bot_message': bot_message}), 200
        if bot_response['intent'] == 'menu_entire':
            bot_message = actions.menu_entire(bot_response['entities'])
            return jsonify({'bot_message': bot_message}), 200
        if bot_response['intent'] == 'menu_ingredients':
            bot_message = actions.menu_ingredients(bot_response['entities'])
            return jsonify({'bot_message': bot_message}), 200
        if bot_response['intent'] == 'menu_nutrition':
            bot_message = actions.menu_nutrition(bot_response['entities'])
            return jsonify({'bot_message': bot_message}), 200
        if bot_response['intent'] == 'order_cancel':
            bot_message = actions.order_cancel(bot_response['entities'])
            return jsonify({'bot_message': bot_message}), 200
        if bot_response['intent'] == 'order_modify':
            bot_message = actions.order_modify(bot_response['entities'])
            return jsonify({'bot_message': bot_message}), 200
        if bot_response['intent'] == 'order_nutrition':
            bot_message = actions.order_nutrition(bot_response['entities'])
            return jsonify({'bot_message': bot_message}), 200
        if bot_response['intent'] == 'order_place':
            bot_message = actions.order_place(bot_response['entities'])
            return jsonify({'bot_message': bot_message}), 200
        if bot_response['intent'] == 'order_status':
            bot_message = actions.order_status(bot_response['entities'])
            return jsonify({'bot_message': bot_message}), 200
        if bot_response['intent'] == 'get_help':
            bot_message = response_generator.get_help()
            return jsonify({'bot_message': bot_message}), 200 
        
        #default handler
        return jsonify({"bot_message": "Error parsing intent!"}), 200
    else:
        return jsonify({"bot_message": "Error in Flask application!"}), 400

if __name__ == "__main__":
    app.run(port=8000)