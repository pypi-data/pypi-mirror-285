from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ListProjectPoliciesResponse(_message.Message):
    __slots__ = ("project_ids",)
    PROJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    project_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, project_ids: _Optional[_Iterable[str]] = ...) -> None: ...
