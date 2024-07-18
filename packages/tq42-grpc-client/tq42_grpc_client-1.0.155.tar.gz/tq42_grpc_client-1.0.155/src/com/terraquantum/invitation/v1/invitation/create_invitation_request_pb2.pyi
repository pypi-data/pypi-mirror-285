from com.terraquantum.role.v1.role import role_id_pb2 as _role_id_pb2
from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateInvitationRequest(_message.Message):
    __slots__ = ("email", "request_id", "first_name", "last_name", "role_ids", "project_ids", "organization_id")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_IDS_FIELD_NUMBER: _ClassVar[int]
    PROJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    email: str
    request_id: str
    first_name: str
    last_name: str
    role_ids: _containers.RepeatedCompositeFieldContainer[_role_id_pb2.RoleIdProto]
    project_ids: _containers.RepeatedScalarFieldContainer[str]
    organization_id: str
    def __init__(self, email: _Optional[str] = ..., request_id: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., role_ids: _Optional[_Iterable[_Union[_role_id_pb2.RoleIdProto, _Mapping]]] = ..., project_ids: _Optional[_Iterable[str]] = ..., organization_id: _Optional[str] = ...) -> None: ...
