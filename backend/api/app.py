from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import actions

app = Flask(__name__)
CORS(app)


#@app.route('/')
#def index():
#    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def get_bot_response():
    customer_message = request.json.get('customer_message')
    print("before if:",customer_message)
    if customer_message:

        bot_response = actions.get_intent_and_entities(customer_message)
        print("in if:",bot_response)

        #ensure query in scope
        if bot_response['intent'] == 'invalid':
            print("hi")
            return jsonify({"bot_message": "Sorry, I can only help with queries related to the restaurant ordering system."}), 200

        
        #three high level intents of ordering, menu related queries, and needing help
        if bot_response['intent'] == 'order':
            bot_message = actions.order_handler(bot_response['entities'])
            return jsonify({'bot_message': bot_message}, 200)
        if bot_response['intent'] == 'menu':
            bot_message = actions.menu_handler(bot_response['entities'])
            return jsonify({'bot_message': bot_message}, 200)
        if bot_response['intent'] == 'help':
            bot_message = actions.get_help(bot_response['entities'])
            return jsonify({'bot_message': bot_message}, 200)
        
        #default handler
        return jsonify({"bot_message": "Sorry, I can only help with queries related to the restaurant ordering system."}), 200

    else:
        return jsonify({"bot_message": "Error in Flask application!"}, 400)

if __name__ == "__main__":
    app.run()