"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from typing import Final, Optional


class SourceKlarnaRegion(str, Enum):
    r"""Base url region (For playground eu https://docs.klarna.com/klarna-payments/api/payments-api/#tag/API-URLs). Supported 'eu', 'na', 'oc'"""
    EU = 'eu'
    NA = 'na'
    OC = 'oc'


class Klarna(str, Enum):
    KLARNA = 'klarna'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceKlarna:
    password: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('password') }})
    r"""A string which is associated with your Merchant ID and is used to authorize use of Klarna's APIs (https://developers.klarna.com/api/#authentication)"""
    region: SourceKlarnaRegion = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('region') }})
    r"""Base url region (For playground eu https://docs.klarna.com/klarna-payments/api/payments-api/#tag/API-URLs). Supported 'eu', 'na', 'oc'"""
    username: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('username') }})
    r"""Consists of your Merchant ID (eid) - a unique number that identifies your e-store, combined with a random string (https://developers.klarna.com/api/#authentication)"""
    playground: Optional[bool] = dataclasses.field(default=False, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('playground'), 'exclude': lambda f: f is None }})
    r"""Propertie defining if connector is used against playground or production environment"""
    SOURCE_TYPE: Final[Klarna] = dataclasses.field(default=Klarna.KLARNA, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('sourceType') }})
    

