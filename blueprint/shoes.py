import os
import psycopg2
from flask import Blueprint, request
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env file into environment
shoes = Blueprint("shoes", __name__)
url = os.environ.get("DATABASE_URL")
connection = psycopg2.connect(url)

# CREATE ROUTE
@shoes.route("/", methods=["POST"])
def new_shoe():
    data = request.get_json()
    data_values = list(data.values())
    shoe_model = data["shoe_model"]
    shoe_size = data["shoe_size"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO shoes (shoe_brand,shoe_model,shoe_size,shoe_img,shoe_description) VALUES (%s,%s,%s,%s,%s)",
                data_values,
            )
    return {"status": f"Shoe model {shoe_model}, size {shoe_size} created"}, 201


# GET ALL ROUTE
@shoes.route("/", methods=["GET"])
def shoes_data():

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM shoes")
            # transform result
            columns = list(cursor.description)
            result = cursor.fetchall()
            # make dict
            results = []
            for row in result:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col.name] = row[i]
                results.append(row_dict)
            return results


# READ ROUTE
@shoes.route("/<id>", methods=["GET"])
def one_user_data(id):
    results = []
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM shoes WHERE shoe_id='{id}'")
            # result = cursor.fetchone()[0]
            columns = list(cursor.description)
            result = cursor.fetchall()
            # make dict
            results = []
            for row in result:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col.name] = row[i]
                results.append(row_dict)
            return results


# UPDATE ROUTE
@shoes.route("/<id>", methods=["PUT"])
def update_one_shoe(id):
    data = request.get_json()
    shoe_model = data["shoe_model"]
    shoe_size = data["shoe_size"]
    data_values = list(data.values())
    data_values.append(id)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE shoes SET shoe_brand=%s,shoe_model=%s,shoe_size=%s,shoe_img=%s,shoe_description=%s WHERE shoe_id=%s",
                data_values,
            )
        return {"msg": f"Shoe model {shoe_model}, size {shoe_size} updated"}


# DELETE ROUTE
@shoes.route("/<id>", methods=["DELETE"])
def del_one_shoe(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM shoes WHERE shoe_id='{id}'")
            return {"msg": f"User id {id} deleted"}, 200
