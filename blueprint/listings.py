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
    shoe_model = data["shoe_model"]
    shoe_size = data["shoe_size"]
    listing_price = data["listing_price"]
    with connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"WITH rows AS (SELECT shoe_id FROM shoes WHERE shoe_brand='{shoe_brand}' AND shoe_model='{shoe_model}' AND shoe_size='{shoe_size}') INSERT INTO listings (user_listing_id,shoe_id,listing_price) SELECT '{id}',shoe_id,'{listing_price}' FROM rows RETURNING listings.*;"
                )
                results = []
                check_alert(cursor, results)
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

# GET ALL ROUTE (new) if sold = true with volume of ALl,1D,1M,1Y
@listings.route("/volume", methods=["GET"])
def listings_data_volume():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "WITH volumes AS (SELECT shoe_id, SUM(CASE WHEN listing_date_close >= NOW() - INTERVAL '1 month' AND listing_date_close < NOW() THEN listing_price ELSE 0 END) as one_month_total_volume,SUM(CASE WHEN listing_date_close >= NOW() - INTERVAL '3 month' AND listing_date_close < NOW() THEN listing_price ELSE 0 END) as three_month_total_volume,SUM(CASE WHEN listing_date_close >= NOW() - INTERVAL '6 month' AND listing_date_close < NOW() THEN listing_price ELSE 0 END) as six_month_total_volume, SUM(CASE WHEN listing_date_close >= NOW() - INTERVAL '1 year' AND listing_date_close < NOW() THEN listing_price ELSE 0 END) as one_year_total_volume FROM listings WHERE listing_date_close < NOW()GROUP BY shoe_id)SELECT main.shoe_id, sub.shoe_brand, sub.shoe_model, sub.shoe_img, main.lowest_listing_price, main.total_volume, volumes.one_month_total_volume, volumes.three_month_total_volume, volumes.six_month_total_volume, volumes.one_year_total_volume FROM shoes sub JOIN (SELECT shoe_id, MIN(listing_price) as lowest_listing_price, SUM(listing_price) as total_volume FROM listings WHERE listing_date_close < NOW() GROUP BY shoe_id) main ON main.shoe_id = sub.shoe_id JOIN volumes ON volumes.shoe_id = main.shoe_id ORDER BY main.total_volume DESC;"
            )
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


# GET ALL sold = false listings FOR SPECIFIC shoe, ALL time
@listings.route("/false/<id>/all", methods=["GET"])
def listings_data_sold_false_all(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT listings.*, users.username,users.verified FROM listings JOIN users  ON listings.user_id = users.user_id WHERE listings.SHOE_ID = '{id}'  AND listings.listing_date < NOW() AND listings.sold = FALSE  ORDER BY listings.listing_date DESC;"
            )
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


# GET ALL sold = true listings FOR SPECIFIC shoe, ALL time
@listings.route("/true/<id>/all", methods=["GET"])
def listings_data_sold_true_all(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT listing_price,listing_date_close from listings WHERE shoe_id = '{id}' AND sold = true AND listing_date_close < NOW() ORDER BY listing_date_close DESC;"
            )
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


# GET ALL sold = true listings FOR SPECIFIC shoe, 3 Month(1 day average = abt 90 data)
@listings.route("/true/<id>/three-month", methods=["GET"])
def listings_data_sold_true_three_month(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT date_trunc('day', listing_date_close) as date, ROUND(AVG(listing_price)) as avg_price FROM listings WHERE shoe_id = '{id}' AND sold = true AND listing_date_close >= NOW() - INTERVAL '3 month' AND listing_date_close < NOW() GROUP BY date ORDER BY date DESC;"
            )
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


# GET ALL sold = true listings FOR SPECIFIC shoe, 6 Month(2 day average = abt 90 data)
@listings.route("/true/<id>/six-month", methods=["GET"])
def listings_data_sold_true_six_month(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"WITH two_day_intervals AS (SELECT date_trunc('day', NOW() - INTERVAL '6 month') + (generate_series * 2 || ' day')::interval AS two_day_start FROM generate_series(0, extract(day from NOW() - date_trunc('day', NOW() - INTERVAL '6 month')) / 2)) SELECT two_day_start::date, ROUND(AVG(listing_price), 2) AS avg_listing_price FROM two_day_intervals LEFT JOIN listings ON two_day_start <= listing_date_close AND listing_date_close < two_day_start + INTERVAL '2 day' AND shoe_id = '{id}' AND sold = true GROUP BY two_day_start HAVING AVG(listing_price) IS NOT NULL ORDER BY two_day_start DESC;"
            )
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


# GET ALL sold = true listings FOR SPECIFIC shoe, 1 Year(4 day average = abt 91 data)
@listings.route("/true/<id>/one-year", methods=["GET"])
def listings_data_sold_true_one_year(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"WITH two_day_intervals AS (SELECT date_trunc('day', NOW() - INTERVAL '1 year') + (generate_series * 4 || ' day')::interval AS two_day_start FROM generate_series(0, extract(day from NOW() - date_trunc('day', NOW() - INTERVAL '1 year')) / 4)) SELECT two_day_start::date, ROUND(AVG(listing_price), 4) AS avg_listing_price FROM two_day_intervals LEFT JOIN listings ON two_day_start <= listing_date_close AND listing_date_close < two_day_start + INTERVAL '4 day' AND shoe_id = '{id}' AND sold = true GROUP BY two_day_start HAVING AVG(listing_price) IS NOT NULL ORDER BY two_day_start DESC;"
            )
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
            cursor.execute(
                f"SELECT * FROM listings l JOIN shoes s ON l.shoe_id = s.shoe_id JOIN users u ON l.user_listing_id = u.user_id WHERE l.user_listing_id = {id};"
            )
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
            cursor.execute(
                f"SELECT * FROM listings l JOIN shoes s ON l.shoe_id = s.shoe_id JOIN users u ON l.user_listing_id = u.user_id WHERE listing_id='{id}';"
            )
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
