import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, Blueprint
from flask_cors import CORS
from blueprint.users import users
from blueprint.shoes import shoes
from blueprint.listings import listings
from blueprint.alerts import alerts


load_dotenv()  # loads variables from .env file into environment

app = Flask(__name__)
CORS(app)

app.register_blueprint(users, url_prefix="/users")
app.register_blueprint(shoes, url_prefix="/shoes")
app.register_blueprint(listings, url_prefix="/listings")
app.register_blueprint(alerts, url_prefix="/alerts")


url = os.environ.get("DATABASE_URL")  # gets variables from environment
connection = psycopg2.connect(url)


@app.route("/", methods=["GET", "POST"])
def home():
    return {"home": "This is the homepage"}
