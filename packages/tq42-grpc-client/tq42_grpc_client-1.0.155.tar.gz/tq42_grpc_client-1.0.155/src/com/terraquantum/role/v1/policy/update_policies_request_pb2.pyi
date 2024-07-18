from com.terraquantum.role.v1.role import role_id_pb2 as _role_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpdatePoliciesRequest(_message.Message):
    __slots__ = ("member_type", "member_id", "update_user_policies", "organization_id")
    MEMBER_TYPE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    UPDATE_USER_POLICIES_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    member_type: str
    member_id: str
    update_user_policies: _containers.RepeatedCompositeFieldContainer[UpdateUserPolicyProto]
    organization_id: str
    def __init__(self, member_type: _Optional[str] = ..., member_id: _Optional[str] = ..., update_user_policies: _Optional[_Iterable[_Union[UpdateUserPolicyProto, _Mapping]]] = ..., organization_id: _Optional[str] = ...) -> None: ...

class UpdateUserPolicyProto(_message.Message):
    __slots__ = ("role_id", "object_id")
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    role_id: _role_id_pb2.RoleIdProto
    object_id: str
    def __init__(self, role_id: _Optional[_Union[_role_id_pb2.RoleIdProto, _Mapping]] = ..., object_id: _Optional[str] = ...) -> None: ...
