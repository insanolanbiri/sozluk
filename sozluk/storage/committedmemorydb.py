import pickle
import random
from datetime import UTC, datetime
from threading import RLock

import aiofiles

from sozluk.authorname import AuthorName
from sozluk.entry import Entry, EntryID, EntrySketch
from sozluk.storage import EntryAddResponse, EntryDeleteResponse, SozlukStorage
from sozluk.topicname import TopicName


class CommittedMemoryDB(SozlukStorage):
    def __init__(self, file: str):
        self.__file = file

        self.__db_lock = RLock()

        dump = None
        try:
            with open(self.__file, "rb") as f:
                dump = pickle.load(f)
        except FileNotFoundError:
            pass

        if dump:
            self.__next_id: int = dump["next_id"]
            self.__entries: dict[EntryID, Entry] = dump["entries"]

        else:
            self.__next_id: int = 1
            self.__entries: dict[EntryID, Entry] = {}

    async def __make_next_id(self) -> EntryID:
        with self.__db_lock:
            id_candidate = self.__next_id
            self.__next_id += 1
        await self.__commit_db()
        return EntryID(id_candidate)

    async def add_entry(
        self, sketch: EntrySketch
    ) -> tuple[EntryAddResponse, EntryID | None]:
        new_id = await self.__make_next_id()
        new_entry = Entry.from_sketch(sketch, new_id, datetime.now(UTC))

        with self.__db_lock:
            for entry in self.__entries.values():
                if entry.topic == sketch.topic and entry.text == sketch.text:
                    return EntryAddResponse.DEFINITION_EXISTS, None
            self.__entries[new_id] = new_entry
        await self.__commit_db()

        return EntryAddResponse.SUCCESS, new_id

    async def get_entry(self, entry_id: EntryID) -> Entry | None:
        # assuming no need to lock
        return self.__entries.get(entry_id, None)

    async def get_topic(self, topic_name: TopicName) -> list[Entry]:
        entries = []

        with self.__db_lock:
            for entry in self.__entries.values():
                if entry.topic == topic_name:
                    entries.append(entry)

        return entries

    async def topic_search_basic(
        self, query: str, limit: int | None = None
    ) -> list[TopicName]:
        matches = []
        for topic in await self.get_latest_topics(limit=None):
            if query in topic:
                matches.append(topic)
                if limit and len(matches) >= limit:
                    break
        return matches

    async def del_entry(self, entry_id: EntryID) -> EntryDeleteResponse:
        if self.get_entry(entry_id) is None:
            return EntryDeleteResponse.ENTRY_NOT_FOUND
        with self.__db_lock:
            if self.__entries.pop(entry_id, None) is None:
                return EntryDeleteResponse.ENTRY_NOT_FOUND
        await self.__commit_db()

        return EntryDeleteResponse.SUCCESS

    @property
    async def entry_count(self) -> int:
        return len(self.__entries)

    async def get_author(self, author_name: AuthorName) -> list[Entry]:
        entries = []
        with self.__db_lock:
            for entry in self.__entries.values():
                if entry.author == author_name:
                    entries.append(entry)
        return entries

    @property
    async def author_count(self) -> int:
        authors = set()
        with self.__db_lock:
            for entry in self.__entries.values():
                authors.add(entry.author)

        return len(authors)

    @property
    async def topic_count(self) -> int:
        topics = set()
        with self.__db_lock:
            for entry in self.__entries.values():
                topics.add(entry.topic)

        return len(topics)

    async def get_latest_topics(self, limit: int | None = None) -> list[TopicName]:
        # dict objects preserve insertion order in this python version
        topics = {}

        with self.__db_lock:
            entry_list = list(self.__entries.values())
        for entry in entry_list[::-1]:
            topics[entry.topic] = None
            if limit and len(topics) >= limit:
                break
        return list(topics.keys())

    async def get_latest_authors(self, limit: int | None = None) -> list[AuthorName]:
        authors = {}

        with self.__db_lock:
            entry_list = list(self.__entries.values())
        for entry in entry_list[::-1]:
            authors[entry.author] = None
            if limit and len(authors) >= limit:
                break
        return list(authors.keys())

    async def __commit_db(self):
        with self.__db_lock:
            next_id = self.__next_id
            entries = self.__entries.copy()

        async with aiofiles.open(self.__file, "wb") as f:
            dump = pickle.dumps(
                {
                    "next_id": next_id,
                    "entries": entries,
                },
            )
            await f.write(dump)

    async def get_random_entries(self, limit: int = 10) -> list[Entry]:
        with self.__db_lock:
            entry_ids = list(self.__entries.keys())
        if limit > (count := len(entry_ids)):
            limit = count
        selected = random.sample(entry_ids, k=limit)

        result = []
        for entry_id in selected:
            if entry := await self.get_entry(entry_id):
                result.append(entry)

        return result
