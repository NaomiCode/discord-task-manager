import requests
from server.config import host, status_checker
import urllib.parse
from typing import TypedDict, Unpack
from typing_extensions import NotRequired, Required

endpointUrl = f'{host}'


class CreateDepartmentParams(TypedDict):
    title: Required[str]
    parent_id: NotRequired[int]
    user_id: NotRequired[int]


class UpdateDepartmentParams(TypedDict):
    category_id: Required[str]
    title: NotRequired[str]
    user_id: NotRequired[int]
    parent_id: NotRequired[int]


def getAll():
    url = urllib.parse.urljoin(endpointUrl, f'/api/category')
    # TODO enable this error checking for other methods
    try:
        response = requests.get(url)
        return status_checker(response)
    except requests.exceptions.ConnectionError as e:
        return False, e


def create(**kwargs: Unpack[CreateDepartmentParams]):
    url = urllib.parse.urljoin(endpointUrl, '/api/category/')
    params = kwargs
    response = requests.post(url, params=params)
    return status_checker(response)


def delete(categoryId):
    url = urllib.parse.urljoin(endpointUrl, '/api/category/destroy/')
    params = {"category_id": categoryId, "_method": "delete"}
    response = requests.post(url, params=params)
    return status_checker(response)


def update(**kwargs: Unpack[UpdateDepartmentParams]):
    params = kwargs
    params['_method'] = 'put'
    url = urllib.parse.urljoin(endpointUrl, "/api/category/update/")
    response = requests.post(url, params=params)
    return status_checker(response)
