from src.v2.environment import Environment
from src.v2.objects import ObjectType, Objects, SubItems


if __name__ == "__main__":
    env = Environment.from_env_file("cs-sandbox-ovh-flex-config")
    map = {
        ObjectType.ACCOUNTS: SubItems.ACCOUNTS,
        ObjectType.ACTIONS: SubItems.ACTIONS,
        ObjectType.ASSETS: SubItems.ASSETS,
        ObjectType.COLLECTIONS: SubItems.COLLECTIONS,
        ObjectType.EVENT_HANDLERS: SubItems.EVENT_HANDLERS,
        ObjectType.EVENTS: SubItems.EVENTS,
        ObjectType.GROUPS: SubItems.GROUPS,
        ObjectType.JOBS: SubItems.JOBS,
        ObjectType.MESSAGE_TEMPLATES: SubItems.MESSAGE_TEMPLATES,
        ObjectType.METADATA_DEFINITIONS: SubItems.METADATA_DEFINITIONS,
        ObjectType.OBJECT_TYPES: SubItems.OBJECT_TYPES,
        ObjectType.PROFILES: SubItems.PROFILES,
        ObjectType.QUOTAS: SubItems.QUOTAS,
        ObjectType.RESOURCES: SubItems.RESOURCES,
        ObjectType.ROLES: SubItems.ROLES,
        ObjectType.TAG_COLLECTIONS: SubItems.TAG_COLLECTIONS,
        ObjectType.TASK_DEFINITIONS: SubItems.TASK_DEFINITIONS,
        ObjectType.TASKS: SubItems.TASKS,
        ObjectType.TAXONOMIES: SubItems.TAXONOMIES,
        ObjectType.TIMED_ACTIONS: SubItems.TIMED_ACTIONS,
        ObjectType.USER_DEFINED_OBJECT_TYPES: SubItems.USER_DEFINED_OBJECT_TYPES,
        ObjectType.USERS: SubItems.USERS,
        ObjectType.VARIANTS: SubItems.VARIANTS,
        ObjectType.WIZARDS: SubItems.WIZARDS,
        ObjectType.WORKFLOW_DEFINITIONS: SubItems.WORKFLOW_DEFINITIONS,
        ObjectType.WORKFLOWS: SubItems.WORKFLOWS,
        ObjectType.WORKSPACES: SubItems.WORKSPACES,
    }

    for k, v in map.items():
        objects_request = Objects(
            object_type=k,
            sub_items=v,
            filters={"limit": 3},
            with_dependencies=True,
            mode="full",
            save_results=True,
        )

        objects = []
        try:
            objects = objects_request.get_from(environment=env)
            print(len(objects))
        except Exception as ex:
            print(ex)

    # TODO:
    # push
    # tests
