from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import json
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageTemplate, Frame

def loadFromJsonFile(file):
    with open(file, 'r') as file:
        return json.load(file)
    

def create_action_card(filename, scenario, scenario_description, tasks, phase):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []

    styles = getSampleStyleSheet()

    # Add scenario title
    title = styles['Title']
    scenario_title = Paragraph(scenario, title)
    story.append(scenario_title)

    # Add scenario description
    description = styles['BodyText']
    scenario_description = Paragraph(scenario_description, description)
    story.append(scenario_description)

    # Add "OPENING"
    opening = Paragraph(phase, styles['Heading2'])
    story.append(opening)

    story.append(Spacer(1, 12))

    # Tasks
    data = []

    col1 = Paragraph("<b>Task</b>", styles['Heading4'])
    col2 = Paragraph("<b>Role</b>", styles['Heading4'])
    col3 = Paragraph("<b>Description</b>", styles['Heading4'])
    col4 = Paragraph("<b>Priority</b>", styles['Heading4'])
    col5 = Paragraph("<b>Done</b>", styles['Heading4'])
    
    data.append([col1, col2, col3, col4, col5])

    for task in tasks:
        checkbox = " " # empty box for checkbox
        task_title = Paragraph("{}".format(task['title']), styles['BodyText'])
        task_role = Paragraph("{}".format(task['responsible']), styles['BodyText'])
        task_description = Paragraph(task['description'], styles['BodyText'])
        task_priority = Paragraph(task['priority'], styles['BodyText'])
        data.append([task_title, task_role, task_description, task_priority, checkbox])

    # Create table for tasks
    table = Table(data, colWidths=[200, 100, 200, 50, 40])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, 'black'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(table)

    # Create PDF
    doc.build(story)



# TODO: Let user select scenario and then create PDF (use ScenarioLogic.py)
scen_desc = "Crisis Chess Board Incident Scenario for Ransomware Incident."
filename = "ransomware.json"

phase1_tasks    = loadFromJsonFile("./01_opening/" + filename)
phase2_tasks    = loadFromJsonFile("./02_mid_game/" + filename)
phase3_tasks    = loadFromJsonFile("./03_end_game/" + "post-incident-tasks.json")


# Opening PDF
phase = "OPENING"
tasks = []
for task in phase1_tasks:
    tasks.append({
        "title": task["Description"],
        "description": task["Content"],
        "responsible": task["Responsible"],
        "priority": str(task["Priority"])
    })
create_action_card("Opening-ActionCard.pdf", "Ransomware Scenario", scen_desc, tasks, phase)
print("[!] Opening-ActionCard.pdf created")


# Middlegame
phase = "MIDDLEGAME"
tasks = []
for task in phase2_tasks:
    tasks.append({
        "title": task["Description"],
        "description": task["Content"],
        "responsible": task["Responsible"],
        "priority": str(task["Priority"])
    })
create_action_card("Middlegame-ActionCard.pdf", "Ransomware Scenario", scen_desc, tasks, phase)
print("[!] Middlegame-ActionCard.pdf created")


# Endgame
phase = "ENDGAME"
tasks = []
for task in phase3_tasks:
    tasks.append({
        "title": task["Description"],
        "description": task["Content"],
        "responsible": task["Responsible"],
        "priority": str(task["Priority"])
    })
create_action_card("Endgame-ActionCard.pdf", "Ransomware Scenario", scen_desc, tasks, phase)
print("[!] Endgame-ActionCard.pdf created")
