"""

    PROJECT: flex_toolbox
    FILENAME: metadata_designeer.py
    AUTHOR: David NAISSE
    DATE: April 15th, 2024

    DESCRIPTION: metadata designer command functions

    TEST STATUS: DOES NOT REQUIRE TESTING (we only open a url)
"""

import webbrowser
from src.utils import get_default_env_alias, get_items


def metadata_designer_command_func(args):
    """
    Action on metadataDesigner command.

    TEST STATUS: DOES NOT REQUIRE TESTING
    """

    # get default env alias if not specified in args
    environment = get_default_env_alias() if args.in_ == 'default' else args.in_

    # check existence of item in the environment
    sample = get_items(
        config_item="metadataDefinitions",
        filters=["limit=1"],
        environment=environment,
        log=False
    )

    if sample:
        # define url
        metadata = sample[next(iter(sample))]
        url_parts = [
            '/'.join(metadata.get('href').split('/')[:3]),
            '/metadata/a/',
            metadata.get('account').get('name'),
            '#/home',
        ]

        # join
        url = ''.join(url_parts)
        print(f"\nOpening {url} in your default web browser...\n")

        # open
        webbrowser.open_new_tab(url)
