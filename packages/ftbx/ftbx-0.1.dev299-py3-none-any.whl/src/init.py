"""

    PROJECT: flex_toolbox
    FILENAME: init.py
    AUTHOR: David NAISSE
    DATE: December 15, 2023

    DESCRIPTION: init command functions

    TEST STATUS: FULLY TESTED
"""

import os
import platform

from src.utils import update_toolbox_resources


def init_command_func(args):
    """
    Action on init command.

    TEST STATUS: FULLY TESTED

    :param args:
    :return:
    """

    # get os
    user_os = platform.system()
    print(f"\nOS: {user_os.upper()}\n")

    # create dotfolder
    os.makedirs(os.path.join(os.path.expanduser("~"), ".ftbx"), exist_ok=True)
    print(f"Directory '.ftbx' has been created successfully. \n")

    # fetch resources
    update_toolbox_resources()
