#!/usr/bin/env python3
# coding: utf-8
__author__ = "uknbr"

import sys
import requests
import urllib3
from bs4 import BeautifulSoup
from urlextract import URLExtract
import json
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, select
from sqlalchemy.sql import func
import string
import re
import datetime
from pathlib import Path
from hashlib import md5
from prettytable import PrettyTable
import paho.mqtt.client as mqtt
import time
import os
import argparse
import logging
from dotenv import load_dotenv
from colorama import init, Fore, Back, Style

""" Config """
class setup:
    WIN_CONFIG_FILE = "olx.ini"
    WIN_URL_CACHE_FILE = "tlds-alpha-by-domain.txt"
    WIN_URL_CACHE_DIR = ".\\urlextract\\data\\"

""" Colors & Terminal """
init()
def clear():
    # windows
    if os.name == "nt":
        _ = os.system("cls")
    # mac and linux
    else:
        _ = os.system("clear")


""" Functions """
def get_km(value):
    options = []
    options.append(5)                   # 5.000
    for num in range(10, 50, 10):       # 10.000 - 40.000
        options.append(num)
    for num in range(60, 220, 20):      # 60.000 - 200.000
        options.append(num)
    options.append(250)                 # 250.000
    for num in range(300, 600, 100):    # 300.000 - 500.000
        options.append(num)

    if int(value/1000) in options:
        return True
    else:
        logger.error(f"Invalid KM: {value}")
        for key in options:
            print(f"{key}.000", end=" | ")
        raise SystemExit(f"\nKM '{value}' is not valid!")


def get_region(value):
    options = {
        "ac": "AC",
        "al": "AL",
        "ap": "AP",
        "am": "AM",
        "ba": "BA",
        "ce": "CE",
        "df": "DF",
        "es": "ES",
        "go": "GO",
        "ma": "MA",
        "mt": "MT",
        "ms": "MS",
        "mg": "MG",
        "pa": "PA",
        "pb": "PB",
        "pr": "PR",
        "pe": "PE",
        "pi": "PI",
        "rj": "RJ",
        "rn": "RN",
        "rs": "RS",
        "ro": "RO",
        "rr": "RR",
        "sc": "SC",
        "sp": "SP",
        "se": "SE",
        "to": "TO",
        "br": "BR",
    }

    try:
        result = options[value]
        return result
    except KeyError:
        logger.error(f"Invalid region: {value}")
        for key in options.keys():
            print(key, end=" | ")
        raise SystemExit(f"\nRegion '{value}' is not valid!")


def get_year(value):
    options = {
        1950: 0,
        1955: 1,
        1960: 2,
        1965: 3,
        1970: 4,
        1975: 5,
        1980: 6,
        1985: 7,
        1990: 8,
        1991: 9,
        1992: 10,
        1993: 11,
        1994: 12,
        1995: 13,
        1996: 14,
        1997: 15,
        1998: 16,
        1999: 17,
        2000: 18,
        2001: 19,
        2002: 20,
        2003: 21,
        2004: 22,
        2005: 23,
        2006: 24,
        2007: 25,
        2008: 26,
        2009: 27,
        2010: 28,
        2011: 29,
        2012: 30,
        2013: 31,
        2014: 32,
        2015: 33,
        2016: 34,
        2017: 35,
        2018: 36,
        2019: 37,
        2020: 38,
        2021: 39,
        2022: 40,
    }

    try:
        result = options[value]
        return result
    except KeyError:
        logger.error(f"Invalid year: {value}")
        for key in options.keys():
            print(key, end=" | ")
        raise SystemExit(f"\nYear '{value}' is not valid!")


def telegram_bot_send_text(message):
    if telegram_enable:

        items = {
            "chat_id": telegram_chat,
            "parse_mode": "Markdown",
            "disable_notification": "false",
            "text": message,
        }

        try:
            send_text = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            response = requests.get(send_text, params=items, verify=ssl_verify)
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram message: {e.strerror}")
            return False

        if response.status_code != 200:
            logger.error("Failed to send notification to Telegram")
            return False


def score_by_year(year):
    result = 0
    for value in car_score_year.split(","):
        if int(value) == int(year):
            result += 1
            logger.debug(f"<+> SCORE (year) = {year} [{value}]")
        else:
            logger.debug(f"<=> SCORE (year) = {year} [{value}]")
    return result


def score_by_color(color):
    result = 0
    for value in car_score_color.split(","):
        if str.lower(value) == str.lower(color):
            result += 1
            logger.debug(f"<+> SCORE (color) = {color} [{value}]")
        else:
            logger.debug(f"<=> SCORE (color) = {color} [{value}]")
    return result


def score_by_doors(doors):
    result = 0
    if int(car_score_door) == int(doors):
        result += 1
        logger.debug(f"<+> SCORE (doors) = {doors} [{car_score_door}]")
    else:
        logger.debug(f"<=> SCORE (doors) = {doors} [{car_score_door}]")
    return result


def score_by_fuel(fuel):
    result = 0
    if str.lower(car_score_fuel).replace("á","a") == str.lower(fuel):
        result += 1
        logger.debug(f"<+> SCORE (fuel) = {fuel} [{car_score_fuel}]")
    else:
        logger.debug(f"<=> SCORE (fuel) = {fuel} [{car_score_fuel}]")
    return result


def score_by_tranmission(transmission):
    result = 0
    if str.lower(car_score_transmission) == str.lower(transmission):
        result += 1
        logger.debug(f"<+> SCORE (transmission) = {transmission} [{car_score_transmission}]")
    else:
        logger.debug(f"<=> SCORE (transmission) = {transmission} [{car_score_transmission}]")
    return result


def score_by_price(price):
    result = 0
    if int(price) <= int(car_score_price):
        if int(price) > 0:
            result += 1
            logger.debug(f"<+> SCORE (price) = {price} [{car_score_price}]")
        else:
            logger.debug(f"<=> SCORE (price) = {price} [{car_score_price}]")
    return result


def score_by_keyword(name, desc):
    result = 0
    for value in car_score_keyword.split(","):
        if str.lower(value) in str.lower(name):
            result += 1
            logger.debug(f"<+> SCORE (keyword - name) = {value} [{name}]")
        else:
            logger.debug(f"<=> SCORE (keyword - name) = {value} [{name}]")

        if str.lower(value) in str.lower(desc):
            result += 1
            logger.debug(f"<+> SCORE (keyword - desc) = {value} [{desc}]")
        else:
            logger.debug(f"<=> SCORE (keyword - desc) = {value} [{desc}]")
    return result


def score_by_km(km):
    result = 0
    if int(km) <= int(car_score_km):
        if int(km) > 1:
            result += 1
            logger.debug(f"<+> SCORE (km) = {km} [{car_score_km}]")
        else:
            logger.debug(f"<=> SCORE (km) = {km} [{car_score_km}]")
    return result


def request_web(page, url):
    items = {
        "re": car_re,
        "rs": car_rs
    }

    if page > 1:
        logger.debug(f"Request (page): {page}")
        items["o"] = page

    if car_query:
        logger.debug(f"Request (query): {car_query}")
        items["q"] = car_query
        items["ot"] = 1

    if car_km_check:
        logger.debug(f"Request (km): {car_km}")
        items["me"] = car_km

    try:
        logger.debug(f"Request (url): {url}")
        response = requests.get(
            url,
            verify=ssl_verify,
            params=items,
            headers={
                "authority": f"{car_region}olx.com.br",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
                "sec-fetch-dest": "document",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "navigate",
                "sec-fetch-user": "?1",
                "referer": f"https://{car_region}olx.com.br/autos-e-pecas",
                "accept-language": "en-US,en;q=0.9,pt;q=0.8",
            },
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"OLX page: {e}")
        raise SystemExit("HTTP request failed, please check the log")
    return response


def update_mqtt(topic, value):
    if mqtt_enable:
        try:
            client = mqtt.Client()
            client.connect(mqtt_host, mqtt_port, 60)
            client.publish(f"{mqtt_host}/{car_model}/{topic}", value, retain=True)
            logger.debug(f"MQTT ({topic}): {value}")
        except Exception as e:
            logger.error(f"MQTT error: {repr(e)}")


def get_datetime_epoch():
    return int(datetime.datetime.now().timestamp())


def extract_url():
    url_list = []

    for st in car_region.split(","):
        index = 0
        item = 0

        while True:
            if st == "br":
                target_region = ""
            else:
                target_region = f"{st}."

            index += 1

            response = request_web(
                index,
                f"https://{target_region}olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/{car_brand}/{car_model}",
            )

            if response.status_code == 200:
                response.encoding = "utf-8"

                if not args.q:
                    print(f"Loading page {index}", end="\r")
                logger.info(f"Parsing page {index} [{st}]")

                html = response.text
                html = html.replace(" ", "").replace("=", "").replace("&quot", "")

                """ URL cache (windows only) """
                if os.name == "nt":
                    logger.info(f"Windows platform detected")
                    logger.debug(f"Current directory: {os.getcwd()}")
                    logger.debug(f"Create URL cache directory {setup.WIN_URL_CACHE_DIR}")
                    Path(f"{setup.WIN_URL_CACHE_DIR}").mkdir(parents=True, exist_ok=True)
                    if os.path.isfile(setup.WIN_URL_CACHE_FILE):
                        with open(setup.WIN_URL_CACHE_FILE, "r") as infile:
                            content = infile.read()
                            with open(f"{setup.WIN_URL_CACHE_DIR}{setup.WIN_URL_CACHE_FILE}", "w") as outfile:
                                outfile.write(content)
                    else:
                        logger.error(f"File not found: {setup.WIN_URL_CACHE_FILE}")
                        raise SystemExit("Windows requires cache dir/file")

                extractor = URLExtract()
                href = []

                for url in extractor.find_urls(html):
                    if "autos-e-pecas/carros-vans-e-utilitarios" in url:
                        if str.isdigit(url.split("-")[-1]):
                            href.append(url)

                if len(href) == 0:
                    if item > 0:
                        if not args.q:
                            print(f"Completed with success! [{st}]")
                        logger.info(f"Loaded all pages: {item} [{st}]")
                    else:
                        if not args.q:
                            print(f"Car was not found [{st}]")
                        logger.warning("Car code was not found [{st}]")
                    break
                else:
                    item += 1

                for url in href:
                    url_list.append(url)
            else:
                print("Failed to get URL")
                logger.error(f"Error response from server:\n{response.content}")
                sys.exit(1)

    url_list = list(dict.fromkeys(url_list))
    return url_list


def get_car(car):
    response = request_web(1, car)

    if response.status_code == 200:
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            car_info = soup.find("script", type="application/ld+json")
            json_string = str(car_info.contents[0])
            offer = json.loads(json_string)
        except Exception as e:
            logger.error(f"Failed to load offer JSON: {repr(e)}")
            logger.error(json_string)
            return -1

        with open(f"{base_path}olx/tmp/offer.json", "w") as outfile:
            json.dump(offer, outfile)
            logger.debug("Saved json file: offer")

        for ad in soup.find_all("script"):
            if "pageType" in str(ad):
                try:
                    ad_string = str(ad)
                    json_string = ad_string[ad_string.find("[")+len("["):ad_string.rfind("]")]
                    details = json.loads(json_string)
                except Exception as e:
                    logger.error(f"Failed to load details JSON: {repr(e)}")
                    logger.error(ad_string)
                    return -1

                with open(f"{base_path}olx/tmp/details.json", "w") as outfile:
                    json.dump(details, outfile)
                    logger.debug("Saved json file: details")

                """ Values """
                logger.debug("Checking json values")
                _code = details["page"]["adDetail"]["listId"]
                _numberOfDoors = offer["makesOffer"]["itemOffered"].get(
                    "numberOfDoors", 0
                )
                _numberOfDoors = int(re.findall("\d+", str(_numberOfDoors))[0])
                _vehicleTransmission = offer["makesOffer"]["itemOffered"].get(
                    "vehicleTransmission", "N/A"
                )
                _modelDate = offer["makesOffer"]["itemOffered"]["modelDate"]
                _fuelType = offer["makesOffer"]["itemOffered"].get("fuelType", "N/A")
                _bodyType = offer["makesOffer"]["itemOffered"].get("bodyType", "N/A")
                _mileage = offer["makesOffer"]["itemOffered"].get("mileageFromOdometer", 0)
                _state = details["page"]["adDetail"]["state"]
                _carColor = details["page"]["adDetail"].get("carcolor", "N/A")
                _endTag = details["page"]["adDetail"].get("end_tag", -1)
                _price = details["page"]["detail"].get("price", 0)
                if not _price:
                    _price = 0

                sql = table_offer.select().where(table_offer.c.code == _code)
                conn = engine.connect()
                row = conn.execute(sql).fetchone()

                if row is None:
                    logger.info(f"New car ({_code})")

                    """ Directory and files """
                    logger.debug(f"Create offer directory {_code}")
                    Path(f"{base_path}olx/data/{_code}").mkdir(
                        parents=True, exist_ok=True
                    )
                    with open(
                        f"{base_path}olx/data/{_code}/{_code}-offer.json", "w"
                    ) as outfile:
                        json.dump(offer, outfile)
                    with open(
                        f"{base_path}olx/data/{_code}/{_code}-details.json", "w"
                    ) as outfile:
                        json.dump(details, outfile)

                    """ URL """
                    sql = table_url.insert()
                    sql = table_url.insert().values(
                        code=_code, url=car, date=get_datetime_epoch()
                    )
                    conn.execute(sql)
                    logger.debug(f"Added data into table: url")

                    """ Offer """
                    sql = table_offer.insert()
                    sql = table_offer.insert().values(
                        code=_code,
                        owner=offer["name"],
                        price=_price,
                        name=offer["makesOffer"]["itemOffered"]["name"],
                        description=offer["makesOffer"]["itemOffered"]["description"],
                        brand=offer["makesOffer"]["itemOffered"]["brand"],
                        model=offer["makesOffer"]["itemOffered"]["model"],
                        numberOfDoors=_numberOfDoors,
                        modelDate=_modelDate,
                        vehicleTransmission=_vehicleTransmission,
                        fuelType=_fuelType,
                        mileageFromOdometer=_mileage,
                        bodyType=_bodyType,
                        ddd=details["page"]["adDetail"]["ddd"],
                        state=_state,
                        region=details["region"],
                        zipcode=details["page"]["detail"]["zipcode"],
                        pictures=details["pictures"],
                        carColor=_carColor,
                        endTag=_endTag,
                    )
                    conn.execute(sql)
                    logger.debug(f"Added data into table: offer")

                    """ Save images """
                    image_count = 0
                    for img in offer["makesOffer"]["itemOffered"]["image"]:
                        image_count += 1
                        image_url = img["contentUrl"]
                        image_file = (
                            f"{base_path}olx/data/{_code}/{_code}-{image_count}.jpg"
                        )

                        try:
                            file = requests.get(
                                image_url, verify=ssl_verify, allow_redirects=True
                            )
                            open(image_file, "wb").write(file.content)
                        except requests.exceptions.RequestException as e:
                            logger.error(f"Save image: {e.strerror}")
                            raise SystemExit(
                                "HTTP request failed, please check the log"
                            )

                        image_size = Path(image_file).stat().st_size
                        image_hash = md5(Path(image_file).read_bytes()).hexdigest()

                        sql = table_image.insert()
                        sql = table_image.insert().values(
                            code=_code,
                            url=image_url,
                            file=image_file,
                            md5=image_hash,
                            size=image_size,
                        )
                        conn.execute(sql)
                        logger.debug(f"Added data into table: image ({image_file})")

                    """ Define score """
                    car_score = 0
                    car_score = car_score + score_by_year(
                        offer["makesOffer"]["itemOffered"]["modelDate"]
                    )
                    car_score = car_score + score_by_doors(_numberOfDoors)
                    car_score = car_score + score_by_color(_carColor)
                    car_score = car_score + score_by_fuel(_fuelType)
                    car_score = car_score + score_by_tranmission(_vehicleTransmission)
                    car_score = car_score + score_by_price(_price)
                    car_score = car_score + score_by_km(_mileage)
                    car_score = car_score + score_by_keyword(
                        offer["makesOffer"]["itemOffered"]["name"],
                        offer["makesOffer"]["itemOffered"]["description"],
                    )

                    sql = table_score.insert()
                    sql = table_score.insert().values(code=_code, score=car_score)
                    conn.execute(sql)
                    logger.debug(f"Added data into table: score")

                    """ History """
                    sql = table_history.insert().values(
                        code=_code, price=_price, date=get_datetime_epoch()
                    )
                    conn.execute(sql)
                    logger.debug(f"Added data into table (first): history ({_price})")

                    car_offer.add_row(
                        [
                            _code,
                            _price,
                            _state,
                            _modelDate,
                            _fuelType,
                            _carColor,
                            _numberOfDoors,
                            _mileage,
                            car_score,
                            f"{Fore.GREEN}New{Style.RESET_ALL}",
                        ]
                    )

                    """ Telegram """
                    telegram_message = f"Novo anúncio ({car_model}) foi encontrado em {_state}!\nValor: {_price}\nAno: {_modelDate}\nPontos: {car_score}\n{car}"
                    if telegram_bot_send_text(telegram_message):
                        sql = table_notification.insert().values(
                            code=_code,
                            message=re.sub(
                                r"http\S+", "", telegram_message.replace("\n", " ")
                            ),
                            date=get_datetime_epoch(),
                        )
                        conn.execute(sql)
                        logger.debug(f"Added data into table: notification")

                    return 1
                else:
                    _price_current = int(row["price"])

                    """ Already exists - no changes"""
                    if _price_current == int(_price):
                        logger.info(f"Car already exists ({_code})")
                        return 0
                    else:
                        logger.info(
                            f"Car price was updated ({_code}): {_price_current} --> {_price}"
                        )
                        car_offer.add_row(
                            [
                                _code,
                                _price,
                                _state,
                                _modelDate,
                                _fuelType,
                                _carColor,
                                _numberOfDoors,
                                _mileage,
                                "-",
                                f"{Fore.YELLOW}Update{Style.RESET_ALL}",
                            ]
                        )
                        sql = (
                            table_offer.update()
                            .where(table_offer.c.code == _code)
                            .values(price=_price)
                        )
                        conn.execute(sql)
                        logger.debug(f"Updated data into table: offer")

                        """ History """
                        sql = table_history.select().where(
                            table_history.c.code == _code
                        )
                        row = conn.execute(sql).fetchone()

                        if row is None:
                            sql = table_history.insert().values(
                                code=_code,
                                price=_price_current,
                                date=get_datetime_epoch(),
                            )
                            conn.execute(sql)
                            logger.debug(
                                f"Added data into table (first): history ({_price_current})"
                            )
                        sql = table_history.insert().values(
                            code=_code, price=_price, date=get_datetime_epoch()
                        )
                        conn.execute(sql)
                        logger.debug(
                            f"Added data into table (update): history ({_price})"
                        )

                        """ Telegram """
                        telegram_message = f"Anúncio foi atualizado em {_state}!\nValor antigo: {_price_current}\nValor novo: {_price}\n{car}"
                        if telegram_bot_send_text(telegram_message):
                            sql = table_notification.insert().values(
                                code=_code,
                                message=re.sub(
                                    r"http\S+", "", telegram_message.replace("\n", " ")
                                ),
                                date=get_datetime_epoch(),
                            )
                            conn.execute(sql)
                            logger.debug(f"Added data into table: notification")

                        return 2
    else:
        print(f"Failed to get car: {car}")
        logger.error(f"Error response from server:\n{response.content}")
        sys.exit(1)


def get_logger(
    name: str,
    log_file: str = None,
    level=logging.DEBUG,
    formatter=logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"),
):


    fileHandler = logging.FileHandler(f"{base_path}olx/log/car.log")
    fileHandler.setLevel(level)
    fileHandler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(fileHandler)

    return logger


def db_create_table_url():
    table = Table(
        "url",
        meta,
        Column("code", Integer, primary_key=True),
        Column("url", String),
        Column("date", Integer),
    )
    logger.debug("Created table: url")
    return table


def db_create_table_notification():
    table = Table(
        "notification",
        meta,
        Column("code", Integer, primary_key=True),
        Column("message", String),
        Column("date", Integer),
    )
    logger.debug("Created table: notification")
    return table


def db_create_table_history():
    table = Table(
        "history",
        meta,
        Column("id", Integer, primary_key=True),
        Column("code", Integer),
        Column("price", Integer),
        Column("date", Integer),
    )
    logger.debug("Created table: history")
    return table


def db_create_table_status():
    table = Table(
        "status",
        meta,
        Column("id", Integer, primary_key=True),
        Column("duration", Float(2)),
        Column("rate", Float(2)),
        Column("found", Integer),
        Column("update", Integer),
        Column("error", Integer),
        Column("total", Integer),
        Column("region", String(2)),
        Column("date", Integer),
    )
    logger.debug("Created table: status")
    return table


def db_create_table_score():
    table = Table(
        "score",
        meta,
        Column("code", Integer, primary_key=True),
        Column("score", Integer),
    )
    logger.debug("Created table: score")
    return table


def db_create_table_image():
    table = Table(
        "image",
        meta,
        Column("id", Integer, primary_key=True),
        Column("code", Integer),
        Column("url", String),
        Column("file", String),
        Column("md5", String),
        Column("size", Integer),
    )
    logger.debug("Created table: image")
    return table


def db_create_table_offer():
    table = Table(
        "offer",
        meta,
        Column("code", Integer, primary_key=True),
        Column("owner", String),
        Column("price", Integer),
        Column("name", String),
        Column("description", String),
        Column("brand", String),
        Column("model", String),
        Column("numberOfDoors", String),
        Column("modelDate", Integer),
        Column("vehicleTransmission", String),
        Column("fuelType", String),
        Column("mileageFromOdometer", Integer),
        Column("bodyType", String),
        Column("ddd", Integer),
        Column("state", String),
        Column("region", String),
        Column("zipcode", Integer),
        Column("pictures", Integer),
        Column("carColor", String),
        Column("endTag", Integer),
    )
    meta.create_all(engine)
    logger.debug("Created table: offer")
    return table


def main():
    if not args.q:
        print(
            f"Search for {Fore.BLUE}{car_model}{Style.RESET_ALL} in {Fore.BLUE}{car_brand}{Style.RESET_ALL}"
        )
        print(
            f"Dates between {Fore.BLUE}{car_date_s}{Style.RESET_ALL} and {Fore.BLUE}{car_date_e}{Style.RESET_ALL} in {Fore.BLUE}{car_location}{Style.RESET_ALL}"
        )
        print(f"Connecting to {Fore.MAGENTA}OLX{Style.RESET_ALL}.com.br...")

    global car_offer
    car_offer = PrettyTable(
        [
            f"{Fore.MAGENTA}CODE{Style.RESET_ALL}",
            f"{Fore.MAGENTA}PRICE{Style.RESET_ALL}",
            f"{Fore.MAGENTA}STATE{Style.RESET_ALL}",
            f"{Fore.MAGENTA}YEAR{Style.RESET_ALL}",
            f"{Fore.MAGENTA}FUEL{Style.RESET_ALL}",
            f"{Fore.MAGENTA}COLOR{Style.RESET_ALL}",
            f"{Fore.MAGENTA}DOORS{Style.RESET_ALL}",
            f"{Fore.MAGENTA}KM{Style.RESET_ALL}",
            f"{Fore.MAGENTA}SCORE{Style.RESET_ALL}",
            f"{Fore.MAGENTA}STATUS{Style.RESET_ALL}",
        ]
    )

    cars = extract_url()
    cars_total = len(cars)

    if cars_total == 0:
        logger.error("Exit")
        sys.exit(1)

    cars_found = 0
    cars_update = 0
    cars_exists = 0
    cars_error = 0
    cars_count = 0

    for url in cars:
        result = get_car(url)
        cars_count += 1

        if result == -1:
            cars_error += 1
            car_result = f"{Fore.RED}={Style.RESET_ALL}"
        elif result == 0:
            cars_exists += 1
            car_result = f"{Fore.CYAN}={Style.RESET_ALL}"
        elif result == 1:
            cars_found += 1
            car_result = f"{Fore.GREEN}+{Style.RESET_ALL}"
        else:
            cars_update += 1
            car_result = f"{Fore.YELLOW}*{Style.RESET_ALL}"

        if not args.q:
            print(
                f"{Style.BRIGHT}Car{Style.RESET_ALL}: {cars_count}/{cars_total} [{car_result}]",
                end="\r",
            )

    if cars_total != cars_exists:
        if not args.q:
            print(f"\n\n{car_offer}")
        logger.info("Update available: YES")
    else:
        if not args.q:
            print(
                f"\n\nThere is {Style.BRIGHT}no update available{Style.RESET_ALL} at the moment."
            )
        logger.info("Update available: NO")


    time_end = time.time()
    time_elapsed = round(time_end - time_start, 2)
    rate = round(cars_total / time_elapsed, 2)

    """ Status """
    conn = engine.connect()
    sql = table_status.insert().values(
        duration=time_elapsed,
        rate=rate,
        found=cars_found,
        update=cars_update,
        error=cars_error,
        total=cars_total,
        region=car_location,
        date=get_datetime_epoch(),
    )
    conn.execute(sql)
    logger.info("Saved table: status")

    """ MQTT """
    result = conn.execute(select([func.avg(table_offer.c.price)]))
    avg_price = round(result.fetchone()[0], 2)

    update_mqtt("found", cars_found)
    update_mqtt("total", cars_total)
    update_mqtt(
        "last", datetime.datetime.fromtimestamp(get_datetime_epoch()).strftime("%c")
    )
    update_mqtt("location", car_location)
    update_mqtt("update", cars_update)
    update_mqtt("duration", time_elapsed)
    update_mqtt("rate", rate)
    update_mqtt("avg", avg_price)
    logger.info("Updated MQTT topics")

    """ Summary """
    car_status = PrettyTable(
        [f"{Fore.MAGENTA}ITEM{Style.RESET_ALL}", f"{Fore.MAGENTA}COUNT{Style.RESET_ALL}"]
    )
    car_status.add_row(["Duration", time_elapsed])
    car_status.add_row(["Region", car_location])
    car_status.add_row(
        [f"{Fore.GREEN}New{Style.RESET_ALL}", f"{Fore.GREEN}{cars_found}{Style.RESET_ALL}"]
    )
    car_status.add_row(
        [f"{Fore.CYAN}Exist{Style.RESET_ALL}", f"{Fore.CYAN}{cars_exists}{Style.RESET_ALL}"]
    )
    car_status.add_row(
        [f"{Fore.YELLOW}Update{Style.RESET_ALL}", f"{Fore.YELLOW}{cars_update}{Style.RESET_ALL}"]
    )
    car_status.add_row(
        [f"{Fore.RED}Error{Style.RESET_ALL}", f"{Fore.RED}{cars_error}{Style.RESET_ALL}"]
    )
    car_status.add_row(["Rate", rate])
    car_status.add_row(["Total", cars_total])
    if not args.q:
        print(f"\n{car_status}")
    logger.info("Display car status")


""" ############ """
"""     Main     """
""" ############ """

""" Windows config """
if os.name == "nt":
    if os.path.isfile(setup.WIN_CONFIG_FILE):
        load_dotenv(setup.WIN_CONFIG_FILE)

""" Folders """
data_enable = eval(os.getenv("DATA_MOUNT_ENABLE", "False"))
data_mount = os.getenv("DATA_MOUNT_PATH")

if data_enable:
    base_path = f"{data_mount}/"
else:
    base_path = ""

folders = ["data", "log", "tmp", "db"]
for folder in folders:
    Path(f"{base_path}olx/{folder}").mkdir(parents=True, exist_ok=True)

""" Start """
logger = get_logger(__file__)
bar = "----------------"
logger.info(f"O L X\n\n{bar}\n--- Starting ---\n{bar}")
time_start = time.time()

""" Database """
engine = create_engine(f"sqlite:///{base_path}olx/db/car.db", echo=False)
meta = MetaData()
table_url = db_create_table_url()
table_notification = db_create_table_notification()
table_history = db_create_table_history()
table_status = db_create_table_status()
table_score = db_create_table_score()
table_image = db_create_table_image()
table_offer = db_create_table_offer()

""" Parameters """
logger.info("Reading parameters")
app_version = os.getenv("APP_VERSION", "?")

parser = argparse.ArgumentParser(description="[OLX] Find your car now!")
parser.add_argument("-q", action="store_true", help="Quite mode, without output")
parser.add_argument("--version", action="version", version=f"%(prog)s {app_version}")
args = parser.parse_args()

try:
    daemon_mode = eval(os.getenv("DAEMON_MODE", "False"))
    daemon_interval = int(os.getenv("DAEMON_INTERVAL", 10)) * 60

    car_location_list = []
    car_region_p = os.getenv("CAR_REGION")
    for st in car_region_p.split(","):
        car_location_list.append(get_region(st))
    car_location = str.join(",", car_location_list)
    car_region = str.lower(car_region_p)
    logger.debug(f"Location: {car_location}")

    car_brand = os.getenv("CAR_BRAND")
    car_model = os.getenv("CAR_MODEL")

    car_query = os.getenv("CAR_TITLE", "")
    car_km = int(os.getenv("CAR_KM", 0))
    if car_km > 0 and get_km(car_km):
        car_km_check = True
    else:
        car_km_check = False

    car_date_s = int(os.getenv("CAR_DATE_BEGIN"))
    logger.debug(f"Year (begin): {car_date_s}")

    car_date_e = int(os.getenv("CAR_DATE_END"))
    logger.debug(f"Year (end): {car_date_e}")

    car_rs = get_year(car_date_s)
    car_re = get_year(car_date_e)

except Exception as e:
    logger.error(f"Variable is not defined: {repr(e)}")
    raise SystemExit("Variable is not defined! Exiting...")

mqtt_enable = eval(os.getenv("MQTT_ENABLE", "False"))
mqtt_host = os.getenv("MQTT_HOST")
mqtt_port = int(os.getenv("MQTT_PORT", 1983))
logger.debug(f"MQTT = {mqtt_enable}")

telegram_enable = eval(os.getenv("TELEGRAM_ENABLE", "False"))
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
telegram_chat = os.getenv("TELEGRAM_CHAT_ID")
logger.debug(f"TELEGRAM = {telegram_enable}")

logger.debug(f"DATA = {data_enable}")
if data_enable:
    logger.debug(f"CUSTOM DATA PATH: {data_mount}")

proxy_enabled = bool(os.getenv("HTTP_PROXY", ""))
logger.debug(f"PROXY = {proxy_enabled}")
ssl_verify = True
if proxy_enabled:
    ssl_verify = False
    urllib3.disable_warnings()
    logger.debug(f"SSL verification is disabled")

logger.debug("ARGS - SCORE")
car_score_year = os.getenv("SCORE_YEAR", "")
car_score_color = os.getenv("SCORE_COLOR", "")
car_score_door = int(os.getenv("SCORE_DOOR", 0))
car_score_fuel = os.getenv("SCORE_FUEL", "")
car_score_transmission = os.getenv("SCORE_TRANSMISSION", "")
car_score_price = int(os.getenv("SCORE_PRICE", 0))
car_score_keyword = os.getenv("SCORE_KEYWORD", "")
car_score_km = os.getenv("SCORE_KM", 0)

logger.debug(f"DAEMON mode: {daemon_mode}")
if daemon_mode:
    while True:
        main()
        print(f"\n[{datetime.datetime.now()}] {Style.BRIGHT}Waiting{Style.RESET_ALL} for {Fore.BLUE}next execution{Style.RESET_ALL}...")
        logger.info(f"Sleeping for {daemon_interval} seconds")
        time.sleep(daemon_interval)
        clear()
else:
    main()

""" Exit """
logger.info(f"O L X\n\n{bar}\n--- Exiting  ---\n{bar}\n")
sys.exit(0)