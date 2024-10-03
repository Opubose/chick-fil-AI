from flask import Flask, render_template, request, jsonify

import actions

app = Flask(__name__)


#@app.route('/')
#def index():
#    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def get_bot_response():
    customer_message = request.json.get('customer_message')
    if customer_message:
        bot_response = actions.detect_intent(customer_message)

        #three high level intents of ordering, menu related queries, and needing help
        if bot_response['intent'] == 'order':
            order = actions.order_handler(bot_response['entities'])
            return jsonify({'bot_message': order}, 200)
        if bot_response['intent'] == 'menu':
            menu = actions.menu_handler(bot_response['entities'])
            return jsonify({'bot_message': menu}, 200)
        if bot_response['intent'] == 'help':
            help = actions.get_help(bot_response['entities'])
            return jsonify({'bot_message': help}, 200)
        
        #if a high level intent isnt detected it is out of scope for this bot
        return jsonify({"bot_message": "Sorry, I can only help with queries related to the restauarnt ordering system."}, 200)
    else:
        return jsonify({"bot_message": "Error in Flask application!"}, 400)

if __name__ == "__main__":
    app.run()