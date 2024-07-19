#!/usr/bin/python3

"""

    PROJECT: flex_toolbox
    FILENAME: toolbox.py
    AUTHOR: David NAISSE
    DATE: September 07, 2023

    DESCRIPTION: terminal command reader

"""

import argparse

from src.create import create_command_func
from src.compare import compare_command_func
from src.connect import connect_command_func
from src.env import env_command_func
from src.init import init_command_func
from src.launch import launch_command_func
from src.list import list_command_func
from src.pull import pull_command_func
from src.push import push_command_func
from src.query import query_command_func
from src.restore import restore_command_func
from src.retry import retry_command_func
from src.setup import setup_command_func
from src.update import update_command_func
from src.variables import Variables
from src.workflow_designer import workflow_designer_command_func
from src.metadata_designer import metadata_designer_command_func


def main():
    # parser
    parser = argparse.ArgumentParser(description='Flex Toolbox')
    subparsers = parser.add_subparsers(help='Commands')

    # init
    init_command = subparsers.add_parser('init', help='Initialize FTBX')
    init_command.set_defaults(func=init_command_func)

    # update
    update_command = subparsers.add_parser('update', help='Update FTBX')
    update_command.set_defaults(func=update_command_func)

    # connect
    connect_command = subparsers.add_parser('connect', help='Connect to a Flex environment')
    connect_command.add_argument('env_url', type=str, help='URL of the Flex environment (ex: https://my-env-url.com)')
    connect_command.add_argument('username', type=str, nargs='?', help='Flex username')
    connect_command.add_argument('password', type=str, nargs='?', help='Flex password')
    connect_command.add_argument('--alias', type=str, nargs='?', help='Env alias (ex: wb-stg, fm-prod..)')
    connect_command.set_defaults(func=connect_command_func)

    # env
    env_command = subparsers.add_parser('env', help='Show available and default environments')
    env_command.set_defaults(func=env_command_func)

    # setup
    setup_command = subparsers.add_parser('setup', help='Download the documentation and SDK for a given Flex version')
    setup_command.add_argument('version', type=str, help="The version you want to get the documentation and SDK from (ex: 2022.5.7)")
    setup_command.set_defaults(func=setup_command_func)

    # query
    query_command = subparsers.add_parser('query', help='Query (GET, POST, PUT, DELETE) an environment')
    query_command.add_argument('method', type=str, choices=['GET', 'POST', 'PUT', 'DELETE'], default='GET')
    query_command.add_argument('url', type=str, help='Query to send (ex: workflows/<workflow_id>/variables)')
    query_command.add_argument('--from', dest="from_", type=str, help='Environment to query', default="default")
    query_command.add_argument('--payload', type=str, nargs='*', help='File or arguments to use as payload (ex: "assetId=30456", or payload.json)')
    query_command.add_argument('--stdout', action="store_true", help="Print the query in the terminal (does not disable writing to query.json)")
    query_command.set_defaults(func=query_command_func)

    # list
    list_command = subparsers.add_parser('list', help='List (to CSV & JSON) config items from an environment, with filters and post-filters')
    list_command.add_argument('config_item', type=str, choices=Variables.CommandOptions.list, help='Config item to list')
    list_command.add_argument('--filters', type=str, nargs="*", help="Filters to use (from the API doc)")
    list_command.add_argument('--post-filters', dest="post_filters", type=str, nargs="*", help="Post retrieval filters (custom)")
    list_command.add_argument('--from', dest="from_", type=str, help="Environment to list items from", default="default")
    list_command.add_argument('--from-csv', dest='from_csv', type=str, help='[TMP] CSV file from which items must be listed', default=None)
    list_command.add_argument('--name', type=str, help="Name of the output file (ex: my_list, a_list_about_smth..)", default=None)
    list_command.set_defaults(func=list_command_func)

    # pull
    pull_command = subparsers.add_parser('pull', help='Pull (files & folders) config items from an environment, with filters and post-filters')
    pull_command.add_argument('config_item', type=str, choices=Variables.CommandOptions.pull, help='Config item to pull')
    pull_command.add_argument('--filters', type=str, nargs='*', help='Filters to use (from the API doc)')
    pull_command.add_argument('--with-dependencies', dest="with_dependencies", action='store_true', help='Whether to retrieve items dependencies')
    pull_command.add_argument('--post-filters', dest="post_filters", type=str, nargs="*", help="Post retrieval filters")
    pull_command.add_argument('--from', dest="from_", type=str, nargs="*", help="Environments to pull items from")
    pull_command.set_defaults(func=pull_command_func)

    # create
    create_command = subparsers.add_parser('create', help='Create a config item within an environment if no item with same name already exist')
    create_command.add_argument('config_item', type=str, choices=Variables.CommandOptions.create, help='Config item to create')
    create_command.add_argument('plugin', type=str, choices=['decision', 'script', 'launchWorkflow'], help='Plugin to use for the new item')
    create_command.add_argument('item_name', type=str, help='Name of the item to create')
    create_command.add_argument('--in', dest="in_", type=str, default="default", help='Environment to create item in')
    create_command.set_defaults(func=create_command_func)

    # push
    push_command = subparsers.add_parser('push', help='Push (create or update) config items to an environment')
    push_command.add_argument('config_item', type=str, choices=Variables.CommandOptions.push, help='Config item to push')
    push_command.add_argument('item_names', type=str, nargs='*', help='Item(s) to push')
    push_command.add_argument('--from', dest="from_", type=str, default="default", help='Environment to push from')
    push_command.add_argument('--to', type=str, nargs='*', default=["default"], help='Environments to push to')
    push_command.add_argument('--push-to-failed-jobs', nargs='?', const=True, default=False, help='Whether to retry failed jobs with new code. If a is provided, it will be treated as a filename.')
    push_command.add_argument('--retry', nargs='?', const=True, default=False, help='Whether to retry the given instance after pushing changes (jobs, workflows).')
    push_command.add_argument('--with-dependencies', nargs='?', const=True, default=False, help='Whether to push dependencies along with the item you are pushing')
    push_command.add_argument('--include-resources', nargs='?', const=True, default=False, help='/!\\ Whether to also push resource configurations, this will overwrite the corresponding destination environment resource configurations /!\\')
    push_command.add_argument('--listen', action='store_true', help='Whether to listen to pushed and retried jobs')
    # push_command.add_argument('--all', type=bool, help='Whether to push all config items or not')
    # todo: same syntax than pull
    push_command.set_defaults(func=push_command_func)

    # restore
    # todo: env
    restore_command = subparsers.add_parser('restore', help='Restore config items to a previous point in time')
    restore_command.add_argument('config_item', type=str, choices=Variables.CommandOptions.restore, help='Config item to restore')
    restore_command.add_argument('item_name', type=str, help='Item to restore (ex: "my-resource-name")')
    restore_command.add_argument('backup', type=str, help='Backup to restore (ex: "2024-03-25 12h51m10s")')
    restore_command.set_defaults(func=restore_command_func)

    # compare
    compare_command = subparsers.add_parser('compare', help='Compare config items against several environments')
    compare_command.add_argument('config_item', type=str, choices=Variables.CommandOptions.compare, help='Config item to compare')
    compare_command.add_argument('environments', type=str, nargs='*', help='Environments')
    compare_command.add_argument('--filters', type=str, nargs='*', help='Filters to use (from the API doc)')
    compare_command.set_defaults(func=compare_command_func)

    # retry
    retry_command = subparsers.add_parser('retry', help='Retry or bulk retry config item instances within an environment')
    retry_command.add_argument('config_item', type=str, choices=Variables.CommandOptions.retry, help='Config item')
    retry_command.add_argument('--from', dest="from_", type=str, default="default", help='Environment to retry from')
    retry_command.add_argument('--filters', type=str, nargs='*', default=[], help='Filters to use (from the API doc)')
    retry_command.add_argument('--file', type=str, default=None, help='File containing items to retry (ex: CSV or JSON from ftbx list)')
    retry_command.set_defaults(func=retry_command_func)

    # launch
    launch_command = subparsers.add_parser('launch', help='Launch a config item instance within an environment')
    launch_command.add_argument('config_item', type=str, choices=Variables.CommandOptions.launch, help='Config item to launch')
    launch_command.add_argument('item_name', type=str, help='Item name')
    launch_command.add_argument('--in', dest="in_", type=str, default="default", help='Environment to launch instance in')
    launch_command.add_argument('--params', type=str, nargs='*', default=[], help='Parameters to use (ex: "assetId=1234", "workspaceId=303"..)')
    launch_command.add_argument('--from-file', type=str, help='Parameters file to use (ex: params.json..)')
    launch_command.add_argument('--use-local', nargs='?', const=True, default=False, help='Whether to push local config to remote before launching an instance')
    launch_command.add_argument('--listen', nargs='?', const=True, default=False, help='Whether to listen to the launched job')
    launch_command.set_defaults(func=launch_command_func)

    # workflowDesigner
    workflow_designer_command = subparsers.add_parser('workflowDesigner', help='Opens a browser window with the given workflow designer')
    workflow_designer_command.add_argument('workflow_name', type=str, help='Name of the workflow to open')
    workflow_designer_command.add_argument('--in', dest='in_', type=str, default='default', help='Environment to launch workflow designer in')
    workflow_designer_command.set_defaults(func=workflow_designer_command_func)

    # metadataDesigner
    metadata_designer_command = subparsers.add_parser('metadataDesigner', help='Opens a browser window with the given metadata designer')
    metadata_designer_command.add_argument('--in', dest='in_', type=str, default='default', help='Environment to launch metadata designer in')
    metadata_designer_command.set_defaults(func=metadata_designer_command_func)

    # todo:
    #     1 refactor ftbx.py to contain parser with depth=3
    #     1 create items from CSV
    #     logs and log file
    #     cancel
    #     sync
    #     major speedup required for get_items with threads

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
   main() 
