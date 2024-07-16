"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from .jobstatusenum import JobStatusEnum
from .jobtypeenum import JobTypeEnum
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class JobResponse:
    r"""Provides details of a single job."""
    connection_id: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('connectionId') }})
    job_id: int = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('jobId') }})
    job_type: JobTypeEnum = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('jobType') }})
    r"""Enum that describes the different types of jobs that the platform runs."""
    start_time: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('startTime') }})
    status: JobStatusEnum = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('status') }})
    bytes_synced: Optional[int] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('bytesSynced'), 'exclude': lambda f: f is None }})
    duration: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('duration'), 'exclude': lambda f: f is None }})
    r"""Duration of a sync in ISO_8601 format"""
    last_updated_at: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('lastUpdatedAt'), 'exclude': lambda f: f is None }})
    rows_synced: Optional[int] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('rowsSynced'), 'exclude': lambda f: f is None }})
    

