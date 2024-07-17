from fintekkers.models.transaction import transaction_pb2 as _transaction_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateTransactionRequestProto(_message.Message):
    __slots__ = ["create_transaction_input", "object_class", "version"]
    CREATE_TRANSACTION_INPUT_FIELD_NUMBER: _ClassVar[int]
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    create_transaction_input: _transaction_pb2.TransactionProto
    object_class: str
    version: str
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., create_transaction_input: _Optional[_Union[_transaction_pb2.TransactionProto, _Mapping]] = ...) -> None: ...
