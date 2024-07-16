"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
from enum import Enum


class PermissionType(str, Enum):
    r"""Describes what actions/endpoints the permission entitles to"""
    INSTANCE_ADMIN = 'instance_admin'
    ORGANIZATION_ADMIN = 'organization_admin'
    ORGANIZATION_EDITOR = 'organization_editor'
    ORGANIZATION_READER = 'organization_reader'
    ORGANIZATION_MEMBER = 'organization_member'
    WORKSPACE_OWNER = 'workspace_owner'
    WORKSPACE_ADMIN = 'workspace_admin'
    WORKSPACE_EDITOR = 'workspace_editor'
    WORKSPACE_READER = 'workspace_reader'
