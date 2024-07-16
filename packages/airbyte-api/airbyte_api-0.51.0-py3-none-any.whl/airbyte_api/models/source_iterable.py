"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import dateutil.parser
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from datetime import datetime
from enum import Enum
from typing import Final


class Iterable(str, Enum):
    ITERABLE = 'iterable'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceIterable:
    api_key: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('api_key') }})
    r"""Iterable API Key. See the <a href=\\\"https://docs.airbyte.com/integrations/sources/iterable\\\">docs</a>  for more information on how to obtain this key."""
    start_date: datetime = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('start_date'), 'encoder': utils.datetimeisoformat(False), 'decoder': dateutil.parser.isoparse }})
    r"""The date from which you'd like to replicate data for Iterable, in the format YYYY-MM-DDT00:00:00Z.  All data generated after this date will be replicated."""
    SOURCE_TYPE: Final[Iterable] = dataclasses.field(default=Iterable.ITERABLE, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('sourceType') }})
    

