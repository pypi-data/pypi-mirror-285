# coding: utf-8

"""
    Antimatter Public API

    Interact with the Antimatter Cloud API

    The version of the OpenAPI document: 1.1.5
    Contact: support@antimatter.io
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import json
from enum import Enum
from typing_extensions import Self


class TagTypeField(str, Enum):
    """
    the type of this tag
    """

    """
    allowed enum values
    """
    STRING = 'string'
    NUMBER = 'number'
    BOOLEAN = 'boolean'
    DATE = 'date'
    UNARY = 'unary'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of TagTypeField from a JSON string"""
        return cls(json.loads(json_str))


