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
import pprint
from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError, field_validator
from typing import Any, List, Optional
from antimatter_api.models.domain_identity_api_key_principal_params import DomainIdentityAPIKeyPrincipalParams
from antimatter_api.models.domain_identity_email_principal_params import DomainIdentityEmailPrincipalParams
from antimatter_api.models.domain_identity_hosted_domain_principal_params import DomainIdentityHostedDomainPrincipalParams
from pydantic import StrictStr, Field
from typing import Union, List, Optional, Dict
from typing_extensions import Literal, Self

DOMAINIDENTITYPRINCIPALDETAILS_ONE_OF_SCHEMAS = ["DomainIdentityAPIKeyPrincipalParams", "DomainIdentityEmailPrincipalParams", "DomainIdentityHostedDomainPrincipalParams"]

class DomainIdentityPrincipalDetails(BaseModel):
    """
    DomainIdentityPrincipalDetails
    """
    # data type: DomainIdentityAPIKeyPrincipalParams
    oneof_schema_1_validator: Optional[DomainIdentityAPIKeyPrincipalParams] = None
    # data type: DomainIdentityEmailPrincipalParams
    oneof_schema_2_validator: Optional[DomainIdentityEmailPrincipalParams] = None
    # data type: DomainIdentityHostedDomainPrincipalParams
    oneof_schema_3_validator: Optional[DomainIdentityHostedDomainPrincipalParams] = None
    actual_instance: Optional[Union[DomainIdentityAPIKeyPrincipalParams, DomainIdentityEmailPrincipalParams, DomainIdentityHostedDomainPrincipalParams]] = None
    one_of_schemas: List[str] = Field(default=Literal["DomainIdentityAPIKeyPrincipalParams", "DomainIdentityEmailPrincipalParams", "DomainIdentityHostedDomainPrincipalParams"])

    model_config = ConfigDict(
        validate_assignment=True,
        protected_namespaces=(),
    )


    discriminator_value_class_map: Dict[str, str] = {
    }

    def __init__(self, *args, **kwargs) -> None:
        if args:
            if len(args) > 1:
                raise ValueError("If a position argument is used, only 1 is allowed to set `actual_instance`")
            if kwargs:
                raise ValueError("If a position argument is used, keyword arguments cannot be used.")
            super().__init__(actual_instance=args[0])
        else:
            super().__init__(**kwargs)

    @field_validator('actual_instance')
    def actual_instance_must_validate_oneof(cls, v):
        instance = DomainIdentityPrincipalDetails.model_construct()
        error_messages = []
        match = 0
        # validate data type: DomainIdentityAPIKeyPrincipalParams
        if not isinstance(v, DomainIdentityAPIKeyPrincipalParams):
            error_messages.append(f"Error! Input type `{type(v)}` is not `DomainIdentityAPIKeyPrincipalParams`")
        else:
            match += 1
        # validate data type: DomainIdentityEmailPrincipalParams
        if not isinstance(v, DomainIdentityEmailPrincipalParams):
            error_messages.append(f"Error! Input type `{type(v)}` is not `DomainIdentityEmailPrincipalParams`")
        else:
            match += 1
        # validate data type: DomainIdentityHostedDomainPrincipalParams
        if not isinstance(v, DomainIdentityHostedDomainPrincipalParams):
            error_messages.append(f"Error! Input type `{type(v)}` is not `DomainIdentityHostedDomainPrincipalParams`")
        else:
            match += 1
        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when setting `actual_instance` in DomainIdentityPrincipalDetails with oneOf schemas: DomainIdentityAPIKeyPrincipalParams, DomainIdentityEmailPrincipalParams, DomainIdentityHostedDomainPrincipalParams. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when setting `actual_instance` in DomainIdentityPrincipalDetails with oneOf schemas: DomainIdentityAPIKeyPrincipalParams, DomainIdentityEmailPrincipalParams, DomainIdentityHostedDomainPrincipalParams. Details: " + ", ".join(error_messages))
        else:
            return v

    @classmethod
    def from_dict(cls, obj: Union[str, Dict[str, Any]]) -> Self:
        return cls.from_json(json.dumps(obj))

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Returns the object represented by the json string"""
        instance = cls.model_construct()
        error_messages = []
        match = 0

        # deserialize data into DomainIdentityAPIKeyPrincipalParams
        try:
            instance.actual_instance = DomainIdentityAPIKeyPrincipalParams.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into DomainIdentityEmailPrincipalParams
        try:
            instance.actual_instance = DomainIdentityEmailPrincipalParams.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into DomainIdentityHostedDomainPrincipalParams
        try:
            instance.actual_instance = DomainIdentityHostedDomainPrincipalParams.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))

        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when deserializing the JSON string into DomainIdentityPrincipalDetails with oneOf schemas: DomainIdentityAPIKeyPrincipalParams, DomainIdentityEmailPrincipalParams, DomainIdentityHostedDomainPrincipalParams. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when deserializing the JSON string into DomainIdentityPrincipalDetails with oneOf schemas: DomainIdentityAPIKeyPrincipalParams, DomainIdentityEmailPrincipalParams, DomainIdentityHostedDomainPrincipalParams. Details: " + ", ".join(error_messages))
        else:
            return instance

    def to_json(self) -> str:
        """Returns the JSON representation of the actual instance"""
        if self.actual_instance is None:
            return "null"

        if hasattr(self.actual_instance, "to_json") and callable(self.actual_instance.to_json):
            return self.actual_instance.to_json()
        else:
            return json.dumps(self.actual_instance)

    def to_dict(self) -> Optional[Union[Dict[str, Any], DomainIdentityAPIKeyPrincipalParams, DomainIdentityEmailPrincipalParams, DomainIdentityHostedDomainPrincipalParams]]:
        """Returns the dict representation of the actual instance"""
        if self.actual_instance is None:
            return None

        if hasattr(self.actual_instance, "to_dict") and callable(self.actual_instance.to_dict):
            return self.actual_instance.to_dict()
        else:
            # primitive type
            return self.actual_instance

    def to_str(self) -> str:
        """Returns the string representation of the actual instance"""
        return pprint.pformat(self.model_dump())


