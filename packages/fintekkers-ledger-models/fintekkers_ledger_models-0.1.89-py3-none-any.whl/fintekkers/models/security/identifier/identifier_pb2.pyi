from fintekkers.models.security.identifier import identifier_type_pb2 as _identifier_type_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IdentifierProto(_message.Message):
    __slots__ = ["identifier_type", "identifier_value", "object_class", "version"]
    IDENTIFIER_TYPE_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_VALUE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    identifier_type: _identifier_type_pb2.IdentifierTypeProto
    identifier_value: str
    object_class: str
    version: str
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., identifier_value: _Optional[str] = ..., identifier_type: _Optional[_Union[_identifier_type_pb2.IdentifierTypeProto, str]] = ...) -> None: ...
