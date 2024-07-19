"""

    PROJECT: flex_toolbox
    FILENAME: restore.py
    AUTHOR: David NAISSE
    DATE: October 05, 2023

    DESCRIPTION: restore command functions

    TEST STATUS: DOES NOT REQUIRE TESTING
"""
import json
import os

from src.utils import push_item, get_default_env_alias


def restore_command_func(args):
    """
    Action on restore command.

    TEST STATUS: DOES NOT REQUIRE TESTING
    """

    print("\nThis command is not available for now as it requires some revamp. \n")
    quit()

    # get default env alias if not specified in args
    environment = get_default_env_alias()

    # if path exists
    if os.path.isdir(os.path.join(environment, args.config_item, args.item_name, 'backup', args.backup)):

        # check if is action
        with open(os.path.join(environment, args.config_item, args.item_name, 'backup', args.backup, '_object.json'), 'r') as config_file:
            data = json.load(config_file)

        if args.config_item == 'actions' and data['objectType']['name'] == 'action':
            push_item(config_item=args.config_item, item_name=args.item_name, item_config=data, restore=True)
        else:
            print(f'Cannot restore backup {environment}/{args.item_name}/backup/{args.backup} since it is not an action.\n')

    # path doesn't exist
    else:
        print(f"Cannot find folder for {environment}/{args.item_name}/backup/{args.backup}.\n")
