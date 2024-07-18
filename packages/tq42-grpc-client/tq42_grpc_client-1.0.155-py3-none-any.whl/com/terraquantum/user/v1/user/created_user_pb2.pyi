from com.terraquantum.role.v1.role import role_id_pb2 as _role_id_pb2
from com.terraquantum.user.v1.user import user_profile_pb2 as _user_profile_pb2
from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreatedUserProto(_message.Message):
    __slots__ = ("id", "profile", "email", "invitation_token", "organization_id", "role_ids", "project_ids")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    INVITATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_IDS_FIELD_NUMBER: _ClassVar[int]
    PROJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    profile: _user_profile_pb2.UserProfileProto
    email: str
    invitation_token: str
    organization_id: str
    role_ids: _containers.RepeatedCompositeFieldContainer[_role_id_pb2.RoleIdProto]
    project_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., profile: _Optional[_Union[_user_profile_pb2.UserProfileProto, _Mapping]] = ..., email: _Optional[str] = ..., invitation_token: _Optional[str] = ..., organization_id: _Optional[str] = ..., role_ids: _Optional[_Iterable[_Union[_role_id_pb2.RoleIdProto, _Mapping]]] = ..., project_ids: _Optional[_Iterable[str]] = ...) -> None: ...
