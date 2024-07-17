from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

CASH: IdentifierTypeProto
CUSIP: IdentifierTypeProto
DESCRIPTOR: _descriptor.FileDescriptor
EXCH_TICKER: IdentifierTypeProto
FIGI: IdentifierTypeProto
ISIN: IdentifierTypeProto
OSI: IdentifierTypeProto
UNKNOWN_IDENTIFIER_TYPE: IdentifierTypeProto

class IdentifierTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
