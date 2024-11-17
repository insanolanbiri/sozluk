import dataclasses
import logging
import re
from datetime import datetime, timedelta
from typing import Type, TypeVar

from markupsafe import escape

from sozluk.authorname import AuthorName
from sozluk.topicname import TopicName
from sozluk.turkishlowercasedstring import TurkishLowercasedString

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="EntrySketch")

ENTRY_REFERENCE_PARSER = {
    "(bkz: {})": re.compile(r"\(bkz: ((?:[#@]?[a-z \d])+)?\)"),
    "(ayrica bkz: {})": re.compile(r"\(ayrica bkz: ((?:[#@]?[a-z \d])+)?\)"),
    "(ayrıca bkz: {})": re.compile(r"\(ayrıca bkz: ((?:[#@]?[a-z \d])+)?\)"),
    "{}": re.compile(r"`([#@]?[a-z \d]+)?`"),
}


class EntryText(TurkishLowercasedString):

    def parse(self):
        # escape for python format syntax
        string = self.replace("{", "{{").replace("}", "}}")

        indexes = {}

        for replacement, parser in ENTRY_REFERENCE_PARSER.items():
            for m in parser.finditer(string):
                indexes[m.span()[0]] = m.group(1)

        matches = [v for k, v in sorted(indexes.items(), key=lambda item: item[0])]

        for replacement, parser in ENTRY_REFERENCE_PARSER.items():
            string = parser.sub(replacement, string)

        return string, matches

    def render(self, topic_prefix="", entry_prefix="", author_prefix=""):
        try:
            string, matches = self.parse()
        except Exception as e:
            logger.exception(e)
            return self

        string = str(escape(string))

        formatted = []
        for i in matches:
            if i.startswith("@"):
                formatted.append(
                    f"<a href='{author_prefix}{i.removeprefix('@')}'>{i}</a>"
                )
            elif i.startswith("#"):
                formatted.append(
                    f"<a href='{entry_prefix}{i.removeprefix('#')}'>{i}</a>"
                )
            else:
                formatted.append(f"<a href='{topic_prefix}{i}'>{i}</a>")

        try:
            return string.format(*formatted)
        except Exception as e:
            logger.exception(e)
            return self


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
