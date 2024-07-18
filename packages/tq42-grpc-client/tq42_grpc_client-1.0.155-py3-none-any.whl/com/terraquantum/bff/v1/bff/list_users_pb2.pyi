from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from com.terraquantum.common.v1.organization import organization_user_status_pb2 as _organization_user_status_pb2
from com.terraquantum.user.v1.waiting_user import waiting_user_pb2 as _waiting_user_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListEditableOrganizationMembersRequest(_message.Message):
    __slots__ = ("organization_id",)
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    def __init__(self, organization_id: _Optional[str] = ...) -> None: ...

class ListBffUsersResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[BffUserProto]
    def __init__(self, users: _Optional[_Iterable[_Union[BffUserProto, _Mapping]]] = ...) -> None: ...

class BffUserProto(_message.Message):
    __slots__ = ("id", "email", "status", "organization_id", "first_name", "middle_name", "last_name", "company", "role", "primary_area_of_interest", "picture", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_AREA_OF_INTEREST_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    email: str
    status: _organization_user_status_pb2.OrganizationUserStatusProto
    organization_id: str
    first_name: str
    middle_name: str
    last_name: str
    company: str
    role: _waiting_user_pb2.UserRoleProto
    primary_area_of_interest: _waiting_user_pb2.AreaOfInterestProto
    picture: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., email: _Optional[str] = ..., status: _Optional[_Union[_organization_user_status_pb2.OrganizationUserStatusProto, str]] = ..., organization_id: _Optional[str] = ..., first_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., last_name: _Optional[str] = ..., company: _Optional[str] = ..., role: _Optional[_Union[_waiting_user_pb2.UserRoleProto, str]] = ..., primary_area_of_interest: _Optional[_Union[_waiting_user_pb2.AreaOfInterestProto, str]] = ..., picture: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
