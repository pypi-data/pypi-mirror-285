from enum import Enum


class Variables(Enum):
    def __getattr__(self, item):
        if item != "_value_":
            return getattr(self.value, item).value
        raise AttributeError

    class SubItems(Enum):
        accounts = ["metadata", "properties"]
        actions = ["configuration"]
        assets = ["metadata"]
        collections = ["metadata"]
        event_handlers = ["configuration"]
        events = []
        groups = ["members"]
        jobs = ["configuration", "history"]
        message_templates = ["body"]
        metadata_definitions = ["definition"]
        object_types = []
        profiles = ["configuration"]
        quotas = []
        resources = ["configuration"]
        roles = []
        tag_collections = []
        task_definitions = []
        tasks = []
        taxonomies = []
        timed_actions = ["configuration"]
        user_defined_object_types = ["hierarchy", "relationships"]
        users = []
        variants = []
        wizards = ["configuration"]
        workflow_definitions = ["structure"]
        workflows = ["jobs"]
        workspaces = ["members"]

    class CommandOptions(Enum):
        cancel = ["jobs", "workflows"]
        compare = [
            "accounts",
            "actions",
            "eventHandlers",
            "groups",
            "messageTemplates",
            "metadataDefinitions",
            "objectTypes",
            "profiles",
            "quotas",
            "resources",
            "roles",
            "tagCollections",
            "taskDefinitions",
            "taxonomies",
            "timedActions",
            "userDefinedObjectTypes",
            "users",
            "variants",
            "wizards",
            "workflowDefinitions",
            "workspaces",
        ]
        create = ["actions", "wizards"]
        launch = ["jobs", "workflows"]
        list = [
            "accounts",
            "actions",
            "assets",
            "collections",
            "eventHandlers",
            "events",
            "groups",
            "jobs",
            "messageTemplates",
            "metadataDefinitions",
            "objectTypes",
            "profiles",
            "quotas",
            "resources",
            "roles",
            "tagCollections",
            "taskDefinitions",
            "tasks",
            "taxonomies",
            "timedActions",
            "userDefinedObjectTypes",
            "users",
            "variants",
            "wizards",
            "workflowDefinitions",
            "workflows",
            "workspaces",
        ]
        pull = [
            "all",
            "accounts",
            "actions",
            "assets",
            "eventHandlers",
            "events",
            "groups",
            "jobs",
            "messageTemplates",
            "metadataDefinitions",
            "objectTypes",
            "profiles",
            "quotas",
            "resources",
            "roles",
            "tagCollections",
            "taskDefinitions",
            "tasks",
            "taxonomies",
            "timedActions",
            "userDefinedObjectTypes",
            "users",
            "variants",
            "wizards",
            "workflowDefinitions",
            "workflows",
            "workspaces",
        ]
        push = [
            "accounts",
            "actions",
            "assets",
            "eventHandlers",
            "groups",
            "jobs",
            "messageTemplates",
            "metadataDefinitions",
            "profiles",
            "quotas",
            "resources",
            "roles",
            "taskDefinitions",
            "tasks",
            "timedActions",
            "userDefinedObjectTypes",
            "users",
            "variants",
            "wizards",
            "workflowDefinitions",
            "workflows",
            "workspaces",
        ]  # todo: taxonomies
        restore = [
            "accounts",
            "actions",
            "eventHandlers",
            "groups",
            "jobs",
            "messageTemplates",
            "metadataDefinitions",
            "profiles",
            "quotas",
            "resources",
            "roles",
            "taskDefinitions",
            "timedActions",
            "userDefinedObjectTypes",
            "users",
            "variants",
            "wizards",
            "workflowDefinitions",
            "workflows",
            "workspaces",
        ]  # todo: taxonomies
        retry = ["jobs", "workflows"]


sdk_version_from_flex_version = {
    "2019.11.x": "1.1.49",
    "2019.12.x": "1.2.0",
    "2019.9.x": "1.1.39",
    "2020.1.x": "1.2.21",
    "2020.10.x": "3.1.0",
    "2020.11.x": "3.2.6",
    "2020.12.x": "3.3.12.1",
    "2020.2.x": "1.2.27",
    "2020.4.x": "1.2.31",
    "2020.5.x": "1.3.5",
    "2020.6.x": "1.3.11",
    "2020.7.x": "1.3.27",
    "2020.8.x": "1.3.27",
    "2020.9.x": "1.4.2",
    "2021.1.x": "3.3.12",
    "2021.10.x": "4.0.26",
    "2021.11.x": "4.0.29",
    "2021.12.x": "4.0.39.6",
    "2021.2.x": "3.3.13",
    "2021.3.x": "3.3.20",
    "2021.5.x": "3.4.9.6",
    "2021.7.x": "4.0.8",
    "2021.8.x": "4.0.11",
    "2021.9.x": "4.0.16",
    "2022.11.x": "5.6.5",
    "2022.12.x": "5.6.13.9",
    "2022.3.x": "5.1.0.2",
    "2022.5.x": "5.2.10.9",
    "2022.7.x": "5.3.1",
    "2022.8.x": "5.3.6",
    "2022.9.x": "5.4.1",
    "2023.10.x": "6.2.10",
    "2023.11.x": "6.3.4",
    "2023.12.x": "6.3.15.7",
    "2023.2.x": "5.6.15",
    "2023.4.x": "5.6.28",
    "2023.6.x": "6.1.4.17",
    "2023.7.x": "6.1.9",
    "2023.8.x": "6.1.14.9",
    "latest": "6.3.15.7",
}
