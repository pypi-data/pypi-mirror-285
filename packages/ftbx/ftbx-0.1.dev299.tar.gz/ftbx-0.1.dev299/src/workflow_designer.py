"""

    PROJECT: flex_toolbox
    FILENAME: workflow_designer.py
    AUTHOR: David NAISSE
    DATE: April 15th, 2024

    DESCRIPTION: workflow designer command functions

    TEST STATUS: DOES NOT REQUIRE TESTING
"""

import webbrowser
from src.utils import get_default_env_alias, get_items


def workflow_designer_command_func(args):
    """
    Action on workflowDesigner command.

    TEST STATUS: DOES NOT REQUIRE TESTING
    """

    # get default env alias if not specified in args
    environment = get_default_env_alias() if args.in_ == 'default' else args.in_

    # check existence of item in the environment
    item_exist = get_items(
        config_item="workflowDefinitions",
        filters=[f"name={args.workflow_name}", "exactNameMatch=true"],
        environment=environment,
        log=False
    )

    if item_exist:
        # define url
        workflow = item_exist[next(iter(item_exist))]
        url_parts = [
            '/'.join(workflow.get('href').split('/')[:3]),
            '/workflow/a/',
            workflow.get('account').get('name'),
            '/edit?id=',
            str(workflow.get('id'))
        ]

        # join
        url = ''.join(url_parts)
        print(f"\nOpening {url} in your default web browser...\n")

        # open
        webbrowser.open_new_tab(url)
    else:
        print(f"\n/!\\ Cannot find workflowDefinitions with name {args.workflow_name} in {environment}. Please check the information provided. /!\\\n")
