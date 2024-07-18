from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberProto(_message.Message):
    __slots__ = ("type", "id")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    type: str
    id: str
    def __init__(self, type: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

class MemberListProto(_message.Message):
    __slots__ = ("members",)
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    members: _containers.RepeatedCompositeFieldContainer[MemberProto]
    def __init__(self, members: _Optional[_Iterable[_Union[MemberProto, _Mapping]]] = ...) -> None: ...
