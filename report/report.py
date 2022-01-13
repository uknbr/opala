#!/usr/bin/env python3
# coding: utf-8
__author__ = "uknbr"

#pip install mysql-connector-python
from mysql.connector import connect, Error

try:
    with connect(
        host="localhost",
        port=8084,
        user="car",
        password="Olx@123",
        database="olx",
    ) as connection:
        mycursor = connection.cursor()

        # Total executions
        mycursor.execute("select count(1) from status")
        status_count = mycursor.fetchone()[0]

        # Offer count
        mycursor.execute("select count(1) from offer")
        offer_count = mycursor.fetchone()[0]

        # Average price
        mycursor.execute("select format(avg(price),2) from offer where price > 1000 and price < 1000000")
        price_avg = mycursor.fetchone()[0]

        # Average score
        mycursor.execute("select format(avg(score),1) from score")
        score_avg = mycursor.fetchone()[0]

        # Recommendation
        mycursor.execute("select code from score order by score desc limit 1")
        offer_best = mycursor.fetchone()[0]

        # Show
        print(f"\nNro de pesquisas: {status_count}\nNro de anuncios: {offer_count}\nMedia de preço: R$ {price_avg}\nMedia de pontos: {score_avg}\nAnucio destaque: https://www.olx.com.br/vi/{offer_best}")

except Error as e:
    print(e)
