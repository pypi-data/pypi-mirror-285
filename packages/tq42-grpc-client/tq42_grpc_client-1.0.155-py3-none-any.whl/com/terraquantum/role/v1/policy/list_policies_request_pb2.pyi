from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ListPoliciesRequest(_message.Message):
    __slots__ = ("member_type", "member_id", "relation", "object_type", "object_id", "user_set")
    MEMBER_TYPE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_SET_FIELD_NUMBER: _ClassVar[int]
    member_type: str
    member_id: str
    relation: str
    object_type: str
    object_id: str
    user_set: str
    def __init__(self, member_type: _Optional[str] = ..., member_id: _Optional[str] = ..., relation: _Optional[str] = ..., object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., user_set: _Optional[str] = ...) -> None: ...

class ListPoliciesRecursiveRequest(_message.Message):
    __slots__ = ("member_type", "member_id", "relation", "object_type")
    MEMBER_TYPE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    member_type: str
    member_id: str
    relation: str
    object_type: str
    def __init__(self, member_type: _Optional[str] = ..., member_id: _Optional[str] = ..., relation: _Optional[str] = ..., object_type: _Optional[str] = ...) -> None: ...
