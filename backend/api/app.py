from flask import Flask, request, jsonify
from flask_cors import CORS
import actions

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.route('/chat', methods=['POST'])
def get_bot_response():
    customer_message = request.json.get('customer_message')
    if customer_message:
        bot_response = actions.get_intent_and_entities(customer_message)

        #ensure query in scope
        #if bot_response['intent'] == 'invalid':
        #    return jsonify({"bot_message": "Sorry, I can only help with queries related to the restaurant ordering system."}), 200
        
        #three high level intents of ordering, menu related queries, and needing help
        if bot_response['intent'] == 'order':
            lower_level_intent = ""
            bot_message = actions.order_handler(lower_level_intent, bot_response['entities'])
            return jsonify({'bot_message': "order related intent detected"}), 200
        if bot_response['intent'] == 'menu':
            lower_level_intent = ""
            bot_message = actions.menu_handler(lower_level_intent, bot_response['entities'])
            return jsonify({'bot_message': "menu related intent detected"}), 200
        if bot_response['intent'] == 'help':
            bot_message = actions.get_help()
            return jsonify({'bot_message': bot_message}), 200
        
        #default handler
        return jsonify({"bot_message": "Sorry, I can only help with queries related to the restaurant ordering system."}), 200
    else:
        return jsonify({"bot_message": "Error in Flask application!"}), 400
    
if __name__ == "__main__":
    app.run(port=8000)