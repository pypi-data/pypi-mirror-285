"""

    PROJECT: flex_toolbox
    FILENAME: test_flatten_dict.py
    AUTHOR: David NAISSE
    DATE: March 18, 2024

    DESCRIPTION: flatten dict function testing

"""
from unittest import TestCase

from src.utils import flatten_dict


class TestFlattenDict(TestCase):

    def test_flatten_dict(self):
        # ins
        dict = {
            "list": [
                {
                    "name": "name_1",
                    "item_1": "value_2"
                },
                {
                    "name": "name_2",
                    "item_2": "value_2"
                }
            ],
            "dict": {
                "dict_2": {
                    "item_3": "value_3"
                }
            }
        }

        # outs
        flattened_dict = flatten_dict(dict)

        # test
        assert flattened_dict.get('list.name_1.item_1') == "value_2" and flattened_dict.get('dict.dict_2.item_3') == "value_3"
