from com.terraquantum.role.v1.role import role_id_pb2 as _role_id_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InvitationStatusProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVITATION_STATUS_UNSPECIFIED: _ClassVar[InvitationStatusProto]
    ACTIVE: _ClassVar[InvitationStatusProto]
    ACCEPTED: _ClassVar[InvitationStatusProto]
INVITATION_STATUS_UNSPECIFIED: InvitationStatusProto
ACTIVE: InvitationStatusProto
ACCEPTED: InvitationStatusProto

class InvitationProto(_message.Message):
    __slots__ = ("id", "status", "email", "created_at", "first_name", "last_name", "organization_id", "role_ids", "project_ids", "is_existing_user")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_IDS_FIELD_NUMBER: _ClassVar[int]
    PROJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    IS_EXISTING_USER_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: InvitationStatusProto
    email: str
    created_at: _timestamp_pb2.Timestamp
    first_name: str
    last_name: str
    organization_id: str
    role_ids: _containers.RepeatedCompositeFieldContainer[_role_id_pb2.RoleIdProto]
    project_ids: _containers.RepeatedScalarFieldContainer[str]
    is_existing_user: bool
    def __init__(self, id: _Optional[str] = ..., status: _Optional[_Union[InvitationStatusProto, str]] = ..., email: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., organization_id: _Optional[str] = ..., role_ids: _Optional[_Iterable[_Union[_role_id_pb2.RoleIdProto, _Mapping]]] = ..., project_ids: _Optional[_Iterable[str]] = ..., is_existing_user: bool = ...) -> None: ...
