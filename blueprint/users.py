import os
from tkinter import EXCEPTION
import psycopg2
from flask import Blueprint, request
from dotenv import load_dotenv
from flask_cors import CORS


load_dotenv()  # loads variables from .env file into environment
users = Blueprint("users", __name__)
CORS(users)
url = os.environ.get("DATABASE_URL")
connection = psycopg2.connect(url)

# CREATE ROUTE
@users.route("/", methods=["POST"])
def new_user():
    data = request.get_json()
    print(data)
    data_values = list(data.values())
    print("data_values", data_values)
    email = data["email"]
    with connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO users (first_name,last_name,email,password,country) VALUES (%s,%s,%s,%s,%s) ",
                    data_values,
                )
                return {"status": f"User {email} created"}, 201
            except Exception as error:
                return {"error": f"{error}"}, 400


# GET ALL ROUTE
@users.route("/", methods=["GET"])
def users_data():

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
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
@users.route("/<id>", methods=["GET"])
def one_user_data(id):
    results = []
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users WHERE user_id='{id}'")
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


# Find by username
@users.route("/findbyusername/<username>", methods=["GET"])
def one_user_username(username):
    results = []
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT user_id, username, first_name, last_name, country,verified, followings, followers, joined_date FROM users WHERE username = '{username}';"
            )
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


# Find by email
@users.route("/findbyemail/<email>", methods=["GET"])
def one_user_email(email):
    results = []
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT email FROM users WHERE email='{email}'")
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


# Verify login
@users.route("/login", methods=["POST"])
def verify_user():
    data = request.get_json()
    data_values = list(data.values())
    email = data["email"]
    with connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT user_id, email, password FROM users WHERE email=%s AND password=%s",
                    data_values,
                )
                result = cursor.fetchall()
                id = result[0][0]
                return {"id": f"{id}", "msg": f"User {email} logged in!"}, 200
            except Exception as error:
                return {"error": f"{error}"}, 400


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
