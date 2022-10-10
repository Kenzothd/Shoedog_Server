import os
import psycopg2
from flask import Blueprint, request
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env file into environment
users = Blueprint("users", __name__)
url = os.environ.get("DATABASE_URL")
connection = psycopg2.connect(url)

# CREATE ROUTE
@users.route("/", methods=["POST"])
def new_user():
    data = request.get_json()
    data_values = list(data.values())
    email = data["email"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (first_name,last_name,email,password,country,verified) VALUES (%s,%s,%s,%s,%s,%s) ",
                data_values,
            )
    return {"status": f"User {email} created"}, 201


# GET ALL ROUTE
@users.route("/", methods=["GET"])
def users_data():

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            # transform result
            columns = list(cursor.description)
            result = cursor.fetchall()
            print(result)
            # make dict
            results = []
            for row in result:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col.name] = row[i]
                results.append(row_dict)
            return results


# READ ROUTE
@users.route("/<id>", methods=["GET"])
def one_user_data(id):
    results = []
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users WHERE user_id='{id}'")
            # result = cursor.fetchone()[0]
            columns = list(cursor.description)
            result = cursor.fetchall()
            print(result)
            # make dict
            results = []
            for row in result:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col.name] = row[i]
                results.append(row_dict)
            return results


# UPDATE ROUTE
@users.route("/<id>", methods=["PUT"])
def update_one_user(id):
    data = request.get_json()
    data_values = list(data.values())
    data_values.append(id)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET first_name=%s,last_name=%s,email=%s,password=%s,country=%s,verified=%s WHERE user_id=%s",
                data_values,
            )
            return {"msg": f"User id {id} updated"}


# DELETE ROUTE
@users.route("/<id>", methods=["DELETE"])
def del_one_user(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM users WHERE user_id='{id}'")
            # columns = list(cursor.description)
            # result = cursor.fetchall()
            # results = []
            # for row in result:
            #     row_dict = {}
            #     for i, col in enumerate(columns):
            #         row_dict[col.name] = row[i]
            #         results.append(row_dict)
            return {"msg": f"User id {id} deleted"}, 200
