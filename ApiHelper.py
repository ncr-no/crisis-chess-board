import os
import json
import requests
from datetime import datetime, timedelta

from dotenv import load_dotenv
from Classes import Task, Scenario, Incident, Role

load_dotenv()
api_key = os.getenv("API_KEY")

# Verify that API key has been set
if not api_key:
    raise ValueError("API key not loaded")

BASE_URL = "https://uat.incaseit.net"

headers = {"Authorization": api_key, "Content-Type": "application/json"}

# --------------------------------------------- #


# - GetScenariosForPlan #GET
def getScenariosForPlan():
    """
    :return: JSON object with list of scenarios
    """
    path = "/api/ascert/scenarios"

    req = requests.get(BASE_URL + path, headers=headers)
    return req.content.decode()


# - GetRolesForPlan #GET
def getRolesForPlan():
    """
    :return: JSON object with list of roles
    """
    path = "/api/ascert/roles"

    req = requests.get(BASE_URL + path, headers=headers)
    req = json.loads(req.content.decode())
    return req


# - GetRolesForIncident #GET
def getRolesForIncident(id):
    """
    :param id: int (e.g. 5345)
    """
    path = f"/api/ascert/roles/{str(id)}"

    req = requests.get(BASE_URL + path, headers=headers)
    req = json.loads(req.content.decode())
    return req


# Create Role for Plan #POST
def createRole(name: str):
    """
    :param name: string
    """
    path = "/api/ascert/role/plan"

    data = {"name": name}

    req = requests.post(BASE_URL + path, headers=headers, json=data)
    return req.status_code, req.content.decode()


# Create Scenario #POST
def createScenario(name: str, description: str):
    """
    :param name: string
    :param description: string
    """
    path = "/api/ascert/scenario"
    payload = json.dumps({"description": description, "name": name})

    req = requests.post(BASE_URL + path, headers=headers, data=payload)
    return req.status_code, req.content.decode()


# - CreateIncident #POST
def createIncident(name: str, description: str, scenario):
    """
    :param name: string
    :param description: string
    :param scenario: Scenario object
    """
    path = "/api/ascert/incident"

    # create Incident object
    payload = Incident(name=name, description=description, scenario=scenario)


    # Push to api with object as payload
    inc_response = requests.post(
        BASE_URL + path, headers=headers, data=payload.toJSON()
    )
    print(inc_response.status_code, inc_response.content.decode())

    print(json.loads(inc_response.content.decode()))
    return inc_response.status_code, inc_response.content.decode()


# - CreateTask #POST
def createTask(
    priority: int, role: Role, description: str, content: str, due_date = None
):
    """
    :param priority: int (1-3)
    :param role: Role object
    :param description: string
    :param content: string
    :param due_date: string (e.g. 20m, 1h, 2d, 3w)
    """
    path = "/api/ascert/task"
    if due_date:
        due_date = calculate_due_date(due_date)

    # Create Task Object
    payload = Task(
        priority=priority,
        group=role,
        description=description,
        content=content,
        due_date=due_date,
    )

    task_response = requests.post(
        BASE_URL + path, headers=headers, data=payload.toJSON()
    )

    return task_response.status_code, task_response.content.decode()

def calculate_due_date(due_date_str: str) -> str:
    current_time = datetime.now()

    time_unit = due_date_str[-1]
    amount = int(due_date_str[:-1])

    if time_unit == 'm':
        due_date = current_time + timedelta(minutes=amount)
    elif time_unit == 'h':
        due_date = current_time + timedelta(hours=amount)
    elif time_unit == 'd':
        due_date = current_time + timedelta(days=amount)
    elif time_unit == 'w':
        due_date = current_time + timedelta(weeks=amount)
    else:
        raise ValueError("Invalid due_date format")

    due_date_str = due_date.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    due_date_str = due_date_str[:-2] + ":" + due_date_str[-2:]
    return due_date_str

# - addTaskToScenario #POST
def addTaskToScenario(task_id, scenario: Scenario):
    """
    :param task_id: int
    :param scenario: Scenario object
    """
    # path = f"/api/ascert/scenarios/task/{str(task_id)}"  # (e.g. 43311)
    path = f"/api/ascert/scenarios/task/43311"  # (e.g. 43311)
    
    payload = scenario
    scenario_response = requests.post(BASE_URL+path, headers=headers, data=payload.toJSON())

    return scenario_response.status_code, scenario_response.content.decode()


def getTaskStatus(task_id):
    """
    :param task_id: int
    :return: False if task is not completed, True if task is completed
    """
    path = f"/api/ascert/tasks/{str(task_id)}"

    req = requests.get(BASE_URL + path, headers=headers)
    req = json.loads(req.content.decode())
    return req["completedChecked"]
