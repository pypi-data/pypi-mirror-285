from com.terraquantum.role.v1.role import permission_pb2 as _permission_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListPermissionsResponse(_message.Message):
    __slots__ = ("permissions",)
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    permissions: _containers.RepeatedCompositeFieldContainer[_permission_pb2.PermissionProto]
    def __init__(self, permissions: _Optional[_Iterable[_Union[_permission_pb2.PermissionProto, _Mapping]]] = ...) -> None: ...
