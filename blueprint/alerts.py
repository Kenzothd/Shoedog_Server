import os
import psycopg2
from flask import Blueprint, request
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()  # loads variables from .env file into environment
alerts = Blueprint("alerts", __name__)
CORS(alerts)
url = os.environ.get("DATABASE_URL")
connection = psycopg2.connect(url)

# CREATE ROUTE (OLD)
# @alerts.route("/", methods=["POST"])
# def new_alert():
#     data = request.get_json()
#     data_values = list(data.values())
#     with connection:
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "INSERT INTO alerts (alert_price,shoe_id,user_id) VALUES (%s,%s,%s)",
#                 data_values,
#             )
#     return {"status": f"Alert created"}, 201

# CREATE ROUTE (NEW)
@alerts.route("/<id>", methods=["POST"])
def new_alert(id):
    data = request.get_json()
    shoe_brand = data["shoe_brand"]
    shoe_model= data["shoe_model"]
    shoe_size= data["shoe_size"]
    alert_price= data["alert_price"]
    with connection:
         try: 
            with connection.cursor() as cursor:
                cursor.execute(f"WITH rows AS (SELECT shoe_id FROM shoes WHERE shoe_brand='{shoe_brand}' AND shoe_model='{shoe_model}' AND shoe_size='{shoe_size}') INSERT INTO alerts (user_id,shoe_id,alert_price) SELECT '{id}',shoe_id,'{alert_price}' FROM rows RETURNING alerts.*;")
            return {"status": f"Alert created"}, 201
         except Exception as error:
                return {"error": f"{error}"}, 400


# GET ALL ROUTE
@alerts.route("/", methods=["GET"])
def alerts_data():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM alerts")
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


# READ ROUTE(OLD)
# @alerts.route("/<id>", methods=["GET"])
# def one_listing_data(id):
#     results = []
#     with connection:
#         with connection.cursor() as cursor:
#             cursor.execute(f"SELECT * FROM alerts WHERE alert_id='{id}'")
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

# READ ROUTE (NEW)
@alerts.route("/<id>", methods=["GET"])
def one_listing_data(id):
    results = []
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM alerts a JOIN shoes s ON s.shoe_id = a.shoe_id JOIN users u ON a.user_id = u.user_id WHERE a.user_id='{id}'")
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
@alerts.route("/<id>", methods=["PUT"])
def update_one_alert(id):
    data = request.get_json()
    data_values = list(data.values())
    data_values.append(id)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE alerts SET alert_price=%s,shoe_id=%s,user_id=%s WHERE alert_id=%s",
                data_values,
            )
        return {"msg": f"Alert id {id} updated"}


# DELETE ROUTE
@alerts.route("/<id>", methods=["DELETE"])
def del_one_alert(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM alerts WHERE alert_id='{id}'")
            return {"msg": f"Alert id {id} deleted"}, 200
