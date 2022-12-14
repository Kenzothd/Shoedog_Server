import os
import psycopg2
from flask import Blueprint, request
from dotenv import load_dotenv
from flask_cors import CORS
from blueprint.alerts import check_alert

load_dotenv()  # loads variables from .env file into environment
listings = Blueprint("listings", __name__)
CORS(listings)
url = os.environ.get("DATABASE_URL")
connection = psycopg2.connect(url)

# CREATE ROUTE(old)
# @listings.route("/", methods=["POST"])
# def new_listing():
#     data = request.get_json()
#     data_values = list(data.values())
#     with connection:
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "INSERT INTO listings (user_id,shoe_id,listing_price) VALUES (%s,%s,%s)",
#                 data_values,
#             )
#     return {"status": f"Listing created"}, 201

# CREATE ROUTE(new)
@listings.route("/<id>", methods=["POST"])
def new_listing(id):
    data = request.get_json()
    shoe_brand = data["shoe_brand"]
    shoe_model= data["shoe_model"]
    shoe_size= data["shoe_size"]
    listing_price= data["listing_price"]
    with connection:
         try: 
            with connection.cursor() as cursor:
                cursor.execute(f"WITH rows AS (SELECT shoe_id FROM shoes WHERE shoe_brand='{shoe_brand}' AND shoe_model='{shoe_model}' AND shoe_size='{shoe_size}') INSERT INTO listings (user_listing_id,shoe_id,listing_price) SELECT '{id}',shoe_id,'{listing_price}' FROM rows RETURNING listings.*;")
                results=[]
                check_alert(cursor,results)
            return results, 201
         except Exception as error:
                return {"error": f"{error}"}, 400


# GET ALL ROUTE (old)
# @listings.route("/", methods=["GET"])
# def listings_data():
#     with connection:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM listings")
#             # transform result
#             columns = list(cursor.description)
#             result = cursor.fetchall()
#             # make dict
#             results = []
#             for row in result:
#                 row_dict = {}
#                 for i, col in enumerate(columns):
#                     row_dict[col.name] = row[i]
#                 results.append(row_dict)
#             return results

# GET ALL ROUTE (new) with shoe and user details(remove password KIV)
@listings.route("/", methods=["GET"])
def listings_data():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM listings l JOIN shoes s ON l.shoe_id = s.shoe_id JOIN users u ON l.user_listing_id = u.user_id;")
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

# GET ALL FOR SPECIFIC USER
@listings.route("user/<id>", methods=["GET"])
def listings_user_data(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM listings l JOIN shoes s ON l.shoe_id = s.shoe_id JOIN users u ON l.user_listing_id = u.user_id WHERE l.user_listing_id = {id};")
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

# # READ ROUTE(old)
# @listings.route("/<id>", methods=["GET"])
# def one_listing_data(id):
#     results = []
#     with connection:
#         with connection.cursor() as cursor:
#             cursor.execute(f"SELECT * FROM listings WHERE listing_id='{id}'")
#             # result = cursor.fetchone()[0]
#             columns = list(cursor.description)
#             result = cursor.fetchall()
#             # make dict
#             results = []
#             for row in result:
#                 row_dict = {}
#                 for i, col in enumerate(columns):
#                     row_dict[col.name] = row[i]
#                 results.append(row_dict)
#             return results

# READ ROUTE(new)
@listings.route("/<id>", methods=["GET"])
def one_listing_data(id):
    results = []
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM listings l JOIN shoes s ON l.shoe_id = s.shoe_id JOIN users u ON l.user_listing_id = u.user_id WHERE listing_id='{id}';")
            # result = cursor.fetchone()[0]
            columns = list(cursor.description)
            result = cursor.fetchall()
            # make dict
           
            for row in result:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col.name] = row[i]
                
            return row_dict

# UPDATE ROUTE
@listings.route("/<id>", methods=["PUT"])
def update_one_listing(id):
    data = request.get_json()
    data_values = list(data.values())
    data_values.append(id)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE listings SET listing_price=%s,shoe_id=%s,sold=%s,user_listing_id=%s WHERE listing_id=%s",
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
