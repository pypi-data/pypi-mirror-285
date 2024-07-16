from typing import Annotated, TypeVar

T = TypeVar("T")


class EmptySeq(tuple[T, ...]):
    __slots__ = ()

    def __new__(cls):
        return super().__new__(cls)


EmptyObject = EmptySeq[object]
EMPTY_SEQ = EmptySeq[
    object
]()  # object instead of Any cause Any is simply "ignored" by pyright!
PositiveTimeStamp = Annotated[float, lambda x: x > 0]
