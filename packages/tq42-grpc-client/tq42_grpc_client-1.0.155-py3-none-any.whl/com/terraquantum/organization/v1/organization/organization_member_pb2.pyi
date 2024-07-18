from com.terraquantum.organization.v1.organization import organization_member_permission_pb2 as _organization_member_permission_pb2
from com.terraquantum.common.v1.organization import organization_member_status_pb2 as _organization_member_status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrganizationMemberProto(_message.Message):
    __slots__ = ("id", "organization_id", "user_id", "status", "permission", "organization_owner", "email", "first_name", "last_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_OWNER_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_id: str
    user_id: str
    status: _organization_member_status_pb2.OrganizationMemberStatusProto
    permission: _organization_member_permission_pb2.OrganizationMemberPermissionProto
    organization_owner: bool
    email: str
    first_name: str
    last_name: str
    def __init__(self, id: _Optional[str] = ..., organization_id: _Optional[str] = ..., user_id: _Optional[str] = ..., status: _Optional[_Union[_organization_member_status_pb2.OrganizationMemberStatusProto, str]] = ..., permission: _Optional[_Union[_organization_member_permission_pb2.OrganizationMemberPermissionProto, _Mapping]] = ..., organization_owner: bool = ..., email: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ...) -> None: ...
