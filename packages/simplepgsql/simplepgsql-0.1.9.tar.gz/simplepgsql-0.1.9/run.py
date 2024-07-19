import os
import pandas as pd
from simplepgsql import SimplePgSQL
from simplepgsql import Query
from simplepgsql import Params as Par
from simplepgsql import StandardKeywords as sk
import configparser

if __name__ == "__main__":
    # read data from config file
    config = configparser.ConfigParser()
    config.read("config.ini")
    conn_params = {
        "host": config['DB']['DB_HOST'],
        "database": config['DB']['DB_NAME'],
        "user": config['DB']['DB_USER'].strip(),
        "password": config['DB']['DB_PASSWORD'].strip(),
        "port": config['DB']['DB_PORT'],
    }

    _query_params = {
        Par.schema: "public",
        Par.table: "film_list",
        Par.columns: ["category", "price"],
        Par.aggregate: {
            "price": "SUM"
        },
        Par.conditions: {
            "length": (">", 60)
        },
        Par.order_by: {"price": sk.DESCENDING},
        Par.group_by: ["category", "price"],
        Par.limit: 10,
    }

    _query = Query(**_query_params)
    # data =
    # Using SimplePgSQL class
    pgsql = SimplePgSQL(conn_params, return_type=pd.DataFrame)
    data = pgsql.execute(_query.build(), columns=["category", "price"])
    print(data)
    # _query = """
    #         SELECT category, SUM(price)
    #         FROM public.film_list
    #         WHERE length > 60
    #         GROUP BY category, price
    #         ORDER BY price DESC
    #         LIMIT 10;
    #         """

    # q_results = pgsql.execute(_query, columns=["category", "price"])
    # r_results = pgsql.read(**_query_params)
    # print(q_results)
    # print(r_results)

    # Deprecated method to query data DO NOT USE. For backward compatibility only
    # with DBConnect(conn_params, return_type=pd.DataFrame) as cursor:
    #     q_results = cursor.query("SELECT category, price FROM film_list LIMIT 10;", columns=["category", "price"])
    #     _query_params.pop("table")
    #     _query_params["table_name"] = "film_list"
    #     r_results = cursor.read(**_query_params)
    #     print(r_results)
    #     print(q_results)
