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

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from openapi_client.models.device_metadata import DeviceMetadata
from openapi_client.models.push_token_create_query_resource_object_attributes_profile import PushTokenCreateQueryResourceObjectAttributesProfile
from typing import Optional, Set
from typing_extensions import Self

class PushTokenCreateQueryResourceObjectAttributes(BaseModel):
    """
    PushTokenCreateQueryResourceObjectAttributes
    """ # noqa: E501
    token: Optional[StrictStr] = Field(description="A push token from APNS or FCM.")
    platform: Optional[StrictStr] = Field(description="The platform on which the push token was created.")
    enablement_status: Optional[StrictStr] = Field(default='AUTHORIZED', description="This is the enablement status for the individual push token.")
    vendor: Optional[StrictStr] = Field(description="The vendor of the push token.")
    background: Optional[StrictStr] = Field(default='AVAILABLE', description="The background state of the push token.")
    device_metadata: Optional[DeviceMetadata] = None
    profile: PushTokenCreateQueryResourceObjectAttributesProfile
    __properties: ClassVar[List[str]] = ["token", "platform", "enablement_status", "vendor", "background", "device_metadata", "profile"]

    @field_validator('platform')
    def platform_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['android', 'ios']):
            raise ValueError("must be one of enum values ('android', 'ios')")
        return value

    @field_validator('enablement_status')
    def enablement_status_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['AUTHORIZED', 'DENIED', 'NOT_DETERMINED', 'PROVISIONAL', 'UNAUTHORIZED']):
            raise ValueError("must be one of enum values ('AUTHORIZED', 'DENIED', 'NOT_DETERMINED', 'PROVISIONAL', 'UNAUTHORIZED')")
        return value

    @field_validator('vendor')
    def vendor_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['apns', 'fcm']):
            raise ValueError("must be one of enum values ('apns', 'fcm')")
        return value

    @field_validator('background')
    def background_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['AVAILABLE', 'DENIED', 'RESTRICTED']):
            raise ValueError("must be one of enum values ('AVAILABLE', 'DENIED', 'RESTRICTED')")
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
        """Create an instance of PushTokenCreateQueryResourceObjectAttributes from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of device_metadata
        if self.device_metadata:
            _dict['device_metadata'] = self.device_metadata.to_dict()
        # override the default output from pydantic by calling `to_dict()` of profile
        if self.profile:
            _dict['profile'] = self.profile.to_dict()
        # set to None if token (nullable) is None
        # and model_fields_set contains the field
        if self.token is None and "token" in self.model_fields_set:
            _dict['token'] = None

        # set to None if platform (nullable) is None
        # and model_fields_set contains the field
        if self.platform is None and "platform" in self.model_fields_set:
            _dict['platform'] = None

        # set to None if enablement_status (nullable) is None
        # and model_fields_set contains the field
        if self.enablement_status is None and "enablement_status" in self.model_fields_set:
            _dict['enablement_status'] = None

        # set to None if vendor (nullable) is None
        # and model_fields_set contains the field
        if self.vendor is None and "vendor" in self.model_fields_set:
            _dict['vendor'] = None

        # set to None if background (nullable) is None
        # and model_fields_set contains the field
        if self.background is None and "background" in self.model_fields_set:
            _dict['background'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PushTokenCreateQueryResourceObjectAttributes from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "token": obj.get("token"),
            "platform": obj.get("platform"),
            "enablement_status": obj.get("enablement_status") if obj.get("enablement_status") is not None else 'AUTHORIZED',
            "vendor": obj.get("vendor"),
            "background": obj.get("background") if obj.get("background") is not None else 'AVAILABLE',
            "device_metadata": DeviceMetadata.from_dict(obj["device_metadata"]) if obj.get("device_metadata") is not None else None,
            "profile": PushTokenCreateQueryResourceObjectAttributesProfile.from_dict(obj["profile"]) if obj.get("profile") is not None else None
        })
        return _obj


