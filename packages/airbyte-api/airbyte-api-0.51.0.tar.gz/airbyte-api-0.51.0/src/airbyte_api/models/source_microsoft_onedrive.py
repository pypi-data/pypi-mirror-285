"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import dateutil.parser
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from datetime import datetime
from enum import Enum
from typing import Final, List, Optional, Union


class SourceMicrosoftOnedriveSchemasAuthType(str, Enum):
    SERVICE = 'Service'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class ServiceKeyAuthentication:
    r"""ServiceCredentials class for service key authentication.
    This class is structured similarly to OAuthCredentials but for a different authentication method.
    """
    client_id: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('client_id') }})
    r"""Client ID of your Microsoft developer application"""
    client_secret: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('client_secret') }})
    r"""Client Secret of your Microsoft developer application"""
    tenant_id: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('tenant_id') }})
    r"""Tenant ID of the Microsoft OneDrive user"""
    user_principal_name: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('user_principal_name') }})
    r"""Special characters such as a period, comma, space, and the at sign (@) are converted to underscores (_). More details: https://learn.microsoft.com/en-us/sharepoint/list-onedrive-urls"""
    AUTH_TYPE: Final[Optional[SourceMicrosoftOnedriveSchemasAuthType]] = dataclasses.field(default=SourceMicrosoftOnedriveSchemasAuthType.SERVICE, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('auth_type'), 'exclude': lambda f: f is None }})
    



class SourceMicrosoftOnedriveAuthType(str, Enum):
    CLIENT = 'Client'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class AuthenticateViaMicrosoftOAuth:
    r"""OAuthCredentials class to hold authentication details for Microsoft OAuth authentication.
    This class uses pydantic for data validation and settings management.
    """
    client_id: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('client_id') }})
    r"""Client ID of your Microsoft developer application"""
    client_secret: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('client_secret') }})
    r"""Client Secret of your Microsoft developer application"""
    refresh_token: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('refresh_token') }})
    r"""Refresh Token of your Microsoft developer application"""
    tenant_id: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('tenant_id') }})
    r"""Tenant ID of the Microsoft OneDrive user"""
    AUTH_TYPE: Final[Optional[SourceMicrosoftOnedriveAuthType]] = dataclasses.field(default=SourceMicrosoftOnedriveAuthType.CLIENT, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('auth_type'), 'exclude': lambda f: f is None }})
    



class SearchScope(str, Enum):
    r"""Specifies the location(s) to search for files. Valid options are 'ACCESSIBLE_DRIVES' to search in the selected OneDrive drive, 'SHARED_ITEMS' for shared items the user has access to, and 'ALL' to search both."""
    ACCESSIBLE_DRIVES = 'ACCESSIBLE_DRIVES'
    SHARED_ITEMS = 'SHARED_ITEMS'
    ALL = 'ALL'


class SourceMicrosoftOnedriveMicrosoftOnedrive(str, Enum):
    MICROSOFT_ONEDRIVE = 'microsoft-onedrive'


class SourceMicrosoftOnedriveSchemasStreamsFormatFormatFiletype(str, Enum):
    UNSTRUCTURED = 'unstructured'


class SourceMicrosoftOnedriveMode(str, Enum):
    LOCAL = 'local'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceMicrosoftOnedriveLocal:
    r"""Process files locally, supporting `fast` and `ocr` modes. This is the default option."""
    MODE: Final[Optional[SourceMicrosoftOnedriveMode]] = dataclasses.field(default=SourceMicrosoftOnedriveMode.LOCAL, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('mode'), 'exclude': lambda f: f is None }})
    



class SourceMicrosoftOnedriveParsingStrategy(str, Enum):
    r"""The strategy used to parse documents. `fast` extracts text directly from the document which doesn't work for all files. `ocr_only` is more reliable, but slower. `hi_res` is the most reliable, but requires an API key and a hosted instance of unstructured and can't be used with local mode. See the unstructured.io documentation for more details: https://unstructured-io.github.io/unstructured/core/partition.html#partition-pdf"""
    AUTO = 'auto'
    FAST = 'fast'
    OCR_ONLY = 'ocr_only'
    HI_RES = 'hi_res'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class UnstructuredDocumentFormat:
    r"""Extract text from document formats (.pdf, .docx, .md, .pptx) and emit as one record per file."""
    FILETYPE: Final[Optional[SourceMicrosoftOnedriveSchemasStreamsFormatFormatFiletype]] = dataclasses.field(default=SourceMicrosoftOnedriveSchemasStreamsFormatFormatFiletype.UNSTRUCTURED, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('filetype'), 'exclude': lambda f: f is None }})
    processing: Optional[SourceMicrosoftOnedriveProcessing] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('processing'), 'exclude': lambda f: f is None }})
    r"""Processing configuration"""
    skip_unprocessable_files: Optional[bool] = dataclasses.field(default=True, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('skip_unprocessable_files'), 'exclude': lambda f: f is None }})
    r"""If true, skip files that cannot be parsed and pass the error message along as the _ab_source_file_parse_error field. If false, fail the sync."""
    strategy: Optional[SourceMicrosoftOnedriveParsingStrategy] = dataclasses.field(default=SourceMicrosoftOnedriveParsingStrategy.AUTO, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('strategy'), 'exclude': lambda f: f is None }})
    r"""The strategy used to parse documents. `fast` extracts text directly from the document which doesn't work for all files. `ocr_only` is more reliable, but slower. `hi_res` is the most reliable, but requires an API key and a hosted instance of unstructured and can't be used with local mode. See the unstructured.io documentation for more details: https://unstructured-io.github.io/unstructured/core/partition.html#partition-pdf"""
    



class SourceMicrosoftOnedriveSchemasStreamsFormatFiletype(str, Enum):
    PARQUET = 'parquet'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceMicrosoftOnedriveParquetFormat:
    decimal_as_float: Optional[bool] = dataclasses.field(default=False, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('decimal_as_float'), 'exclude': lambda f: f is None }})
    r"""Whether to convert decimal fields to floats. There is a loss of precision when converting decimals to floats, so this is not recommended."""
    FILETYPE: Final[Optional[SourceMicrosoftOnedriveSchemasStreamsFormatFiletype]] = dataclasses.field(default=SourceMicrosoftOnedriveSchemasStreamsFormatFiletype.PARQUET, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('filetype'), 'exclude': lambda f: f is None }})
    



class SourceMicrosoftOnedriveSchemasStreamsFiletype(str, Enum):
    JSONL = 'jsonl'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceMicrosoftOnedriveJsonlFormat:
    FILETYPE: Final[Optional[SourceMicrosoftOnedriveSchemasStreamsFiletype]] = dataclasses.field(default=SourceMicrosoftOnedriveSchemasStreamsFiletype.JSONL, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('filetype'), 'exclude': lambda f: f is None }})
    



class SourceMicrosoftOnedriveSchemasFiletype(str, Enum):
    CSV = 'csv'


class SourceMicrosoftOnedriveSchemasStreamsHeaderDefinitionType(str, Enum):
    USER_PROVIDED = 'User Provided'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceMicrosoftOnedriveUserProvided:
    column_names: List[str] = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('column_names') }})
    r"""The column names that will be used while emitting the CSV records"""
    HEADER_DEFINITION_TYPE: Final[Optional[SourceMicrosoftOnedriveSchemasStreamsHeaderDefinitionType]] = dataclasses.field(default=SourceMicrosoftOnedriveSchemasStreamsHeaderDefinitionType.USER_PROVIDED, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('header_definition_type'), 'exclude': lambda f: f is None }})
    



class SourceMicrosoftOnedriveSchemasHeaderDefinitionType(str, Enum):
    AUTOGENERATED = 'Autogenerated'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceMicrosoftOnedriveAutogenerated:
    HEADER_DEFINITION_TYPE: Final[Optional[SourceMicrosoftOnedriveSchemasHeaderDefinitionType]] = dataclasses.field(default=SourceMicrosoftOnedriveSchemasHeaderDefinitionType.AUTOGENERATED, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('header_definition_type'), 'exclude': lambda f: f is None }})
    



class SourceMicrosoftOnedriveHeaderDefinitionType(str, Enum):
    FROM_CSV = 'From CSV'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceMicrosoftOnedriveFromCSV:
    HEADER_DEFINITION_TYPE: Final[Optional[SourceMicrosoftOnedriveHeaderDefinitionType]] = dataclasses.field(default=SourceMicrosoftOnedriveHeaderDefinitionType.FROM_CSV, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('header_definition_type'), 'exclude': lambda f: f is None }})
    



@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceMicrosoftOnedriveCSVFormat:
    delimiter: Optional[str] = dataclasses.field(default=',', metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('delimiter'), 'exclude': lambda f: f is None }})
    r"""The character delimiting individual cells in the CSV data. This may only be a 1-character string. For tab-delimited data enter '\t'."""
    double_quote: Optional[bool] = dataclasses.field(default=True, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('double_quote'), 'exclude': lambda f: f is None }})
    r"""Whether two quotes in a quoted CSV value denote a single quote in the data."""
    encoding: Optional[str] = dataclasses.field(default='utf8', metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('encoding'), 'exclude': lambda f: f is None }})
    r"""The character encoding of the CSV data. Leave blank to default to <strong>UTF8</strong>. See <a href=\\"https://docs.python.org/3/library/codecs.html#standard-encodings\\" target=\\"_blank\\">list of python encodings</a> for allowable options."""
    escape_char: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('escape_char'), 'exclude': lambda f: f is None }})
    r"""The character used for escaping special characters. To disallow escaping, leave this field blank."""
    false_values: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('false_values'), 'exclude': lambda f: f is None }})
    r"""A set of case-sensitive strings that should be interpreted as false values."""
    FILETYPE: Final[Optional[SourceMicrosoftOnedriveSchemasFiletype]] = dataclasses.field(default=SourceMicrosoftOnedriveSchemasFiletype.CSV, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('filetype'), 'exclude': lambda f: f is None }})
    header_definition: Optional[SourceMicrosoftOnedriveCSVHeaderDefinition] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('header_definition'), 'exclude': lambda f: f is None }})
    r"""How headers will be defined. `User Provided` assumes the CSV does not have a header row and uses the headers provided and `Autogenerated` assumes the CSV does not have a header row and the CDK will generate headers using for `f{i}` where `i` is the index starting from 0. Else, the default behavior is to use the header from the CSV file. If a user wants to autogenerate or provide column names for a CSV having headers, they can skip rows."""
    ignore_errors_on_fields_mismatch: Optional[bool] = dataclasses.field(default=False, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('ignore_errors_on_fields_mismatch'), 'exclude': lambda f: f is None }})
    r"""Whether to ignore errors that occur when the number of fields in the CSV does not match the number of columns in the schema."""
    null_values: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('null_values'), 'exclude': lambda f: f is None }})
    r"""A set of case-sensitive strings that should be interpreted as null values. For example, if the value 'NA' should be interpreted as null, enter 'NA' in this field."""
    quote_char: Optional[str] = dataclasses.field(default='"', metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('quote_char'), 'exclude': lambda f: f is None }})
    r"""The character used for quoting CSV values. To disallow quoting, make this field blank."""
    skip_rows_after_header: Optional[int] = dataclasses.field(default=0, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('skip_rows_after_header'), 'exclude': lambda f: f is None }})
    r"""The number of rows to skip after the header row."""
    skip_rows_before_header: Optional[int] = dataclasses.field(default=0, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('skip_rows_before_header'), 'exclude': lambda f: f is None }})
    r"""The number of rows to skip before the header row. For example, if the header row is on the 3rd row, enter 2 in this field."""
    strings_can_be_null: Optional[bool] = dataclasses.field(default=True, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('strings_can_be_null'), 'exclude': lambda f: f is None }})
    r"""Whether strings can be interpreted as null values. If true, strings that match the null_values set will be interpreted as null. If false, strings that match the null_values set will be interpreted as the string itself."""
    true_values: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('true_values'), 'exclude': lambda f: f is None }})
    r"""A set of case-sensitive strings that should be interpreted as true values."""
    



class SourceMicrosoftOnedriveFiletype(str, Enum):
    AVRO = 'avro'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceMicrosoftOnedriveAvroFormat:
    double_as_string: Optional[bool] = dataclasses.field(default=False, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('double_as_string'), 'exclude': lambda f: f is None }})
    r"""Whether to convert double fields to strings. This is recommended if you have decimal numbers with a high degree of precision because there can be a loss precision when handling floating point numbers."""
    FILETYPE: Final[Optional[SourceMicrosoftOnedriveFiletype]] = dataclasses.field(default=SourceMicrosoftOnedriveFiletype.AVRO, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('filetype'), 'exclude': lambda f: f is None }})
    



class SourceMicrosoftOnedriveValidationPolicy(str, Enum):
    r"""The name of the validation policy that dictates sync behavior when a record does not adhere to the stream schema."""
    EMIT_RECORD = 'Emit Record'
    SKIP_RECORD = 'Skip Record'
    WAIT_FOR_DISCOVER = 'Wait for Discover'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceMicrosoftOnedriveFileBasedStreamConfig:
    format: SourceMicrosoftOnedriveFormat = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('format') }})
    r"""The configuration options that are used to alter how to read incoming files that deviate from the standard formatting."""
    name: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('name') }})
    r"""The name of the stream."""
    days_to_sync_if_history_is_full: Optional[int] = dataclasses.field(default=3, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('days_to_sync_if_history_is_full'), 'exclude': lambda f: f is None }})
    r"""When the state history of the file store is full, syncs will only read files that were last modified in the provided day range."""
    globs: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('globs'), 'exclude': lambda f: f is None }})
    r"""The pattern used to specify which files should be selected from the file system. For more information on glob pattern matching look <a href=\\"https://en.wikipedia.org/wiki/Glob_(programming)\\">here</a>."""
    input_schema: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('input_schema'), 'exclude': lambda f: f is None }})
    r"""The schema that will be used to validate records extracted from the file. This will override the stream schema that is auto-detected from incoming files."""
    primary_key: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('primary_key'), 'exclude': lambda f: f is None }})
    r"""The column or columns (for a composite key) that serves as the unique identifier of a record. If empty, the primary key will default to the parser's default primary key."""
    schemaless: Optional[bool] = dataclasses.field(default=False, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('schemaless'), 'exclude': lambda f: f is None }})
    r"""When enabled, syncs will not validate or structure records against the stream's schema."""
    validation_policy: Optional[SourceMicrosoftOnedriveValidationPolicy] = dataclasses.field(default=SourceMicrosoftOnedriveValidationPolicy.EMIT_RECORD, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('validation_policy'), 'exclude': lambda f: f is None }})
    r"""The name of the validation policy that dictates sync behavior when a record does not adhere to the stream schema."""
    



@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceMicrosoftOnedrive:
    r"""SourceMicrosoftOneDriveSpec class for Microsoft OneDrive Source Specification.
    This class combines the authentication details with additional configuration for the OneDrive API.
    """
    credentials: SourceMicrosoftOnedriveAuthentication = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('credentials') }})
    r"""Credentials for connecting to the One Drive API"""
    streams: List[SourceMicrosoftOnedriveFileBasedStreamConfig] = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('streams') }})
    r"""Each instance of this configuration defines a <a href=\\"https://docs.airbyte.com/cloud/core-concepts#stream\\">stream</a>. Use this to define which files belong in the stream, their format, and how they should be parsed and validated. When sending data to warehouse destination such as Snowflake or BigQuery, each stream is a separate table."""
    drive_name: Optional[str] = dataclasses.field(default='OneDrive', metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('drive_name'), 'exclude': lambda f: f is None }})
    r"""Name of the Microsoft OneDrive drive where the file(s) exist."""
    folder_path: Optional[str] = dataclasses.field(default='.', metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('folder_path'), 'exclude': lambda f: f is None }})
    r"""Path to a specific folder within the drives to search for files. Leave empty to search all folders of the drives. This does not apply to shared items."""
    search_scope: Optional[SearchScope] = dataclasses.field(default=SearchScope.ALL, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('search_scope'), 'exclude': lambda f: f is None }})
    r"""Specifies the location(s) to search for files. Valid options are 'ACCESSIBLE_DRIVES' to search in the selected OneDrive drive, 'SHARED_ITEMS' for shared items the user has access to, and 'ALL' to search both."""
    SOURCE_TYPE: Final[SourceMicrosoftOnedriveMicrosoftOnedrive] = dataclasses.field(default=SourceMicrosoftOnedriveMicrosoftOnedrive.MICROSOFT_ONEDRIVE, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('sourceType') }})
    start_date: Optional[datetime] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('start_date'), 'encoder': utils.datetimeisoformat(True), 'decoder': dateutil.parser.isoparse, 'exclude': lambda f: f is None }})
    r"""UTC date and time in the format 2017-01-25T00:00:00.000000Z. Any file modified before this date will not be replicated."""
    


SourceMicrosoftOnedriveAuthentication = Union[AuthenticateViaMicrosoftOAuth, ServiceKeyAuthentication]

SourceMicrosoftOnedriveProcessing = Union[SourceMicrosoftOnedriveLocal]

SourceMicrosoftOnedriveCSVHeaderDefinition = Union[SourceMicrosoftOnedriveFromCSV, SourceMicrosoftOnedriveAutogenerated, SourceMicrosoftOnedriveUserProvided]

SourceMicrosoftOnedriveFormat = Union[SourceMicrosoftOnedriveAvroFormat, SourceMicrosoftOnedriveCSVFormat, SourceMicrosoftOnedriveJsonlFormat, SourceMicrosoftOnedriveParquetFormat, UnstructuredDocumentFormat]
