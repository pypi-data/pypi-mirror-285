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
from typing import Any, ClassVar, Dict, List, Optional
from antimatter_api.models.domain_identity_provider_info import DomainIdentityProviderInfo
from typing import Optional, Set
from typing_extensions import Self

class DomainIdentityProviderList(BaseModel):
    """
    A list of identity providers
    """ # noqa: E501
    identity_providers: Optional[List[DomainIdentityProviderInfo]] = Field(default=None, description="A list of identity providers configured in a domain", alias="identityProviders")
    __properties: ClassVar[List[str]] = ["identityProviders"]

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
        """Create an instance of DomainIdentityProviderList from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in identity_providers (list)
        _items = []
        if self.identity_providers:
            for _item in self.identity_providers:
                if _item:
                    _items.append(_item.to_dict())
            _dict['identityProviders'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of DomainIdentityProviderList from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "identityProviders": [DomainIdentityProviderInfo.from_dict(_item) for _item in obj["identityProviders"]] if obj.get("identityProviders") is not None else None
        })
        return _obj


