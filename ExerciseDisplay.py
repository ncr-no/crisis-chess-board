import json
from tabulate import tabulate
import os


def shorten_role(role):
    role_mapping = {
        "Chief Executive Officer (CEO)": "CEO",
        "Chief Financial Officer (CFO)": "CFO",
        "Chief Information Officer (CIO)": "CIO",
        "Chief Security Officer (CSO)": "CSO",
        "Chief Legal Officer (CLO)": "CLO",
        "System Administrator": "SysAdmin",
        "Security Analyst": "Sec. Analyst"
    }
    return role_mapping.get(role, role)


def display_tasks(tasks):
    table_data = []
    for index, task in enumerate(tasks, start=1):
        table_data.append([
            index,
            task['Description'],
            shorten_role(task['Responsible']),
            task['Content'],
            task['Priority']
        ])

    headers = ['Task', 'Description', 'Responsible', 'Content', 'Priority']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))

def main():
    phase_mapping = {
        '1': '01_first.json',
        '2': '02_second.json',
        '3': '03_third.json',
        '4': '04_final.json',
    }

    print("Which phase do you want to see?")
    print("[1] - First phase")
    print("[2] - Second phase")
    print("[3] - Third phase")
    print("[4] - Fourth phase")

    choice = input("Enter the number corresponding to the phase you want to see: ")

    if choice in phase_mapping:
        with open("EXERCISE/"+phase_mapping[choice], "r") as file:
            tasks = json.load(file)
            display_tasks(tasks)
    else:
        print("Invalid input. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()
