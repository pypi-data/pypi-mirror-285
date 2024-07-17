from fintekkers.models.position import position_util_pb2 as _position_util_pb2
from fintekkers.requests.valuation import valuation_request_pb2 as _valuation_request_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ValuationResponseProto(_message.Message):
    __slots__ = ["measure_results", "object_class", "valuation_request", "version"]
    MEASURE_RESULTS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VALUATION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    measure_results: _containers.RepeatedCompositeFieldContainer[_position_util_pb2.MeasureMapEntry]
    object_class: str
    valuation_request: _valuation_request_pb2.ValuationRequestProto
    version: str
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., valuation_request: _Optional[_Union[_valuation_request_pb2.ValuationRequestProto, _Mapping]] = ..., measure_results: _Optional[_Iterable[_Union[_position_util_pb2.MeasureMapEntry, _Mapping]]] = ...) -> None: ...
