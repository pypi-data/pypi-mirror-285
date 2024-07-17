from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

BUY: TransactionTypeProto
DEPOSIT: TransactionTypeProto
DESCRIPTOR: _descriptor.FileDescriptor
MATURATION: TransactionTypeProto
MATURATION_OFFSET: TransactionTypeProto
SELL: TransactionTypeProto
UNKNOWN: TransactionTypeProto
WITHDRAWAL: TransactionTypeProto

class TransactionTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
