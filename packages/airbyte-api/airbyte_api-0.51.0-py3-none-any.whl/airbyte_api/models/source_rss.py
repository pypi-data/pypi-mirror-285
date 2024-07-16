"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from typing import Final


class Rss(str, Enum):
    RSS = 'rss'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceRss:
    url: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('url') }})
    r"""RSS Feed URL"""
    SOURCE_TYPE: Final[Rss] = dataclasses.field(default=Rss.RSS, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('sourceType') }})
    

