"""

    PROJECT: flex_toolbox
    FILENAME: compare.py
    AUTHOR: David NAISSE
    DATE: October 17, 2023

    DESCRIPTION: compare command functions

    TEST STATUS: FULLY TESTED
"""
import os

import pandas as pd
from tqdm import tqdm

from src.utils import get_items, create_folder, enumerate_sub_items, flatten_dict, compare_dicts_list


def compare_command_func(args):
    """
    Action on compare command.

    TEST STATUS: FULLY TESTED
    """

    if len(args.environments) >= 2:

        # compare items
        compare_items(config_item=args.config_item, environments=args.environments, filters=args.filters,
                      sub_items=enumerate_sub_items(config_item=args.config_item))

    else:
        print(f"Cannot compare {args.config_item} if number of environments provided is less than 2 "
              f"(provided: {args.environments}). ")


def compare_items(config_item: str, filters: list, environments: list, sub_items: list = []):
    """
    Compare items between environments.

    TEST STATUS: DOES NOT REQUIRE TESTING

    :param sub_items: sub items
    :param config_item: config item (ex: actions, workflowDefinitions)
    :param filters: filters to apply
    :param environments: envs (ex: customer-dev, customer-stg, customer-prod)
    :return:
    """

    cmp = {}

    # create comparison folders
    create_folder(folder_name=f"compare_{'_'.join(environments)}", ignore_error=True)
    create_folder(folder_name=os.path.join(f"compare_{'_'.join(environments)}", config_item), ignore_error=True)

    # get item from envs
    for env in environments:
        items = get_items(
            config_item=config_item,
            filters=filters,
            sub_items=sub_items,
            environment=env,
            id_in_keys=False,
        )

        cmp[env] = items

    print("")

    # create diff df for each item
    for item in tqdm(cmp.get(environments[0]), desc=f"Comparing items between {environments}"):
        tmp_compare = {}

        # flatten dicts
        for env in environments:
            tmp_compare[env] = flatten_dict(cmp.get(env).get(item, {}))

        # compare
        result = compare_dicts_list(dict_list=[d for d in tmp_compare.values()], environments=environments)

        # save
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.max_rows', None)
        if result is not None: result.to_csv(os.path.join(f"compare_{'_'.join(environments)}", config_item, f"{item}.tsv"), sep="\t")

    print("\nResult of the comparison (if there are any differences) have been saved in "
          f"compare_{'_'.join(environments)}/{config_item}/<item_name>.tsv for your best convenience. \n")


