from com.terraquantum.role.v1.role import role_id_pb2 as _role_id_pb2
from google.protobuf import field_mask_pb2 as _field_mask_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpdateGroupRequest(_message.Message):
    __slots__ = ("group", "update_mask", "request_id")
    GROUP_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MASK_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    group: UpdateGroupProto
    update_mask: _field_mask_pb2.FieldMask
    request_id: str
    def __init__(self, group: _Optional[_Union[UpdateGroupProto, _Mapping]] = ..., update_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ..., request_id: _Optional[str] = ...) -> None: ...

class UpdateGroupProto(_message.Message):
    __slots__ = ("id", "name", "description", "member_ids", "role_ids", "project_ids")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_IDS_FIELD_NUMBER: _ClassVar[int]
    ROLE_IDS_FIELD_NUMBER: _ClassVar[int]
    PROJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    member_ids: _containers.RepeatedScalarFieldContainer[str]
    role_ids: _containers.RepeatedCompositeFieldContainer[_role_id_pb2.RoleIdProto]
    project_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., member_ids: _Optional[_Iterable[str]] = ..., role_ids: _Optional[_Iterable[_Union[_role_id_pb2.RoleIdProto, _Mapping]]] = ..., project_ids: _Optional[_Iterable[str]] = ...) -> None: ...
