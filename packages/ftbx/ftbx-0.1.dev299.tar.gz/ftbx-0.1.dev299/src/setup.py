"""

    PROJECT: flex_toolbox
    FILENAME: setup.py
    AUTHOR: David NAISSE
    DATE: March 20, 2024

    DESCRIPTION: connect command

    TEST STATUS: DOES NOT REQUIRE TESTING
"""
import os
import re
from src.utils import download_file
from src.variables import sdk_version_from_flex_version


def setup_command_func(args):
    """
    Action on setup command.

    TEST STATUS: DOES NOT REQUIRE TESTING
    """

    version = args.version
    version_x = re.sub(r'\b(\d{4}\.\d{1,2})\.\d{1,2}\b', lambda x: x.group(1) + ".x", version)
    print(f"\nVersion: {version} ({version_x})")

    # create our dirs for docs and sdk
    os.makedirs('docs', exist_ok=True)
    os.makedirs('sdks', exist_ok=True)

    # find related sdk
    sdk = sdk_version_from_flex_version.get(version_x)
    if not sdk: raise KeyError(
        f"Cannot find {version} nor {version_x} in the variables.yml. Please check the information provided. ")

    # download doc
    download_file(url=f"https://help.dalet.com/daletflex/apis/flex-api-{version}.yml",
                  destination=os.path.join('docs', f"{version}.yml"))
    print(f"\nDOCUMENTATION: {version}.yml has been downloaded to docs/{version}.yml\n")

    # download sdk
    try:
        download_file(
            url=f"https://nexus-internal.ooflex.net/repository/maven/com/ooyala/flex/flex-sdk-external/{sdk}/flex-sdk-external-{sdk}.jar",
            destination=os.path.join('sdks', f"flex-sdk-external-{sdk}.jar"))
        print(f"SDK: flex-sdk-external-{sdk}.jar has been downloaded to sdks/flex-sdk-external-{sdk}.jar.\n")
    except Exception as ex:
        print("/!\\ Failed to download the sdk. Please connect to the dlt-fw-uk-UDP4-1120-full-config VPN /!\\ \n")
