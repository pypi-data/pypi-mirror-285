from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Config(_message.Message):
    __slots__ = ("serializedConfig",)
    SERIALIZEDCONFIG_FIELD_NUMBER: _ClassVar[int]
    serializedConfig: str
    def __init__(self, serializedConfig: _Optional[str] = ...) -> None: ...

class Confirmation(_message.Message):
    __slots__ = ("info",)
    INFO_FIELD_NUMBER: _ClassVar[int]
    info: str
    def __init__(self, info: _Optional[str] = ...) -> None: ...

class Matrix(_message.Message):
    __slots__ = ("dimensions", "values")
    DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    dimensions: _containers.RepeatedScalarFieldContainer[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, dimensions: _Optional[_Iterable[int]] = ..., values: _Optional[_Iterable[float]] = ...) -> None: ...

class Percept(_message.Message):
    __slots__ = ("state", "reward", "terminal")
    STATE_FIELD_NUMBER: _ClassVar[int]
    REWARD_FIELD_NUMBER: _ClassVar[int]
    TERMINAL_FIELD_NUMBER: _ClassVar[int]
    state: Matrix
    reward: float
    terminal: bool
    def __init__(self, state: _Optional[_Union[Matrix, _Mapping]] = ..., reward: _Optional[float] = ..., terminal: bool = ...) -> None: ...
