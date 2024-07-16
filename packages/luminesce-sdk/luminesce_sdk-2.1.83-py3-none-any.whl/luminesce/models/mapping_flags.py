# coding: utf-8

"""
    FINBOURNE Luminesce Web API

    FINBOURNE Technology  # noqa: E501

    Contact: info@finbourne.com
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""


import json
import pprint
import re  # noqa: F401
from aenum import Enum, no_arg





class MappingFlags(str, Enum):
    """
    MappingFlags
    """

    """
    allowed enum values
    """
    NONE = 'None'
    EXACT = 'Exact'
    SIMILAR = 'Similar'
    ADDITIONAL = 'Additional'

    @classmethod
    def from_json(cls, json_str: str) -> MappingFlags:
        """Create an instance of MappingFlags from a JSON string"""
        return MappingFlags(json.loads(json_str))
