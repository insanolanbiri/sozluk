import dataclasses
from datetime import datetime, timedelta
from typing import Type, TypeVar

from sozluk.authorname import AuthorName
from sozluk.topicname import TopicName
from sozluk.turkishlowercasedstring import TurkishLowercasedString

T = TypeVar("T", bound="EntrySketch")


class EntryText(TurkishLowercasedString):
    pass


@dataclasses.dataclass
class EntryID:
    value: int

    def __init__(self, identifier_number: int):
        if not identifier_number > 0:
            raise ValueError(
                f"Entry identifier should be greater than zero but {identifier_number} is given"
            )

        self.value = identifier_number

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, EntryID):
            return False
        return o.value == self.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __int__(self):
        return self.value


@dataclasses.dataclass(kw_only=True)
class EntrySketch:
    topic: TopicName
    author: AuthorName
    text: EntryText


@dataclasses.dataclass(kw_only=True)
class Entry(EntrySketch):
    identifier: EntryID
    utc_time: datetime

    @classmethod
    def from_sketch(
        cls: Type[T], sketch: EntrySketch, identifier: EntryID, utc_time: datetime
    ) -> T:
        instance = cls(
            topic=sketch.topic,
            author=sketch.author,
            text=sketch.text,
            identifier=identifier,
            utc_time=utc_time,
        )

        return instance

    def time(self, delta: timedelta):
        return self.utc_time + delta
