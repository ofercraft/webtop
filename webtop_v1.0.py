import requests
from datetime import datetime, timezone, timedelta, date
import random
import math
import requests
import json
import time
import certifi
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()

def login(username: str, password: str):
    """
    gets a cookie for a webtop user, logins by username and password

    Args:
        username (str): the username of the webtop user.
        password (str): The password of the webtop user.

    Returns:
        int: the wanted cookie value, and the student id.
    """

    data = encrypt_string_to_server(f"{username}0")  #encrypt the username to give to the database.

    url = "https://webtopserver.smartschool.co.il/server/api/user/LoginByUserNameAndPassword"
    data = {  #the request parameters.
        "Data": data,
        "UserName": username,
        "Password": password,
        "deviceDataJson": '{"isMobile":false,"isTablet":false,"isDesktop":true}'

    }
    response = requests.post(url, json=data, verify=False)  #send the request, and get the response and the cookie
    student_id = response.json()["data"]["userId"]  #pull the student id from the response json
    cookies = response.cookies  #get the response cookies
    return cookies, student_id
