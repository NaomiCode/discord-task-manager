import requests
from server.config import host, status_checker
import urllib.parse
import datetime
from typing import TypedDict, Unpack
from typing_extensions import NotRequired, Required


class UpdateTaskParams(TypedDict):
    task_id: Required[int]
    title: str
    body: str
    deadline: datetime.date
    category_id: int
    assigned_id: int


class CreateTaskParams(TypedDict):
    title: Required[str]
    body: Required[str]
    deadline: Required[datetime.date]
    category_id: Required[int]
    created_id: Required[int]
    assigned_id: NotRequired[int]


endpointUrl = f'{host}'


def get(taskId):
    url = urllib.parse.urljoin(endpointUrl, f'/api/tasks/show/{taskId}')
    # TODO enable this error checking for other methods
    try:
        response = requests.get(url)
        return status_checker(response)
    except requests.exceptions.ConnectionError as e:
        return False, e


def getAll():
    url = urllib.parse.urljoin(endpointUrl, '/api/tasks')
    response = requests.get(url)
    return status_checker(response)


def create(**kwargs: Unpack[CreateTaskParams]):
    url = urllib.parse.urljoin(endpointUrl, '/api/tasks')
    params = kwargs
    response = requests.post(url, params=params)
    return status_checker(response)


def delete(taskId):
    url = urllib.parse.urljoin(endpointUrl, '/api/tasks/destroy')
    params = {"task_id": taskId, "_method": "delete"}
    response = requests.post(url, params=params)
    return status_checker(response)


def update(**kwargs: Unpack[UpdateTaskParams]):
    params = kwargs
    params['_method'] = 'put'
    url = urllib.parse.urljoin(endpointUrl, "/api/tasks/update")
    response = requests.post(url, params=params)
    return status_checker(response)


class AcceptFinishResignTaskParams(TypedDict):
    task_id: Required[int]
    guiId: NotRequired[int]


def accept(task_id: int, guiId: int):
    params = AcceptFinishResignTaskParams(task_id=task_id, guiId=guiId)
    url = urllib.parse.urljoin(endpointUrl, "/api/tasks/accepts")
    response = requests.post(url, params=params)
    return status_checker(response)


def finish(task_id: int, guiId: int):
    params = AcceptFinishResignTaskParams(task_id=task_id, guiId=guiId)
    url = urllib.parse.urljoin(endpointUrl, "/api/task/finished/")
    response = requests.post(url, params=params)
    return status_checker(response)


def resign(task_id: int, guiId: int):
    params = AcceptFinishResignTaskParams(task_id=task_id, guiId=guiId)
    url = urllib.parse.urljoin(endpointUrl, "/api/task/resign/")
    response = requests.post(url, params=params)
    return status_checker(response)


def reject(task_id: int):
    params = AcceptFinishResignTaskParams(task_id=task_id)
    url = urllib.parse.urljoin(endpointUrl, "/api/tasks/reject/")
    response = requests.post(url, params=params)
    return status_checker(response)


def success(task_id: int):
    params = AcceptFinishResignTaskParams(task_id=task_id)
    url = urllib.parse.urljoin(endpointUrl, "/api/tasks/success/")
    response = requests.post(url, params=params)
    return status_checker(response)


