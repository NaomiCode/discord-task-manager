import os
from requests import Response
from dotenv import load_dotenv

load_dotenv("../.env")

host = os.environ.get("HOST")


def status_checker(response: Response):
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.status_code
