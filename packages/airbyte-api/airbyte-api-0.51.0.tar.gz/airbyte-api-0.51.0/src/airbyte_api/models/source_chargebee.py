"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import dateutil.parser
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from datetime import datetime
from enum import Enum
from typing import Final, Optional


class ProductCatalog(str, Enum):
    r"""Product Catalog version of your Chargebee site. Instructions on how to find your version you may find <a href=\\"https://apidocs.chargebee.com/docs/api?prod_cat_ver=2\\">here</a> under `API Version` section. If left blank, the product catalog version will be set to 2.0."""
    ONE_0 = '1.0'
    TWO_0 = '2.0'


class Chargebee(str, Enum):
    CHARGEBEE = 'chargebee'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceChargebee:
    site: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('site') }})
    r"""The site prefix for your Chargebee instance."""
    site_api_key: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('site_api_key') }})
    r"""Chargebee API Key. See the <a href=\\"https://docs.airbyte.com/integrations/sources/chargebee\\">docs</a> for more information on how to obtain this key."""
    start_date: datetime = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('start_date'), 'encoder': utils.datetimeisoformat(False), 'decoder': dateutil.parser.isoparse }})
    r"""UTC date and time in the format 2017-01-25T00:00:00.000Z. Any data before this date will not be replicated."""
    product_catalog: Optional[ProductCatalog] = dataclasses.field(default=ProductCatalog.TWO_0, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('product_catalog'), 'exclude': lambda f: f is None }})
    r"""Product Catalog version of your Chargebee site. Instructions on how to find your version you may find <a href=\\"https://apidocs.chargebee.com/docs/api?prod_cat_ver=2\\">here</a> under `API Version` section. If left blank, the product catalog version will be set to 2.0."""
    SOURCE_TYPE: Final[Chargebee] = dataclasses.field(default=Chargebee.CHARGEBEE, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('sourceType') }})
    

