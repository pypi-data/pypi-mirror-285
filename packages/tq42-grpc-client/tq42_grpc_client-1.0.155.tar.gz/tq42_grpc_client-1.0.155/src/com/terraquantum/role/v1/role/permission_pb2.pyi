from com.terraquantum.role.v1.role import permission_id_pb2 as _permission_id_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PermissionProto(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: _permission_id_pb2.PermissionIdProto
    def __init__(self, id: _Optional[_Union[_permission_id_pb2.PermissionIdProto, _Mapping]] = ...) -> None: ...
