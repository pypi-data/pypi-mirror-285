"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from .permissiontype import PermissionType
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class PermissionResponse:
    r"""Provides details of a single permission."""
    permission_id: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('permissionId') }})
    permission_type: PermissionType = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('permissionType') }})
    r"""Describes what actions/endpoints the permission entitles to"""
    user_id: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('userId') }})
    r"""Internal Airbyte user ID"""
    organization_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('organizationId'), 'exclude': lambda f: f is None }})
    workspace_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('workspaceId'), 'exclude': lambda f: f is None }})
    

