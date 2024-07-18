import abc
import datetime
import random
import string
import typing

T = typing.TypeVar("T")


class AbstractValueGenerator(typing.Generic[T], abc.ABC):
    @abc.abstractmethod
    def next(self) -> T:
        pass


class ValueGenerator(AbstractValueGenerator[T]):
    def __init__(self, value: T):
        self.__value = value

    def next(self) -> T:
        return self.__value


class StringGenerator(AbstractValueGenerator[str]):
    def next(self) -> str:
        letters = string.ascii_letters
        return "".join(random.choice(letters) for _ in range(20))


class IntegerGenerator(AbstractValueGenerator[int]):
    def next(self) -> int:
        return 1


class FloatGenerator(AbstractValueGenerator[float]):
    def next(self) -> float:
        return 1.0


class DatetimeGenerator(AbstractValueGenerator[datetime.datetime]):
    def next(self) -> datetime.datetime:
        return datetime.datetime.now(tz=datetime.timezone.utc)


class BooleanGenerator(AbstractValueGenerator[bool]):
    def next(self) -> bool:
        return True


class NoneGenerator(AbstractValueGenerator[None]):
    def next(self) -> None:
        return None


class DictGenerator(AbstractValueGenerator[None]):
    def next(self) -> dict:
        return {}


class EnumGenerator(typing.Generic[T], AbstractValueGenerator[T]):
    def __init__(self, enum_class: typing.Type[T]):
        self.__enum_class = enum_class

    def next(self) -> T:
        return random.choice(list(self.__enum_class))
