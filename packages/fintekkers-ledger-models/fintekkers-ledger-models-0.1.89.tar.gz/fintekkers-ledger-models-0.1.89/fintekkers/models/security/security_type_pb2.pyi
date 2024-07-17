from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

BOND_SECURITY: SecurityTypeProto
CASH_SECURITY: SecurityTypeProto
DESCRIPTOR: _descriptor.FileDescriptor
EQUITY_SECURITY: SecurityTypeProto
FRN: SecurityTypeProto
TIPS: SecurityTypeProto
UNKNOWN_SECURITY_TYPE: SecurityTypeProto

class SecurityTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
