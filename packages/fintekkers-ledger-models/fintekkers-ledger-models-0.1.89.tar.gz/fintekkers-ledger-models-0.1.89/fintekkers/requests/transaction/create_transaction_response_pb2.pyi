from fintekkers.models.transaction import transaction_pb2 as _transaction_pb2
from fintekkers.requests.transaction import create_transaction_request_pb2 as _create_transaction_request_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateTransactionResponseProto(_message.Message):
    __slots__ = ["create_transaction_request", "object_class", "transaction_response", "version"]
    CREATE_TRANSACTION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    create_transaction_request: _create_transaction_request_pb2.CreateTransactionRequestProto
    object_class: str
    transaction_response: _transaction_pb2.TransactionProto
    version: str
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., create_transaction_request: _Optional[_Union[_create_transaction_request_pb2.CreateTransactionRequestProto, _Mapping]] = ..., transaction_response: _Optional[_Union[_transaction_pb2.TransactionProto, _Mapping]] = ...) -> None: ...
