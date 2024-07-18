from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ListProjectPoliciesRequest(_message.Message):
    __slots__ = ("member_type", "member_id")
    MEMBER_TYPE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    member_type: str
    member_id: str
    def __init__(self, member_type: _Optional[str] = ..., member_id: _Optional[str] = ...) -> None: ...
