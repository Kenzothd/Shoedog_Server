import os
import psycopg2
from flask import Blueprint, request
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env file into environment
alerts = Blueprint("alerts", __name__)
url = os.environ.get("DATABASE_URL")
connection = psycopg2.connect(url)

# CREATE ROUTE
@alerts.route("/", methods=["POST"])
def new_alert():
    data = request.get_json()
    data_values = list(data.values())
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO alerts (alert_price,shoe_id,user_id) VALUES (%s,%s,%s)",
                data_values,
            )
    return {"status": f"Alert created"}, 201


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


# READ ROUTE
@alerts.route("/<id>", methods=["GET"])
def one_listing_data(id):
    results = []
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM alerts WHERE alert_id='{id}'")
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
