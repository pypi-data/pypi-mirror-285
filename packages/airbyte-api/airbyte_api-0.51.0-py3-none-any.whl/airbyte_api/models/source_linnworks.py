"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import dateutil.parser
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from datetime import datetime
from enum import Enum
from typing import Final


class Linnworks(str, Enum):
    LINNWORKS = 'linnworks'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceLinnworks:
    application_id: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('application_id') }})
    r"""Linnworks Application ID"""
    application_secret: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('application_secret') }})
    r"""Linnworks Application Secret"""
    start_date: datetime = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('start_date'), 'encoder': utils.datetimeisoformat(False), 'decoder': dateutil.parser.isoparse }})
    r"""UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated."""
    token: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('token') }})
    SOURCE_TYPE: Final[Linnworks] = dataclasses.field(default=Linnworks.LINNWORKS, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('sourceType') }})
    

