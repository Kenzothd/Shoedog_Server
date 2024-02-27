import os
import psycopg2
from flask import Blueprint, request
from dotenv import load_dotenv
from flask_cors import CORS


load_dotenv()  # loads variables from .env file into environment
shoes = Blueprint("shoes", __name__)
CORS(shoes)
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
def one_shoe_data(id):
    results = []
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"WITH all_time_query AS (SELECT shoes.shoe_id,shoes.shoe_brand,shoes.shoe_model,shoes.shoe_description,shoes.shoe_img,shoes.shoe_likes,shoes.shoe_release_date,shoes.shoe_retail_price,MIN(listing_price) AS all_time_lowest_listing_price, MAX(listing_price) AS all_time_highest_listing_price, ROUND((AVG(listing_price))) AS average_listing_price, ROUND(STDDev(listing_price)) AS volatility, COUNT(listing_price) AS number_of_sales,  MAX(listing_price) FILTER (WHERE listing_date_close = (SELECT MAX(listing_date_close) FROM listings WHERE sold = true)) AS last_sale_price FROM shoes JOIN listings ON shoes.shoe_id = listings.shoe_id WHERE shoes.shoe_id ='{id}' AND listing_date_close < NOW() GROUP BY shoes.shoe_id, shoes.shoe_brand, shoes.shoe_model) SELECT all_time_query.*,MIN(listing_price) FILTER (WHERE listing_date_close >=  NOW() - INTERVAL '1 year') AS one_year_lowest_listing_price,MAX(listing_price) FILTER (WHERE listing_date_close >=  NOW() - INTERVAL '1 year') AS one_year_highest_listing_price FROM all_time_query JOIN listings ON all_time_query.shoe_id = listings.shoe_id GROUP BY all_time_query.shoe_id, all_time_query.shoe_brand, all_time_query.shoe_model, all_time_query.shoe_description, all_time_query.shoe_img, all_time_query.shoe_likes, all_time_query.shoe_release_date, all_time_query.shoe_retail_price, all_time_query.all_time_lowest_listing_price, all_time_query.all_time_highest_listing_price, all_time_query.average_listing_price, all_time_query.volatility, all_time_query.number_of_sales,  all_time_query.last_sale_price;"
            )
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
