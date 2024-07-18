from com.terraquantum.user.v1.user import user_pb2 as _user_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListUsersResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_user_pb2.UserProto]
    def __init__(self, users: _Optional[_Iterable[_Union[_user_pb2.UserProto, _Mapping]]] = ...) -> None: ...
