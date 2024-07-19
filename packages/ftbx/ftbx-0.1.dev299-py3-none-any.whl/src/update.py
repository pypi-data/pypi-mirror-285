"""

    PROJECT: flex_toolbox
    FILENAME: update.py
    AUTHOR: David NAISSE
    DATE: March 3rd, 2024

    DESCRIPTION: update command functions

    TEST STATUS: DOES NOT REQUIRE TESTING
"""

import subprocess
import os

from src.utils import update_toolbox_resources


def update_command_func(args):
    """
    Action on update command.

    TEST STATUS: DOES NOT REQUIRE TESTING
    """

    print(f"\nUpdating ftbx to latest version..\n")
    subprocess.run(
        [
            "pip",
            "install",
            "ftbx",
            "--upgrade",
            "--quiet",
        ],
        check=True,
    )

    print('#' * os.get_terminal_size().columns)
    subprocess.run(["pip", "show", "ftbx"])
    print('#' * os.get_terminal_size().columns + "\n")

    # fetch updated resources
    update_toolbox_resources()
