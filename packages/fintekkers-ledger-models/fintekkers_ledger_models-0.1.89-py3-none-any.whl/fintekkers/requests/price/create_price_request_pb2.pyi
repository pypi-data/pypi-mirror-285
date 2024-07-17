from fintekkers.models.price import price_pb2 as _price_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreatePriceRequestProto(_message.Message):
    __slots__ = ["create_price_input", "object_class", "version"]
    CREATE_PRICE_INPUT_FIELD_NUMBER: _ClassVar[int]
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    create_price_input: _price_pb2.PriceProto
    object_class: str
    version: str
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., create_price_input: _Optional[_Union[_price_pb2.PriceProto, _Mapping]] = ...) -> None: ...
