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

from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from openapi_client.models.profile_location import ProfileLocation
from typing import Optional, Set
from typing_extensions import Self

class ProfilePartialUpdateQueryResourceObjectAttributes(BaseModel):
    """
    ProfilePartialUpdateQueryResourceObjectAttributes
    """ # noqa: E501
    email: Optional[StrictStr] = Field(default=None, description="Individual's email address")
    phone_number: Optional[StrictStr] = Field(default=None, description="Individual's phone number in E.164 format")
    external_id: Optional[StrictStr] = Field(default=None, description="A unique identifier used by customers to associate Klaviyo profiles with profiles in an external system, such as a point-of-sale system. Format varies based on the external system.")
    anonymous_id: Optional[StrictStr] = None
    first_name: Optional[StrictStr] = Field(default=None, description="Individual's first name")
    last_name: Optional[StrictStr] = Field(default=None, description="Individual's last name")
    organization: Optional[StrictStr] = Field(default=None, description="Name of the company or organization within the company for whom the individual works")
    title: Optional[StrictStr] = Field(default=None, description="Individual's job title")
    image: Optional[StrictStr] = Field(default=None, description="URL pointing to the location of a profile image")
    location: Optional[ProfileLocation] = None
    properties: Optional[Dict[str, Any]] = Field(default=None, description="An object containing key/value pairs for any custom properties assigned to this profile")
    __properties: ClassVar[List[str]] = ["email", "phone_number", "external_id", "anonymous_id", "first_name", "last_name", "organization", "title", "image", "location", "properties"]

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
        """Create an instance of ProfilePartialUpdateQueryResourceObjectAttributes from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of location
        if self.location:
            _dict['location'] = self.location.to_dict()
        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

        # set to None if phone_number (nullable) is None
        # and model_fields_set contains the field
        if self.phone_number is None and "phone_number" in self.model_fields_set:
            _dict['phone_number'] = None

        # set to None if external_id (nullable) is None
        # and model_fields_set contains the field
        if self.external_id is None and "external_id" in self.model_fields_set:
            _dict['external_id'] = None

        # set to None if anonymous_id (nullable) is None
        # and model_fields_set contains the field
        if self.anonymous_id is None and "anonymous_id" in self.model_fields_set:
            _dict['anonymous_id'] = None

        # set to None if first_name (nullable) is None
        # and model_fields_set contains the field
        if self.first_name is None and "first_name" in self.model_fields_set:
            _dict['first_name'] = None

        # set to None if last_name (nullable) is None
        # and model_fields_set contains the field
        if self.last_name is None and "last_name" in self.model_fields_set:
            _dict['last_name'] = None

        # set to None if organization (nullable) is None
        # and model_fields_set contains the field
        if self.organization is None and "organization" in self.model_fields_set:
            _dict['organization'] = None

        # set to None if title (nullable) is None
        # and model_fields_set contains the field
        if self.title is None and "title" in self.model_fields_set:
            _dict['title'] = None

        # set to None if image (nullable) is None
        # and model_fields_set contains the field
        if self.image is None and "image" in self.model_fields_set:
            _dict['image'] = None

        # set to None if properties (nullable) is None
        # and model_fields_set contains the field
        if self.properties is None and "properties" in self.model_fields_set:
            _dict['properties'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ProfilePartialUpdateQueryResourceObjectAttributes from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "email": obj.get("email"),
            "phone_number": obj.get("phone_number"),
            "external_id": obj.get("external_id"),
            "anonymous_id": obj.get("anonymous_id"),
            "first_name": obj.get("first_name"),
            "last_name": obj.get("last_name"),
            "organization": obj.get("organization"),
            "title": obj.get("title"),
            "image": obj.get("image"),
            "location": ProfileLocation.from_dict(obj["location"]) if obj.get("location") is not None else None,
            "properties": obj.get("properties")
        })
        return _obj


