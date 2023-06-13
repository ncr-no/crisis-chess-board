from time import sleep
import json
import sys

MANUAL_SELECT_SCENARIO = False

# identified techniques based on SIEM logs (test data)
identified_techniques = [
    "T1204.002 - User Execution - Malicious File",
    "T1078 - Valid Accounts",
    "T1203 - Exploitation for Client Execution",
    "T1068 - Exploitation for Privilege Escalation",
    "T1566.001 - Spearphishing Attachment",
]

# Used for when MANUAL_SELECT_SCENARIO is enabled
# Name must match friendly_name in scenarios dictionary
available_scenarios = [
    "Ransomware",
    "Destruction of Service",
    "Denial of Service",
    "Phishing",
    "Reconnaissance",
    "C2 Server",
    "System Compromise",
    "Data Breach",
    "Zero Day",
    "Supply Chain Attack",
]
 

scenarios = [
    {   
        "name": "ransomware",
        "friendly_name": "Ransomware",
        "scenario_desc": "Scenario for Ransomware",
        "file": "ransomware.json",
        "required_techniques": 1,
        "techniques": [
            "T1486 - Data Encrypted for Impact",
            ],
    },
    {   
        "name": "destruction-of-service",
        "friendly_name": "Destruction of Service",
        "scenario_desc": "Scenario for Destruction of Service",
        "file": "destruction-of-service.json",
        "required_techniques": 4,
        "techniques": [
            "T1083 - File and Directory Discovery",
            "T1070.004 - File Deletion",
            "T1485 - Data Destruction",
            "T1565.001 - Data Manipulation - Stored Data Manipulation",
            "T1489 - Service Stop",
            ],
    },
    {
        "name": "denial-of-service",
        "friendly_name": "Denial of Service",
        "scenario_desc": "Scenario for DoS",
        "file": "denial-of-service.json",
        "required_techniques": 1,
        "techniques": [
            "T1499.004 - Endpoint DoS - Application or System Exploitation",
            "T1498 - Network denial service",
        ],
    },
        {
        "name": "phishing",
        "friendly_name": "Phishing",
        "scenario_desc": "Scenario for Phishing",
        "file": "phishing.json",
        "required_techniques": 2,
        "techniques": [
            "T1566.001 - Spearphishing Attachment",
            "T1204.002 - User Execution - Malicious File",
        ],
    },
    {
        "name": "reconnaissance",
        "friendly_name": "Reconnaissance",
        "scenario_desc": "Scenario for Reconnaissance",
        "file": "reconnaissance.json",
        "required_techniques": 2,
        "techniques": [
            "T1046 - Network Service Scanning",
            "T1595 - Active Scanning",
            "T1594 - Search Victim-Owned Websites",
            "T1018 - Remote System Discovery",
        ],
    },
    {
        "name": "c2-server",
        "friendly_name": "C2 Server",
        "scenario_desc": "Scenario for C2-Server",
        "file": "c2-server.json",
        "required_techniques": 3,
        "techniques": [
            "T1133 - External Remote Services",
            "T1112 - Modify Registry",
            "T1543.003 - Windows Service",
            "T1021.004 - Remote Services - SSH",
            "T1021 - Remote Services",
        ],
    },
    {
        "name": "system-compromise",
        "friendly_name": "System Compromise",
        "scenario_desc": "Scenario for System Compromise",
        "file": "system-compromise.json",
        "required_techniques": 5,
        "techniques": [
            "T1190 - Exploit Public-Facing Application",
            "T1204.002 - User Execution - Malicious File",
            "T1133 - External Remote Services",
            "T1203 - Exploitation for Client Execution",
            "T1068 - Exploitation for Privilege Escalation",
            "T1489 - Service Stop",
            "T1078.001 - Default Accounts",
            "T1078 - Valid Accounts",
        ],
    },
    {
        "name": "data-breach",
        "friendly_name": "Data Breach",
        "scenario_desc": "Scenario for Data Breach",
        "file": "data-breach.json",
        "required_techniques": 2,
        "techniques": [
            "T1005 - Data from Local System",
            "T1083 - File and Directory Discovery",
        ],
    },
    {
        "name": "zero-day",
        "friendly_name": "Zero Day",
        "scenario_desc": "Scenario for Zero-Day",
        "file": "zero-day.json",
        "required_techniques": 0,
        "techniques": [],
    },
    {
        "name": "supply-chain-attack",
        "friendly_name": "Supply Chain Attack",
        "scenario_desc": "Scenario for Supply Chain Attack",
        "file": "supply-chain-attack.json",
        "required_techniques": 0,
        "techniques": [],
    },
]

def get_scenarios():
    """
    Return a dict with friendly_name and scenario_desc from the scenario dictionary.
    """
    scenario_info = []
    for scenario in scenarios:
        scenario_info.append({"name": scenario["friendly_name"], "description": scenario["scenario_desc"]})
    return scenario_info



# Manual mode: User selects scenario
def get_scenario_from_user(avail_scen_list):
    """
    Prints the available scenarios and asks the user to select one.
    :return: the index of the scenario selected by the user.
    """
    print()
    print("--- Available Scenarios ---"); sleep(0.2)
    for i in range(len(avail_scen_list)):
        print(f"[{i}] {avail_scen_list[i]}")
    print("-------------------------")
    scen_int = int(input("Select Scenario: "))

    while scen_int > len(avail_scen_list) or scen_int < 0:
        print("Invalid input. Please try again.")
        scen_int = int(input("Enter the number of the scenario you want to use: "))
    return avail_scen_list[scen_int]



def determine_scenario(identified_techniques, scenarios_input = scenarios):
    """
    :param scenarios_input: dictionary of scenarios, amount of techniques required to trigger scenario, and list of techniques that match the scenario
    :param identified_techniques: list of techniques identified by attack_paths
    :return: name of the scenario
    :return: friendly name of the scenario
    :return: file name of the scenario
    """
    best_scenario = None
    best_match_count = 0


    # MANUAL MODE: User selects scenario
    if MANUAL_SELECT_SCENARIO:
        chosen_scen = get_scenario_from_user(available_scenarios)
        print(chosen_scen)
        # in available_scenarios, find the scenario with then name chosen_scen
        for scenario in scenarios_input:
            if scenario["friendly_name"] == chosen_scen:
                return scenario["name"], scenario["friendly_name"], scenario["file"]
        return None, None, None

    # AUTOMATIC MODE: Determine scenario based on techniques identified by attack_paths   
    for scenario in scenarios_input:
        matching_techniques = set(identified_techniques).intersection(set(scenario["techniques"]))
        matching_count = len(matching_techniques)

        # if matching_count >= scenario["required_techniques"] and matching_count > best_match_count:
        if matching_count >= scenario["required_techniques"] and matching_count > best_match_count:
            best_scenario = scenario
            best_match_count = matching_count

    if best_scenario is not None:
        return best_scenario["name"], best_scenario["friendly_name"], best_scenario["file"]
    else:
        return None, None, None


def read_mitre_tactics(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        return None

    except json.JSONDecodeError:
        print(f"File {filepath} is not a valid JSON file.")
        return None

    techniques_list = []
    for item in data:
        techniques_list.append(data[item]["technique"])

    return techniques_list

def ScenarioLogic(filename):
    scen = ""
    scen_name = ""
    scen_file = ""

    if MANUAL_SELECT_SCENARIO:
        scen, scen_name, scen_file = determine_scenario([], scenarios)
    else:
        print(f"Monitoring for MITRE ATT&CK Tactics in {filename}.")
        while True:
            tactics = read_mitre_tactics(filename)

            # print(tactics)
            for tactics_list in tactics:
                # print(tactics_list)

                if not tactics_list:
                    continue

                tmp_scen, tmp_scen_name, tmp_scen_file = determine_scenario(tactics_list)
                if tmp_scen is not None:
                    scen = tmp_scen
                    scen_name = tmp_scen_name
                    scen_file = tmp_scen_file

            if scen:
                break
            print(".", end="", flush=True)
            sleep(5)

    print()
    print(scen, scen_name, scen_file)
    return scen, scen_name, scen_file
