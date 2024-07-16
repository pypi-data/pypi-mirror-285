"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from .workspaceresponse import WorkspaceResponse
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from typing import List, Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class WorkspacesResponse:
    data: List[WorkspaceResponse] = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('data') }})
    next: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('next'), 'exclude': lambda f: f is None }})
    previous: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('previous'), 'exclude': lambda f: f is None }})
    

