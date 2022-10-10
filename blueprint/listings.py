import os
import psycopg2
from flask import Blueprint, request
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env file into environment
listings = Blueprint("listings", __name__)
url = os.environ.get("DATABASE_URL")
connection = psycopg2.connect(url)

# CREATE ROUTE
@listings.route("/", methods=["POST"])
def new_listing():
    data = request.get_json()
    data_values = list(data.values())
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO listings (listing_price,shoe_id,user_id) VALUES (%s,%s,%s)",
                data_values,
            )
    return {"status": f"Listing created"}, 201


# GET ALL ROUTE
@listings.route("/", methods=["GET"])
def listings_data():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM listings")
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
@listings.route("/<id>", methods=["GET"])
def one_listing_data(id):
    results = []
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM listings WHERE listing_id='{id}'")
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
@listings.route("/<id>", methods=["PUT"])
def update_one_listing(id):
    data = request.get_json()
    data_values = list(data.values())
    data_values.append(id)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE listings SET listing_price=%s,shoe_id=%s,sold=%s,user_id=%s WHERE listing_id=%s",
                data_values,
            )
        return {"msg": f"Listing id {id} updated"}


# DELETE ROUTE
@listings.route("/<id>", methods=["DELETE"])
def del_one_listing(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM listings WHERE listing_id='{id}'")
            return {"msg": f"Listing id {id} deleted"}, 200
