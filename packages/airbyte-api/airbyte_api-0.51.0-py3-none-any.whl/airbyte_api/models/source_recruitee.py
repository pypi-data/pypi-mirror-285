"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from typing import Final


class Recruitee(str, Enum):
    RECRUITEE = 'recruitee'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceRecruitee:
    api_key: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('api_key') }})
    r"""Recruitee API Key. See <a href=\\"https://docs.recruitee.com/reference/getting-started#generate-api-token\\">here</a>."""
    company_id: int = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('company_id') }})
    r"""Recruitee Company ID. You can also find this ID on the <a href=\\"https://app.recruitee.com/#/settings/api_tokens\\">Recruitee API tokens page</a>."""
    SOURCE_TYPE: Final[Recruitee] = dataclasses.field(default=Recruitee.RECRUITEE, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('sourceType') }})
    

