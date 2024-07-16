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
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, ClassVar, Dict, List
from antimatter_api.models.data_tagging_hook_input_records_inner_elements_inner import DataTaggingHookInputRecordsInnerElementsInner
from typing import Optional, Set
from typing_extensions import Self

class DataTaggingHookInputRecordsInner(BaseModel):
    """
    DataTaggingHookInputRecordsInner
    """ # noqa: E501
    elements: List[DataTaggingHookInputRecordsInnerElementsInner] = Field(description="a batch of values associated with the same record (eg columns of a row), to be processed. ")
    __properties: ClassVar[List[str]] = ["elements"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of DataTaggingHookInputRecordsInner from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in elements (list)
        _items = []
        if self.elements:
            for _item in self.elements:
                if _item:
                    _items.append(_item.to_dict())
            _dict['elements'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of DataTaggingHookInputRecordsInner from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "elements": [DataTaggingHookInputRecordsInnerElementsInner.from_dict(_item) for _item in obj["elements"]] if obj.get("elements") is not None else None
        })
        return _obj


