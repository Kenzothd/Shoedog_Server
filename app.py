import os
import psycopg2
import time
from dotenv import load_dotenv
from flask import Flask, request, Blueprint
from flask_cors import CORS, cross_origin
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
# cors = CORS(app, resources={r'*': {'origins': 'http://localhost:3000'}})

url = os.environ.get("DATABASE_URL")  # gets variables from environment
connection = None
for i in range(10):
    try:
        psycopg2.connect(url)
        break
    except psycopg2.OperationalError as e:
        print("Cannot connect to database, retrying in 5 seconds...")
        time.sleep(5)
if connection:
    # perform database operations
    time.sleep(1800)  # wait for 30 minutes before reconnecting
    connection.close()
else:
    print("Unable to connect to the database")


@app.route("/", methods=["GET", "POST"])
def home():
    return {"home": "This is the homepage"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
