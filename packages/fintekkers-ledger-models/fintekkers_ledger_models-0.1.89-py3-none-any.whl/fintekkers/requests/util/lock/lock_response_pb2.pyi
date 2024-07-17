from fintekkers.models.util.lock import node_state_pb2 as _node_state_pb2
from fintekkers.requests.util.lock import lock_request_pb2 as _lock_request_pb2
from fintekkers.requests.util.errors import summary_pb2 as _summary_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LockResponseProto(_message.Message):
    __slots__ = ["errors_or_warnings", "get_lock_request", "lock_response", "object_class", "version"]
    ERRORS_OR_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    GET_LOCK_REQUEST_FIELD_NUMBER: _ClassVar[int]
    LOCK_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    errors_or_warnings: _summary_pb2.SummaryProto
    get_lock_request: _lock_request_pb2.LockRequestProto
    lock_response: _node_state_pb2.NodeState
    object_class: str
    version: str
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., get_lock_request: _Optional[_Union[_lock_request_pb2.LockRequestProto, _Mapping]] = ..., lock_response: _Optional[_Union[_node_state_pb2.NodeState, _Mapping]] = ..., errors_or_warnings: _Optional[_Union[_summary_pb2.SummaryProto, _Mapping]] = ...) -> None: ...
