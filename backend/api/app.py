from flask import Flask, request, jsonify, session
from flask_cors import CORS
import actions
import response_generator
from uuid import uuid4
from os import environ
from order import Order
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
allowed_origins = [
    "http://localhost:3000",  # Development
    "https://chick-fil-ai.herokuapp.com",  # Production
]
app.config["CORS_HEADERS"] = "Content-Type"
app.config["SECRET_KEY"] = environ["SESSION_ID"]
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    minutes=30
)  # The browser cookies are valid for 30 minutes
CORS(
    app,
    resources={
        r"/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Range", "X-Content-Range"],
            "supports_credentials": True,
            "max_age": 3600,
        }
    },
    vary_header=True,
)


@app.before_request
def before_request():
    if "user_id" not in session:
        session["user_id"] = str(uuid4())
        session["order"] = Order().__dict__


@app.route("/chat", methods=["POST"])
def get_bot_response():
    customer_message = request.json.get("customer_message")
    if customer_message:
        bot_response = actions.get_intent_and_entities(customer_message)

        # Use a dictionary to map intents to actions
        actions_mapping = {
            "menu_dietary": lambda: actions.menu_dietary(bot_response["entities"]),
            "menu_entire": actions.menu_entire,
            "menu_ingredients": lambda: actions.menu_ingredients(bot_response["entities"]),
            "menu_nutrition": lambda: actions.menu_nutrition(bot_response["entities"]),
            "order_cancel": lambda: actions.order_cancel(bot_response["entities"]),
            "order_modify": lambda: actions.order_modify(bot_response["entities"]),
            "order_nutrition": lambda: actions.order_nutrition(bot_response["entities"]),
            "order_place": lambda: actions.order_place(bot_response["entities"]),
            "order_status": actions.order_status,
            "get_help": response_generator.get_help,
        }

        # Attempt to get the bot message from the mapping, or set to out_of_scope if not found
        bot_message = actions_mapping.get(bot_response["intent"], response_generator.out_of_scope)()

        return jsonify({"bot_message": bot_message}), 200
    else:
        return jsonify({"bot_message": "Error in Flask application!"}), 400


if __name__ == "__main__":
    app.run(port=8000)
