from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor
PERPETUAL: TenorTypeProto
TERM: TenorTypeProto
UNKNOWN_TENOR_TYPE: TenorTypeProto

class TenorTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
