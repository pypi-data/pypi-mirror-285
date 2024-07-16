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
import json
from enum import Enum
from typing_extensions import Self


class CampaignMessageEnum(str, Enum):
    """
    CampaignMessageEnum
    """

    """
    allowed enum values
    """
    CAMPAIGN_MINUS_MESSAGE = 'campaign-message'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of CampaignMessageEnum from a JSON string"""
        return cls(json.loads(json_str))


