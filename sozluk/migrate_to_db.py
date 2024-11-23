import asyncio
import pickle
from os import getenv

from sqlalchemy import create_engine

from sozluk.authorname import AuthorName
from sozluk.entry import EntryID, EntrySketch, EntryText
from sozluk.storage.sqlalchemydatabase import (
    SQLAlchemyAuthor,
    SQLAlchemyDatabase,
    SQLAlchemyEntry,
    SQLAlchemyTopic,
)
from sozluk.topicname import TopicName

path = getenv("DATABASE_PATH", "database.pickle")
url = getenv("DATABASE_URL", "sqlite:///sozluk.sqlite")

if url is None:
    raise ValueError()

with open(path, "rb") as f:
    dict_object = pickle.loads(f.read())

next_id = dict_object["next_id"]
old_entries = dict_object["entries"]


engine = create_engine(url, echo=False)

db = SQLAlchemyDatabase(engine)


def create_dummy_entry():
    sketch = EntrySketch(
        topic=TopicName("dd"), author=AuthorName("dd"), text=EntryText("dd")
    )
    result, identifier = asyncio.run(db.add_entry(sketch))
    asyncio.run(db.del_entry(identifier))


def add_entry(e):
    with db.Session() as session:
        new_entry = SQLAlchemyEntry(
            topic=db._get_or_create(session, SQLAlchemyTopic, name=e.topic),
            author=db._get_or_create(session, SQLAlchemyAuthor, name=e.author),
            text=e.text,
            utc_time=e.utc_time,
        )
        session.add(new_entry)
        session.commit()


for i in range(1, next_id):
    entry = old_entries.get(EntryID(i))
    if entry is None:
        print(i)
        create_dummy_entry()
        continue
    add_entry(entry)
