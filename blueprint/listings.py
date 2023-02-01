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

# GET ALL ROUTE (new) if sold = true with volume of one year
@listings.route("/volume/<time>-year", methods=["GET"])
def listings_data_volume_year(time):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT listings.shoe_id, shoe_brand, shoe_img, shoe_model, MIN(listing_price) as lowest_listing_price, SUM(listing_price) as total_volume FROM listings JOIN shoes ON listings.shoe_id = shoes.shoe_id WHERE sold = true AND listing_date_close >= NOW() - INTERVAL '{time} year' AND listing_date_close < NOW() GROUP BY listings.shoe_id, shoe_brand, shoe_img, shoe_model ORDER BY total_volume DESC;"
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


# GET ALL ROUTE (new) if sold = true with volume of <time> month
@listings.route("/volume/<time>-month", methods=["GET"])
def listings_data_volume_month(time):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT listings.shoe_id, shoe_brand, shoe_img, shoe_model, MIN(listing_price) as lowest_listing_price, SUM(listing_price) as total_volume FROM listings JOIN shoes ON listings.shoe_id = shoes.shoe_id WHERE sold = true AND listing_date_close >= NOW() - INTERVAL '{time} month' AND listing_date_close < NOW() GROUP BY listings.shoe_id, shoe_brand, shoe_img, shoe_model ORDER BY total_volume DESC;"
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


# GET ALL sold = true listings FOR SPECIFIC shoe, 1 Month(8 hour average = abt 90 data for 1 month)
@listings.route("/true/<id>/one-month", methods=["GET"])
def listings_data_sold_true_one_month(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"WITH eight_hour_intervals AS (SELECT listing_start_date::timestamp without time zone FROM ( SELECT * FROM generate_series( date_trunc('hour', NOW() - INTERVAL '1 month'), NOW(), concat(480, ' minutes')::interval) as t(listing_start_date)) as t WHERE t.listing_start_date between NOW() - INTERVAL '1 month' and NOW()) SELECT listing_start_date, ROUND(AVG(listing_price)) AS avg_listing_price  FROM  eight_hour_intervals  LEFT JOIN listings ON listing_start_date <= listing_date_close AND listing_date_close < listing_start_date + INTERVAL '8 hour' AND shoe_id = '{id}' AND sold = true GROUP BY listing_start_date HAVING AVG(listing_price) IS NOT NULL ORDER BY listing_start_date ASC;"
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
                f"SELECT date_trunc('day', listing_date_close) as listing_start_date, ROUND(AVG(listing_price)) as avg_listing_price FROM listings WHERE shoe_id = '{id}' AND sold = true AND listing_date_close >= NOW() - INTERVAL '3 month' AND listing_date_close <= NOW() GROUP BY listing_start_date ORDER BY listing_start_date ASC;"
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
                f"WITH two_day_intervals AS (SELECT date_trunc('day', NOW() - INTERVAL '6 month') + (generate_series * 2 || ' day')::interval AS listing_start_date FROM generate_series(0, extract(day from NOW() - date_trunc('day', NOW() - INTERVAL '6 month')) / 2) ) SELECT listing_start_date::date, ROUND(AVG(listing_price)) AS avg_listing_price FROM two_day_intervals LEFT JOIN listings ON listing_start_date <= listing_date_close AND listing_date_close < listing_start_date + INTERVAL '2 day' AND shoe_id = 1 AND sold = true GROUP BY listing_start_date HAVING AVG(listing_price) IS NOT NULL ORDER BY listing_start_date ASC;"
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
                f"WITH four_day_intervals AS (SELECT date_trunc('day', NOW() - INTERVAL '1 year') + (generate_series * 4 || ' day')::interval AS listing_start_date FROM generate_series(0, extract(day from NOW() - date_trunc('day', NOW() - INTERVAL '1 year')) / 4)) SELECT listing_start_date::date, ROUND(AVG(listing_price)) AS avg_listing_price FROM four_day_intervals LEFT JOIN listings ON listing_start_date <= listing_date_close AND listing_date_close < listing_start_date + INTERVAL '4 day' AND shoe_id = 1 AND sold = true GROUP BY listing_start_date HAVING AVG(listing_price) IS NOT NULL ORDER BY listing_start_date ASC;"
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


# GET ALL sold = true listings FOR SPECIFIC shoe, ALL time(7 day average, 1Y = abt 52 data)
@listings.route("/true/<id>/all", methods=["GET"])
def listings_data_sold_true_all(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"WITH seven_day_intervals AS (SELECT generate_series(date_trunc('day', MIN(listing_date_close)), date_trunc('day', NOW()), '7 day')::date AS listing_start_date FROM listings) SELECT listing_start_date, ROUND(AVG(listing_price)) AS avg_listing_price FROM seven_day_intervals LEFT JOIN listings ON listing_start_date <= listing_date_close AND listing_date_close < listing_start_date + INTERVAL '7 day' AND shoe_id = 1 AND sold = true GROUP BY listing_start_date HAVING AVG(listing_price) IS NOT NULL ORDER BY listing_start_date ASC;"
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
