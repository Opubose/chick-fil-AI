from flask import Flask, request, jsonify, session
from flask_cors import CORS
import actions
import response_generator
import uuid
from order import Order
from datetime import timedelta

app = Flask(__name__)
app.config["CORS_HEADERS"] = "Content-Type"
app.config["SECRET_KEY"] = "testing"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    minutes=30
)  # The browser cookies are valid for 30 minutes
CORS(
    app,
    resources={r"/*": {"origins": "http://localhost:3000"}},
    supports_credentials=True,
)


@app.before_request
def before_request():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
        session["order"] = Order().__dict__


@app.route("/chat", methods=["POST"])
def get_bot_response():
    customer_message = request.json.get("customer_message")
    if customer_message:
        bot_response = actions.get_intent_and_entities(customer_message)

        # handle various intents

        if bot_response["intent"] == "menu_dietary":
            bot_message = actions.menu_dietary(bot_response["entities"])
        elif bot_response["intent"] == "menu_entire":
            bot_message = actions.menu_entire()
        elif bot_response["intent"] == "menu_ingredients":
            bot_message = actions.menu_ingredients(bot_response["entities"])
        elif bot_response["intent"] == "menu_nutrition":
            bot_message = actions.menu_nutrition(bot_response["entities"])
        elif bot_response["intent"] == "item_description":
            bot_message = actions.item_description(bot_response["entities"])
        elif bot_response["intent"] == "order_cancel":
            bot_message = actions.order_cancel(bot_response["entities"])
        elif bot_response["intent"] == "order_modify":
            bot_message = actions.order_modify(bot_response["entities"])
        elif bot_response["intent"] == "order_nutrition":
            bot_message = actions.order_nutrition(bot_response["entities"])
        elif bot_response["intent"] == "place_order":
            bot_message = actions.place_order(bot_response["entities"])
        elif bot_response["intent"] == "order_place":
            bot_message = actions.order_place(bot_response["entities"])
        elif bot_response["intent"] == "order_status":
            bot_message = actions.order_status()
        elif bot_response["intent"] == "get_help":
            bot_message = response_generator.get_help()
        else:
            bot_message = response_generator.out_of_scope()
        
        return jsonify({"bot_message": bot_message}), 200
    else:
        return jsonify({"bot_message": "Error in Flask application!"}), 400


if __name__ == "__main__":
    app.run(port=8000)
