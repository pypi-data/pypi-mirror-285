from com.terraquantum.role.v1.role import role_pb2 as _role_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListRolesResponse(_message.Message):
    __slots__ = ("roles",)
    ROLES_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedCompositeFieldContainer[_role_pb2.RoleProto]
    def __init__(self, roles: _Optional[_Iterable[_Union[_role_pb2.RoleProto, _Mapping]]] = ...) -> None: ...
