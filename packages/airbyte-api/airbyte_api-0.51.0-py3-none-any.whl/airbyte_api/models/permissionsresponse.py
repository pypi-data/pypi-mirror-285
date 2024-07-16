"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from .permissionresponseread import PermissionResponseRead
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from typing import List


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class PermissionsResponse:
    r"""List/Array of multiple permissions"""
    data: List[PermissionResponseRead] = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('data') }})
    

