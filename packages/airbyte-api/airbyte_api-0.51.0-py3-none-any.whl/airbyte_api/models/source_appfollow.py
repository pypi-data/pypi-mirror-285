"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from typing import Final, Optional


class Appfollow(str, Enum):
    APPFOLLOW = 'appfollow'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceAppfollow:
    api_secret: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('api_secret'), 'exclude': lambda f: f is None }})
    r"""API Key provided by Appfollow"""
    SOURCE_TYPE: Final[Appfollow] = dataclasses.field(default=Appfollow.APPFOLLOW, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('sourceType') }})
    

