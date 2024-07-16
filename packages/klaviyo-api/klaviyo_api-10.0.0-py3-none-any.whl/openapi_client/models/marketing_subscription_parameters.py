# coding: utf-8

"""
    Klaviyo API

    The Klaviyo REST API. Please visit https://developers.klaviyo.com for more details.

    The version of the OpenAPI document: 2024-07-15
    Contact: developers@klaviyo.com
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class MarketingSubscriptionParameters(BaseModel):
    """
    MarketingSubscriptionParameters
    """ # noqa: E501
    consent: StrictStr = Field(description="The Consent status to subscribe to for the \"Marketing\" type. Currently supports \"SUBSCRIBED\".")
    consented_at: Optional[datetime] = Field(default=None, description="The timestamp of when the profile's consent was gathered. This should only be used when syncing over historical consent info to Klaviyo; if the `historical_import` flag is not included, providing any value for this field will raise an error.")
    __properties: ClassVar[List[str]] = ["consent", "consented_at"]

    @field_validator('consent')
    def consent_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['SUBSCRIBED']):
            raise ValueError("must be one of enum values ('SUBSCRIBED')")
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
        """Create an instance of MarketingSubscriptionParameters from a JSON string"""
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
        # set to None if consented_at (nullable) is None
        # and model_fields_set contains the field
        if self.consented_at is None and "consented_at" in self.model_fields_set:
            _dict['consented_at'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of MarketingSubscriptionParameters from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "consent": obj.get("consent"),
            "consented_at": obj.get("consented_at")
        })
        return _obj


