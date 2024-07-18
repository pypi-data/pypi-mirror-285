import random
import string
from datetime import datetime


def generate_random_string(lenght=10):
    """Method to generate an aleatory string"""
    return "".join(
        random.choices(
            string.ascii_lowercase + string.ascii_uppercase + string.digits,
            k=lenght,
        )
    )


def generate_random_number(lenght=10):
    """Method to generate an aleatory number"""
    number_string = "".join(
        random.choices(
            string.digits,
            k=lenght,
        )
    )
    return int(number_string)


def generate_random_boolean(lenght=10):
    """Method to generate an aleatory bool"""
    randInt = random.getrandbits(1)
    return bool(randInt)


def generate_random_float(from_float=0.1, to_float=100):
    """Method to generate a random float"""
    return random.uniform(from_float, to_float)


def generate_random_email():
    """Method to generate a random email"""
    validchars = "abcdefghijklmnopqrstuvwxyz1234567890"
    loginlen = random.randint(4, 15)
    login = ""
    for i in range(loginlen):
        pos = random.randint(0, len(validchars) - 1)
        login = login + validchars[pos]
    if login[0].isnumeric():
        pos = random.randint(0, len(validchars) - 10)
        login = validchars[pos] + login
    servers = ["@gmail", "@yahoo", "@redmail", "@hotmail", "@bing"]
    servpos = random.randint(0, len(servers) - 1)
    email = login + servers[servpos]
    tlds = [".com", ".in", ".gov", ".ac.in", ".net", ".org"]
    tldpos = random.randint(0, len(tlds) - 1)
    email = email + tlds[tldpos]
    return email


def generate_random_decimal():
    """Method to generate a random decimal"""
    return random.uniform(0.1, 100000)


def generate_random_date():
    """Method to generate a random date"""
    return datetime.now()
