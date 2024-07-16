"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from airbyte_api import utils
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from typing import Any, Dict, Final, Optional, Union


class SourceMongodbV2SchemasClusterType(str, Enum):
    SELF_MANAGED_REPLICA_SET = 'SELF_MANAGED_REPLICA_SET'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SelfManagedReplicaSet:
    r"""MongoDB self-hosted cluster configured as a replica set"""
    connection_string: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('connection_string') }})
    r"""The connection string of the cluster that you want to replicate.  https://www.mongodb.com/docs/manual/reference/connection-string/#find-your-self-hosted-deployment-s-connection-string for more information."""
    database: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('database') }})
    r"""The name of the MongoDB database that contains the collection(s) to replicate."""
    additional_properties: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'exclude': lambda f: f is None }})
    auth_source: Optional[str] = dataclasses.field(default='admin', metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('auth_source'), 'exclude': lambda f: f is None }})
    r"""The authentication source where the user information is stored."""
    CLUSTER_TYPE: Final[SourceMongodbV2SchemasClusterType] = dataclasses.field(default=SourceMongodbV2SchemasClusterType.SELF_MANAGED_REPLICA_SET, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('cluster_type') }})
    password: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('password'), 'exclude': lambda f: f is None }})
    r"""The password associated with this username."""
    schema_enforced: Optional[bool] = dataclasses.field(default=True, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('schema_enforced'), 'exclude': lambda f: f is None }})
    r"""When enabled, syncs will validate and structure records against the stream's schema."""
    username: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('username'), 'exclude': lambda f: f is None }})
    r"""The username which is used to access the database."""
    



class SourceMongodbV2ClusterType(str, Enum):
    ATLAS_REPLICA_SET = 'ATLAS_REPLICA_SET'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class MongoDBAtlasReplicaSet:
    r"""MongoDB Atlas-hosted cluster configured as a replica set"""
    connection_string: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('connection_string') }})
    r"""The connection string of the cluster that you want to replicate."""
    database: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('database') }})
    r"""The name of the MongoDB database that contains the collection(s) to replicate."""
    password: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('password') }})
    r"""The password associated with this username."""
    username: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('username') }})
    r"""The username which is used to access the database."""
    additional_properties: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'exclude': lambda f: f is None }})
    auth_source: Optional[str] = dataclasses.field(default='admin', metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('auth_source'), 'exclude': lambda f: f is None }})
    r"""The authentication source where the user information is stored.  See https://www.mongodb.com/docs/manual/reference/connection-string/#mongodb-urioption-urioption.authSource for more details."""
    CLUSTER_TYPE: Final[SourceMongodbV2ClusterType] = dataclasses.field(default=SourceMongodbV2ClusterType.ATLAS_REPLICA_SET, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('cluster_type') }})
    schema_enforced: Optional[bool] = dataclasses.field(default=True, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('schema_enforced'), 'exclude': lambda f: f is None }})
    r"""When enabled, syncs will validate and structure records against the stream's schema."""
    



class InvalidCDCPositionBehaviorAdvanced(str, Enum):
    r"""Determines whether Airbyte should fail or re-sync data in case of an stale/invalid cursor value into the WAL. If 'Fail sync' is chosen, a user will have to manually reset the connection before being able to continue syncing data. If 'Re-sync data' is chosen, Airbyte will automatically trigger a refresh but could lead to higher cloud costs and data loss."""
    FAIL_SYNC = 'Fail sync'
    RE_SYNC_DATA = 'Re-sync data'


class MongodbV2(str, Enum):
    MONGODB_V2 = 'mongodb-v2'


class CaptureModeAdvanced(str, Enum):
    r"""Determines how Airbyte looks up the value of an updated document. If 'Lookup' is chosen, the current value of the document will be read. If 'Post Image' is chosen, then the version of the document immediately after an update will be read. WARNING : Severe data loss will occur if this option is chosen and the appropriate settings are not set on your Mongo instance : https://www.mongodb.com/docs/manual/changeStreams/#change-streams-with-document-pre-and-post-images."""
    LOOKUP = 'Lookup'
    POST_IMAGE = 'Post Image'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SourceMongodbV2:
    database_config: ClusterType = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('database_config') }})
    r"""Configures the MongoDB cluster type."""
    discover_sample_size: Optional[int] = dataclasses.field(default=10000, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('discover_sample_size'), 'exclude': lambda f: f is None }})
    r"""The maximum number of documents to sample when attempting to discover the unique fields for a collection."""
    initial_waiting_seconds: Optional[int] = dataclasses.field(default=300, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('initial_waiting_seconds'), 'exclude': lambda f: f is None }})
    r"""The amount of time the connector will wait when it launches to determine if there is new data to sync or not. Defaults to 300 seconds. Valid range: 120 seconds to 1200 seconds."""
    invalid_cdc_cursor_position_behavior: Optional[InvalidCDCPositionBehaviorAdvanced] = dataclasses.field(default=InvalidCDCPositionBehaviorAdvanced.FAIL_SYNC, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('invalid_cdc_cursor_position_behavior'), 'exclude': lambda f: f is None }})
    r"""Determines whether Airbyte should fail or re-sync data in case of an stale/invalid cursor value into the WAL. If 'Fail sync' is chosen, a user will have to manually reset the connection before being able to continue syncing data. If 'Re-sync data' is chosen, Airbyte will automatically trigger a refresh but could lead to higher cloud costs and data loss."""
    queue_size: Optional[int] = dataclasses.field(default=10000, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('queue_size'), 'exclude': lambda f: f is None }})
    r"""The size of the internal queue. This may interfere with memory consumption and efficiency of the connector, please be careful."""
    SOURCE_TYPE: Final[MongodbV2] = dataclasses.field(default=MongodbV2.MONGODB_V2, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('sourceType') }})
    update_capture_mode: Optional[CaptureModeAdvanced] = dataclasses.field(default=CaptureModeAdvanced.LOOKUP, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('update_capture_mode'), 'exclude': lambda f: f is None }})
    r"""Determines how Airbyte looks up the value of an updated document. If 'Lookup' is chosen, the current value of the document will be read. If 'Post Image' is chosen, then the version of the document immediately after an update will be read. WARNING : Severe data loss will occur if this option is chosen and the appropriate settings are not set on your Mongo instance : https://www.mongodb.com/docs/manual/changeStreams/#change-streams-with-document-pre-and-post-images."""
    


ClusterType = Union[MongoDBAtlasReplicaSet, SelfManagedReplicaSet]
