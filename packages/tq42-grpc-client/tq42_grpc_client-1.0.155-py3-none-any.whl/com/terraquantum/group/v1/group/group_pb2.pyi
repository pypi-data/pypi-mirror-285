from com.terraquantum.role.v1.role import role_id_pb2 as _role_id_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GroupProto(_message.Message):
    __slots__ = ("id", "organization_id", "name", "description", "created_at", "member_ids", "role_ids", "project_ids")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    MEMBER_IDS_FIELD_NUMBER: _ClassVar[int]
    ROLE_IDS_FIELD_NUMBER: _ClassVar[int]
    PROJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_id: str
    name: str
    description: str
    created_at: _timestamp_pb2.Timestamp
    member_ids: _containers.RepeatedScalarFieldContainer[str]
    role_ids: _containers.RepeatedCompositeFieldContainer[_role_id_pb2.RoleIdProto]
    project_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., organization_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., member_ids: _Optional[_Iterable[str]] = ..., role_ids: _Optional[_Iterable[_Union[_role_id_pb2.RoleIdProto, _Mapping]]] = ..., project_ids: _Optional[_Iterable[str]] = ...) -> None: ...
