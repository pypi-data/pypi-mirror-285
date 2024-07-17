from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

ANNUALLY: CouponFrequencyProto
DESCRIPTOR: _descriptor.FileDescriptor
MONTHLY: CouponFrequencyProto
NO_COUPON: CouponFrequencyProto
QUARTERLY: CouponFrequencyProto
SEMIANNUALLY: CouponFrequencyProto
UNKNOWN_COUPON_FREQUENCY: CouponFrequencyProto

class CouponFrequencyProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
