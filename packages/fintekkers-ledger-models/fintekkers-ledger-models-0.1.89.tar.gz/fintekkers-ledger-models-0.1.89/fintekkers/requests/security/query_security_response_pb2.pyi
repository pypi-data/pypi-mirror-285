from fintekkers.models.security import security_pb2 as _security_pb2
from fintekkers.requests.security import query_security_request_pb2 as _query_security_request_pb2
from fintekkers.requests.util.errors import summary_pb2 as _summary_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QuerySecurityResponseProto(_message.Message):
    __slots__ = ["errors_or_warnings", "object_class", "query_security_input", "security_response", "version"]
    ERRORS_OR_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    QUERY_SECURITY_INPUT_FIELD_NUMBER: _ClassVar[int]
    SECURITY_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    errors_or_warnings: _containers.RepeatedCompositeFieldContainer[_summary_pb2.SummaryProto]
    object_class: str
    query_security_input: _query_security_request_pb2.QuerySecurityRequestProto
    security_response: _containers.RepeatedCompositeFieldContainer[_security_pb2.SecurityProto]
    version: str
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., query_security_input: _Optional[_Union[_query_security_request_pb2.QuerySecurityRequestProto, _Mapping]] = ..., security_response: _Optional[_Iterable[_Union[_security_pb2.SecurityProto, _Mapping]]] = ..., errors_or_warnings: _Optional[_Iterable[_Union[_summary_pb2.SummaryProto, _Mapping]]] = ...) -> None: ...
