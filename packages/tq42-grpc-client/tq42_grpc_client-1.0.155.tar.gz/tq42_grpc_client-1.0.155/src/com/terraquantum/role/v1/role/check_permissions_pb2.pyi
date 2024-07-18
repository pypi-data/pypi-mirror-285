from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CheckPermissionsRequest(_message.Message):
    __slots__ = ("checks",)
    CHECKS_FIELD_NUMBER: _ClassVar[int]
    checks: _containers.RepeatedCompositeFieldContainer[CheckPermissionProto]
    def __init__(self, checks: _Optional[_Iterable[_Union[CheckPermissionProto, _Mapping]]] = ...) -> None: ...

class CheckPermissionProto(_message.Message):
    __slots__ = ("relation", "object_type", "object_id")
    RELATION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    relation: str
    object_type: str
    object_id: str
    def __init__(self, relation: _Optional[str] = ..., object_type: _Optional[str] = ..., object_id: _Optional[str] = ...) -> None: ...

class CheckPermissionResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _containers.RepeatedScalarFieldContainer[bool]
    def __init__(self, result: _Optional[_Iterable[bool]] = ...) -> None: ...
