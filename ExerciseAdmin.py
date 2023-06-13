from time import sleep
import json
import sys
import requests

# Load classes and functions from helper files
from Classes import Task, Scenario, Incident, Role
from ApiHelper import createRole, createScenario, getRolesForPlan, getScenariosForPlan, getRolesForIncident, createTask, createIncident, addTaskToScenario, getTaskStatus

# Flags to control whether to create with api or not
CREATE_SCENARIOS = True
CREATE_ROLES = True

mitre_tactics_file = "mitre_tactics.json"

def show_banner():
    lines = [
    " _____      _     _       _____ _                    ______                     _ ",
    "/  __ \    (_)   (_)     /  __ \ |                   | ___ \                   | |",
    "| /  \/_ __ _ ___ _ ___  | /  \/ |__   ___  ___ ___  | |_/ / ___   __ _ _ __ __| |",
    "| |   | '__| / __| / __| | |   | '_ \ / _ \/ __/ __| | ___ \/ _ \ / _` | '__/ _` |",
    "| \__/\ |  | \__ \ \__ \ | \__/\ | | |  __/\__ \__ \ | |_/ / (_) | (_| | | | (_| |",
    " \____/_|  |_|___/_|___/  \____/_| |_|\___||___/___/ \____/ \___/ \__,_|_|  \__,_|",
    "----------------------------------------------------------------------------------",
    ""
    ]
    for line in lines:
        print(line)
        sleep(0.05)


def loadFromJsonFile(file):
    with open(file, 'r') as file:
        return json.load(file)


def get_role_object(role_list, role_name):
    """
    :param: role_list: list of Role objects
    :param: role_name: name of role to find
    :return: Role object with name containg role_name
    """
    for i in role_list:
        if role_name in i.name:
            return i
    return None

def get_scenario_object(scenario_list, scenario_name):
    """
    :param: scenario_list: list of Scenario objects
    :param: scenario_name: name of scenario to find
    :return: Scenario object with name containg scenario_name
    """
    for i in scenario_list:
        if scenario_name in i.name:
            return i
    return None

def print_task(task):
    """
    :param: task: Task in JSON format
    Prints task in a nice format
    """
    print()
    print("-" * 80)
    print("| Desc: " +     task["Description"][:70].ljust(70) + " | ")
    print("| Role: " +     task["Responsible"].ljust(70)      + " | ")
    print("| Prio: " + str(task["Priority"]).ljust(70)        + " | ")
    print("-" * 80)


def task_creation_successful(status_code, task_id):
    """
    :param: status_code: status code from API (200 = OK)
    :param: task_id: task id from API
    :return: True if task was successfully created, False otherwise
    """
    return status_code == 200 and task_id != "0"


def create_tasks_incaseit(task_list, role_list, current_scenario):
    """
    :param: task_list: list of tasks in JSON format
    :return: list of task_ids that were successfully created
    """
    tasks_created = []
    for task in task_list:
        print_task(task)
        responsible_role = get_role_object(role_list, task["Responsible"])
        if responsible_role:
            print(f"=> Role object found {responsible_role.name}")
        else:
            print("=> FAILED to find role object. Skipping task...")
            continue

        sleep(0.2)
        
        stat_code, task_id = createTask(task["Priority"], responsible_role, task["Description"], task["Content"], task["Time"])
        print("stat_code, task_id", stat_code, task_id)

        if task_creation_successful(stat_code, task_id):
            print(f"=> Task successfully created [id: {task_id}]")

            scenario_response, content = addTaskToScenario(task_id, current_scenario)

            if scenario_response == 200:
                print(f"=> Task added to scenario [{scenario_response}]")
                tasks_created.append(task_id)
            else:
                print(f"=> FAILED to add task to scenario [{scenario_response}]")
        else:
            print("=> FAILED to create task")

    return tasks_created


# --- Main ---
if __name__ == "__main__":
    show_banner()

    # print("Press any key to continue...")
    # n = input()


    # Lists for storing tasks for each stage:
    first =  []
    second = []
    third =  []
    final =  []

    file_dir = "./EXERCISE/"
    phase1_tasks    = loadFromJsonFile(file_dir + "01_first.json")
    phase2_tasks    = loadFromJsonFile(file_dir + "02_second.json")
    phase3_tasks    = loadFromJsonFile(file_dir + "03_third.json")
    phase4_tasks    = loadFromJsonFile(file_dir + "04_final.json")


    print("==============================")
    print("          SCENARIOS           ")
    print("==============================")

    scen_response = getScenariosForPlan()
    all_scenarios = []

    print("Scenario: Ransomware")

    for i in json.loads(scen_response):
        all_scenarios.append(Scenario(i))
    
    curr_scen = get_scenario_object(all_scenarios, "Ransomware")
    scen_name = curr_scen.name
    
    print(f"Scenario Object: {curr_scen.name} - {curr_scen}")


    # Ask user for Incident ID
    inc_id = input("Enter Incident ID: ") # 32887
    if not inc_id:
        print("No Incident ID entered. Exiting...")
        exit(1)

    print()
    print("==============================")
    print("          INCIDENT           ")
    print("==============================")
    
    
    incident_name = f"Incident: Ransomware Incident detected"
    incident_description = f"Security Operations Center has detected a ransomware incident."
    
    print("[!] Incident Selected: " + incident_name)
    

    # ----- GET ROLES -----
    roles_incident = getRolesForIncident(inc_id)

    roles_object_list = []
    for i in roles_incident:
        roles_object_list.append(Role(i))


    # List to keep track of tasks that are not completed
    remaining_tasks = []


    print("Select phase to create tasks for:")
    print("[1] First phase")
    print("[2] Second phase")
    print("[3] Third phase")
    print("[4] Final phase")
    phase = input("Enter phase: ")

    if phase not in ["1", "2", "3", "4"]:
        phase = input("Enter phase: ")

    if phase == "1":
        task_list = phase1_tasks
    elif phase == "2":
        task_list = phase2_tasks
    elif phase == "3":
        task_list = phase3_tasks
    elif phase == "4":
        task_list = phase4_tasks


# Create tasks in IncaseIT
    remaining_tasks = create_tasks_incaseit(task_list, roles_object_list, curr_scen)

    print(); print()
    print("--- TASKS CREATION COMPLETED ---")