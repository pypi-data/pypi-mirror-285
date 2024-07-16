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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List
from typing_extensions import Annotated
from typing import Optional, Set
from typing_extensions import Self

class VendorSettings(BaseModel):
    """
    Vendor settings for a domain
    """ # noqa: E501
    name: StrictStr = Field(description="The name of the vendor associated with the domain.")
    support_contact: StrictStr = Field(description="The contact point for the the vendor", alias="supportContact")
    managed_key_id: Annotated[str, Field(strict=True)] = Field(description="A UUID used for identifying root encryption keys.", alias="managedKeyId")
    hyok_disabled: StrictBool = Field(description="A flag that indicates whether the subdomains of this domain should have the HYOK (Hold Your Own Key) feature enabled in the UI. ", alias="HYOKDisabled")
    __properties: ClassVar[List[str]] = ["name", "supportContact", "managedKeyId", "HYOKDisabled"]

    @field_validator('managed_key_id')
    def managed_key_id_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^((dm-[1-9A-HJ-NP-Za-km-z]{11}|[a-z][a-z0-9_]{2,31})::)?([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}|default|active)$", value):
            raise ValueError(r"must validate the regular expression /^((dm-[1-9A-HJ-NP-Za-km-z]{11}|[a-z][a-z0-9_]{2,31})::)?([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}|default|active)$/")
        return value

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
        """Create an instance of VendorSettings from a JSON string"""
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
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of VendorSettings from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "name": obj.get("name"),
            "supportContact": obj.get("supportContact"),
            "managedKeyId": obj.get("managedKeyId"),
            "HYOKDisabled": obj.get("HYOKDisabled")
        })
        return _obj


