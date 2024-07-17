from fintekkers.models.portfolio import portfolio_pb2 as _portfolio_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreatePortfolioRequestProto(_message.Message):
    __slots__ = ["create_portfolio_input", "object_class", "version"]
    CREATE_PORTFOLIO_INPUT_FIELD_NUMBER: _ClassVar[int]
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    create_portfolio_input: _portfolio_pb2.PortfolioProto
    object_class: str
    version: str
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., create_portfolio_input: _Optional[_Union[_portfolio_pb2.PortfolioProto, _Mapping]] = ...) -> None: ...
