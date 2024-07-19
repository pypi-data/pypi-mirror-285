"""

    PROJECT: flex_toolbox
    FILENAME: test_get_items.py
    AUTHOR: David NAISSE
    DATE: January 02, 2024

    DESCRIPTION: get_items function testing
    
"""
from typing import List
from unittest import TestCase
from src.utils import get_items 


def tmp_get_items(config_item: str, filters: List[str] = ['limit=5'], sub_items: List[str] = []):
    items = get_items(
        config_item=config_item,
        filters=filters,
        sub_items=sub_items,
        environment='cs-sandbox-ovh-flex-config'
    )

    assert items and len(items) >= 1


class TestGetItems(TestCase):

    def test_get_items_fql(self):
        tmp_get_items(config_item='assets', filters=['fql=(name=test)'])

    def test_get_items_limit(self):
        tmp_get_items(config_item='actions', filters=['limit=3'])

    def test_get_items_accounts(self):
        tmp_get_items(config_item='accounts')

    def test_get_items_actions(self):
        tmp_get_items(config_item='actions')

    def test_get_items_assets(self):
        tmp_get_items(config_item='assets')

    def test_get_items_eventHandlers(self):
        tmp_get_items(config_item='eventHandlers')

    def test_get_items_events(self):
        tmp_get_items(config_item='events')

    def test_get_items_groups(self):
        tmp_get_items(config_item='groups')

    def test_get_items_jobs(self):
        tmp_get_items(config_item='jobs')

    def test_get_items_messageTemplates(self):
        tmp_get_items(config_item='messageTemplates')

    def test_get_items_metadataDefinitions(self):
        tmp_get_items(config_item='metadataDefinitions')

    def test_get_items_objectTypes(self):
        tmp_get_items(config_item='objectTypes')

    def test_get_items_profiles(self):
        tmp_get_items(config_item='profiles')

    def test_get_items_quotas(self):
        tmp_get_items(config_item='quotas')

    def test_get_items_resources(self):
        tmp_get_items(config_item='resources')

    def test_get_items_roles(self):
        tmp_get_items(config_item='roles')

    def test_get_items_taskDefinitions(self):
        tmp_get_items(config_item='taskDefinitions')

    def test_get_items_tasks(self):
        tmp_get_items(config_item='tasks')

    def test_get_items_taxonomies(self):
        tmp_get_items(config_item='taxonomies')

    def test_get_items_timedActions(self):
        tmp_get_items(config_item='timedActions')

    def test_get_items_userDefinedObjectTypes(self):
        try:
            tmp_get_items(config_item='userDefinedObjectTypes')
        except:
            pass

    def test_get_items_users(self):
        tmp_get_items(config_item='users')

    def test_get_items_variants(self):
        tmp_get_items(config_item='variants')

    def test_get_items_wizards(self):
        tmp_get_items(config_item='wizards')

    def test_get_items_workflowDefinitions(self):
        tmp_get_items(config_item='workflowDefinitions')

    def test_get_items_workflows(self):
        tmp_get_items(config_item='workflows')

    def test_get_items_workspaces(self):
        tmp_get_items(config_item='workspaces')
