from com.terraquantum.invitation.v1.invitation import invitation_pb2 as _invitation_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListInvitationsRequest(_message.Message):
    __slots__ = ("organization_id", "status")
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    status: _invitation_pb2.InvitationStatusProto
    def __init__(self, organization_id: _Optional[str] = ..., status: _Optional[_Union[_invitation_pb2.InvitationStatusProto, str]] = ...) -> None: ...
