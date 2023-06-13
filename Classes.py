import json

# Task Model Definition
class Task:
    def __init__(self, description: str, content, priority: int, group, due_date):
        self.description = description
        self.content = content
        self.priority = priority
        self.responsibleGroup = group
        self.dueDate = due_date

    def toJSON(self):
        return json.dumps(self, sort_keys=True, indent=4, default=lambda x: x.__dict__)


# Scenario Model Definition
class Scenario:
    def __init__(self, data):
        self.alias = data.get("alias")
        self.createdBy = data.get("createdBy")
        self.incId = data.get("incId")
        self.name = data.get("name")
        self.scenarioApproved = data.get("scenarioApproved")
        self.scenarioShortcut = data.get("scenarioShortcut")
        self.scnId = data.get("scnId")
        self.sequenceNbr = data.get("sequenceNbr")
        self.type = data.get("type")

    def toJSON(self):
        return json.dumps(self, sort_keys=True, indent=4, default=lambda x: x.__dict__)


# Incident Model Definition
class Incident:
    def __init__(self, name: str, description: str, scenario: Scenario):
        self.name = name
        self.description = description
        self.scenarioVO = scenario

    def toJSON(self):
        return json.dumps(self, sort_keys=True, indent=4, default=lambda x: x.__dict__)


# Role Model Definition
class Role:
    def __init__(self, data):
        self.__dict__.update(data)
