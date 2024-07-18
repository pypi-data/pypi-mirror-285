from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ListProjectsByRelationRequest(_message.Message):
    __slots__ = ("organization_id", "relation")
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    relation: str
    def __init__(self, organization_id: _Optional[str] = ..., relation: _Optional[str] = ...) -> None: ...

class ListProjectsForUserRequest(_message.Message):
    __slots__ = ("organization_id", "user_id")
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    user_id: str
    def __init__(self, organization_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class ListProjectsForGroupRequest(_message.Message):
    __slots__ = ("organization_id", "group_id")
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    group_id: str
    def __init__(self, organization_id: _Optional[str] = ..., group_id: _Optional[str] = ...) -> None: ...
