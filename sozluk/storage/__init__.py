from abc import ABC, abstractmethod
from enum import Enum, auto

from sozluk.authorname import AuthorName
from sozluk.entry import Entry, EntryID, EntrySketch, EntryText
from sozluk.topicname import TopicName


class EntryDeleteResponse(Enum):
    SUCCESS = auto()
    ENTRY_NOT_FOUND = auto()


class EntryAddResponse(Enum):
    SUCCESS = auto()
    DEFINITION_EXISTS = auto()


class SozlukStorage(ABC):
    @abstractmethod
    async def add_entry(
        self, sketch: EntrySketch
    ) -> tuple[EntryAddResponse, EntryID | None]:
        pass

    @abstractmethod
    async def get_entry(self, entry_id: EntryID) -> Entry | None:
        pass

    @abstractmethod
    async def get_topic(self, topic_name: TopicName) -> list[Entry]:
        pass

    @abstractmethod
    async def get_author(self, author_name: AuthorName) -> list[Entry]:
        pass

    @abstractmethod
    async def topic_search_basic(
        self, query: str, limit: int | None = None
    ) -> list[TopicName]:
        """Get a list of topics that contains a substring"""

    @abstractmethod
    async def del_entry(self, entry_id: EntryID) -> EntryDeleteResponse:
        pass

    @abstractmethod
    async def get_latest_authors(
        self, limit: int | None = None, offset: int | None = None
    ) -> list[AuthorName]:
        pass

    @abstractmethod
    async def get_latest_topics(
        self, limit: int | None = None, offset: int | None = None
    ) -> list[TopicName]:
        pass

    @property
    @abstractmethod
    async def author_count(self) -> int:
        pass

    @property
    @abstractmethod
    async def topic_count(self) -> int:
        pass

    @property
    @abstractmethod
    async def entry_count(self) -> int:
        pass

    @abstractmethod
    async def get_random_entries(self, limit: int = 10) -> list[Entry]:
        pass
