"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from .scheduletypewithbasicenum import ScheduleTypeWithBasicEnum
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class ConnectionScheduleResponse:
    r"""schedule for when the the connection should run, per the schedule type"""
    schedule_type: ScheduleTypeWithBasicEnum = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('scheduleType') }})
    basic_timing: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('basicTiming'), 'exclude': lambda f: f is None }})
    cron_expression: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('cronExpression'), 'exclude': lambda f: f is None }})
    

