"""

    PROJECT: flex_toolbox
    FILENAME: create.py
    AUTHOR: David NAISSE
    DATE: March 25th, 2024

    DESCRIPTION: create command functions

    TEST STATUS: DOES NOT REQUIRE TESTING (create = push only if not exist)
"""

import json
import os

from src.env import get_default_env_alias
from src.utils import push_item, get_items


def create_command_func(args):
    """
    Action on create command.

    TEST STATUS: DOES NOT REQUIRE TESTING
    """

    # get default env alias if not specified in args
    environment = get_default_env_alias() if args.in_ == 'default' else args.in_

    # check existence of item in the environment
    item_exist = len(get_items(
        config_item=args.config_item,
        filters=[f"name={args.item_name}", "exactNameMatch=true"],
        environment=environment,
        log=False
    ))

    if not item_exist:
        # if local folder exists
        if os.path.isdir(os.path.join(os.path.expanduser('~'), '.ftbx', "templates", args.config_item, args.plugin)):

            # get obj
            with open(os.path.join(os.path.expanduser('~'), '.ftbx', "templates", args.config_item, args.plugin, '_object.json'), 'r') as config_file:
                data = json.load(config_file)

            # rename our item
            data['name'] = args.item_name
            data['displayName'] = args.item_name

            # iterate over dest envs
            push_item(
                config_item=args.config_item,
                item_name=args.plugin,
                item_config=data,
                src_environment=os.path.join(os.path.expanduser('~'), '.ftbx', "templates"),
                dest_environment=environment,
            )

        else:
            print(f"\n/!\\ Cannot find templates/{args.config_item}/{args.plugin}. Please check the information provided. /!\\\n")
    else:
        print(f"\n/!\\ The item {args.config_item}: {args.item_name} already exists in {environment}. Cannot proceed further. /!\\\n")
