from com.terraquantum.invitation.v1.invitation import invitation_pb2 as _invitation_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListInvitationsResponse(_message.Message):
    __slots__ = ("invitations",)
    INVITATIONS_FIELD_NUMBER: _ClassVar[int]
    invitations: _containers.RepeatedCompositeFieldContainer[_invitation_pb2.InvitationProto]
    def __init__(self, invitations: _Optional[_Iterable[_Union[_invitation_pb2.InvitationProto, _Mapping]]] = ...) -> None: ...
