from time import sleep
import json
import sys
import requests

# Load classes and functions from helper files
from Classes import Task, Scenario, Incident, Role
from ApiHelper import createRole, createScenario, getRolesForPlan, getScenariosForPlan, getRolesForIncident, createTask, createIncident, addTaskToScenario, getTaskStatus
from ScenarioLogic import determine_scenario, get_scenarios, ScenarioLogic

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


def read_input(filename):
    board_input = loadFromJsonFile(filename)
    return board_input


def pretty_print_input(json_input) -> None:
    print("--- [Board Input] ---")
    print("[IP]".ljust(13), "[Level]".ljust(10), "[Technique]")
    print("------------+---------+-------------------------")
    for ip, data in json_input.items():
        print(f"{ip.ljust(11)} | level {data['level']} | ", data['technique'])
        sleep(0.2)
    print("------------+---------+-------------------------")


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

    board_input = read_input(mitre_tactics_file)
    pretty_print_input(board_input)

    print()
    print("==============================")
    print("        SCENARIO LOGIC        ")
    print("==============================")
    # Determine scenario using ScenarioLogic
    scen, scen_name, scen_file = ScenarioLogic(mitre_tactics_file)
    if scen is None:
        print("No scenario found")
        sys.exit()

    print("Scenario: " + scen_name)
    print("Scenario file: " + scen_file)

    # print("Press any key to continue...")
    # n = input()


    # Lists for storing tasks for each stage:
    opening_tasks = []
    mid_tasks =     []
    end_tasks =     []

    open_dir = "./01_opening/"
    mid_dir =  "./02_mid_game/"
    end_dir =  "./03_end_game/"
    opening_tasks =           loadFromJsonFile(open_dir + scen_file)
    mid_tasks =               loadFromJsonFile(mid_dir + scen_file)
    end_tasks =               loadFromJsonFile(end_dir + "post-incident-tasks.json")



    print("==============================")
    print("            ROLES             ")
    print("==============================")
    roles = loadFromJsonFile("roles.json")

    for rol in roles:
        print("[!] Creating role: " + rol["name"])
        sleep(0.2)
        if CREATE_ROLES:
            status_code, resp = createRole(rol["name"])
    # ----- ROLES END -----

    # print("Press any key to continue...")
    # n = input()

    print("==============================")
    print("          SCENARIOS           ")
    print("==============================")
    
    # Create all scenarios from ScenarioLogic
    scenarios = get_scenarios() # dict with scen_name and scen_desc

    for scen in scenarios:
        print("[!] Creating scenario: " + scen["name"])
        sleep(0.2)
        if CREATE_SCENARIOS:
            status_code, resp = createScenario(scen["name"], scen["description"])

    scen_response = getScenariosForPlan()
    all_scenarios = []

    for i in json.loads(scen_response):
        all_scenarios.append(Scenario(i))
    
    curr_scen = get_scenario_object(all_scenarios, scen_name)
    scen_name = curr_scen.name
    
    print(f"Scenario Object: {curr_scen.name} - {curr_scen}")


    # wait
    # print("Press any key to continue...")
    # n = input()

    print()
    print("==============================")
    print("          INCIDENT           ")
    print("==============================")
    
    incident_name = f"Incident: {scen_name}"
    incident_description = f"{scen_name} incident detected. Scenario created."
    
    print("[!] Creating incident: " + incident_name)
    
    status_code, inc_id = createIncident(incident_name, incident_description, curr_scen) # (use 200, 32887 for testing)
    print(f"{[status_code]} - Incident Id: {inc_id}")

    

    # ----- GET ROLES -----
    roles_incident = getRolesForIncident(inc_id)

    roles_object_list = []
    for i in roles_incident:
        roles_object_list.append(Role(i))

    print(f"Available roles for this incident: [{len(roles_object_list)}]")


    # List to keep track of tasks that are not completed
    remaining_tasks = []


    # print("Press any key to continue...")
    # n = input()


    print()
    print("====================================")
    print("              OPENING               ")
    print("====================================")
    
    if opening_tasks == []:
        print("No opening tasks for scenario found. Exiting...")
        sys.exit()

    # Create tasks in IncaseIT
    remaining_tasks = create_tasks_incaseit(opening_tasks, roles_object_list, curr_scen)


    print();print()
    print("[Monitoring completion of tasks in IncaseIT...]")
    print(f"Tasks remaining: {len(remaining_tasks)}")

    # while remaining_tasks is not empty, check status of tasks
    while len(remaining_tasks) > 0:
        try:
            sleep(15) # to not spam the API
            for task_id in remaining_tasks:

                # check if task is completed or not
                completed = getTaskStatus(task_id)

                if completed:
                    remaining_tasks.remove(task_id)
                    print(f"[!] Task {task_id} completed. ({len(remaining_tasks)} tasks left)")

        except requests.exceptions.ConnectionError:
            print("Connection error. Retrying...")
            sleep(5)
            continue

    print("--- All opening tasks have been completed")




    print()
    print("====================================")
    print("              MID GAME              ")
    print("====================================")

    # If mid-game tasks exist:
    if mid_tasks != []:
        print("Mid-game tasks found. Creating tasks...")

        remaining_tasks = create_tasks_incaseit(mid_tasks, roles_object_list, curr_scen)
        print();print()
        print("[Monitoring completion of tasks in IncaseIT...]")
        print(f"Tasks remaining: {len(remaining_tasks)}")
        # while remaining_tasks is not empty, check status of tasks
        
        while len(remaining_tasks) > 0:
            try:
                sleep(15) # to not spam the API
                for task_id in remaining_tasks:

                    # check if task is completed or not
                    completed = getTaskStatus(task_id)

                    if completed:
                        remaining_tasks.remove(task_id)
                        print(f"[!] Task {task_id} completed. ({len(remaining_tasks)} tasks left)")
            except requests.exceptions.ConnectionError:
                print("Connection error. Retrying...")
                sleep(5)
                continue
            
    else:
        print("No mid game tasks for this scenario.")
    print("--- All mid-game tasks have been completed")





    print()
    print("====================================")
    print("              END GAME              ")
    print("====================================")
    
    # Create tasks in IncaseIT
    remaining_tasks = create_tasks_incaseit(end_tasks, roles_object_list, curr_scen)
        
    print();print()
    print("[Monitoring completion of tasks in IncaseIT...]")
    print(f"Tasks remaining: {len(remaining_tasks)}")
    # while remaining_tasks is not empty, check status of tasks
    while len(remaining_tasks) > 0:
        try:
            sleep(15) # to not spam the API
            for task_id in remaining_tasks:

                # check if task is completed or not
                completed = getTaskStatus(task_id)

                if completed:
                    remaining_tasks.remove(task_id)
                    print(f"[!] Task {task_id} completed. ({len(remaining_tasks)} tasks left)")
        except requests.exceptions.ConnectionError:
            print("Connection error. Retrying...")
            sleep(5)
            continue

    print("--- All end-game tasks have been completed")
