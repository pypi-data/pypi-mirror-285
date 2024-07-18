from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ResendInvitationRequest(_message.Message):
    __slots__ = ("invitation_id", "organization_id", "request_id")
    INVITATION_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    invitation_id: str
    organization_id: str
    request_id: str
    def __init__(self, invitation_id: _Optional[str] = ..., organization_id: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...
