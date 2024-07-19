"""

    PROJECT: flex_toolbox
    FILENAME: push.py
    AUTHOR: David NAISSE
    DATE: September 14, 2023

    DESCRIPTION: push command functions

    TEST STATUS: FULLY TESTED
"""

import json
import os


from src.env import get_default_env_alias
from src.utils import push_item, listen


def push_command_func(args):
    """
    Action on push command.

    TEST STATUS: FULLY TESTED
    """

    # get default env alias if not specified in args
    src_environment = get_default_env_alias() if args.from_ == 'default' else args.from_
    dest_environments = [get_default_env_alias()] if args.to == ['default'] else args.to

    # build item name
    item = " ".join(args.item_names)

    # if path exists
    if os.path.isdir(os.path.join(src_environment, args.config_item, item)):

        # get obj
        with open(os.path.join(src_environment, args.config_item, item, '_object.json'), 'r') as config_file:
            data = json.load(config_file)

        # iterate over dest envs
        for dest_environment in dest_environments:
            push_item(
                config_item=args.config_item,
                item_name=item,
                item_config=data,
                push_to_failed_jobs=args.push_to_failed_jobs,
                src_environment=src_environment,
                dest_environment=dest_environment,
                retry=args.retry,
                with_dependencies=args.with_dependencies,
                include_resources=args.include_resources
            )

            # listen
            if args.config_item in ['jobs'] and args.retry and args.listen:
                listen(
                    config_item=args.config_item,
                    item_name=item,
                    environment=dest_environment
                )

    else:
        print(f"Cannot find {src_environment}/{args.config_item}/{item}. Please check the information provided. ")
