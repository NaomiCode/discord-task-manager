import requests
from server.config import host, status_checker
import urllib.parse
from typing import TypedDict, Unpack
from typing_extensions import NotRequired, Required

endpointUrl = f'{host}'


class CreateUserParams(TypedDict):
    name: Required[str]
    phone: NotRequired[str]
    email: NotRequired[str]
    guiId: Required[int]
    is_manager: Required[bool]


class UpdateUserParams(TypedDict):
    userId: Required[int]
    name: NotRequired[str]
    phone: NotRequired[str]
    email: NotRequired[str]
    guiId: NotRequired[int]
    is_manager:Required[bool]


def getAll():
    url = urllib.parse.urljoin(endpointUrl, f'/api/users')
    # TODO enable this error checking for other methods
    try:
        response = requests.get(url)
        return status_checker(response)
    except requests.exceptions.ConnectionError as e:
        return False, e


def get(guiId: int):
    url = urllib.parse.urljoin(endpointUrl, f"/api/users?guiId={guiId}")
    response = requests.get(url)
    return status_checker(response),response.json()


def create(**kwargs: Unpack[CreateUserParams]):
    url = urllib.parse.urljoin(endpointUrl, '/api/users/')
    params = kwargs
    response = requests.post(url, params=params)
    return status_checker(response)


def update(**kwargs: Unpack[UpdateUserParams]):
    params = kwargs
    params['_method'] = 'put'
    url = urllib.parse.urljoin(endpointUrl, "/api/users/update/")
    response = requests.post(url, params=params)
    return status_checker(response)


def delete(userId):
    url = urllib.parse.urljoin(endpointUrl, '/api/users/destroy/')
    params = {"userId": userId, "_method": "delete"}
    response = requests.post(url, params=params)
    return status_checker(response)


def getUserTask(guiId: int):
    url = urllib.parse.urljoin(endpointUrl, f'/api/users/show/task?userid={guiId}')
    response = requests.get(url)
    status, data = status_checker(response)
    return status, data['user']

