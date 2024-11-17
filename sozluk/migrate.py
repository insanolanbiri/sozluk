import pickle
from os import getenv

from sozluk.authorname import AuthorName
from sozluk.entry import Entry, EntryID, EntrySketch, EntryText
from sozluk.topicname import TopicName

path = getenv("DATABASE_PATH", "database.pickle")

with open(path, "rb") as f:
    dict_object = pickle.loads(f.read())

next_id = dict_object["next_id"]
old_entries = dict_object["entries"]

old_entries = [
    (k, v) for k, v in sorted(old_entries.items(), key=lambda x: x[1].identifier.value)
]

entries = {}


def rebuild_entry(entry):
    identifer = EntryID(entry.identifier.value)
    author = AuthorName(entry.author)
    topic = TopicName(entry.topic)
    text = EntryText(entry.text)
    utc_time = entry.utc_time
    sketch = EntrySketch(topic=topic, author=author, text=text)
    new_entry = Entry.from_sketch(sketch, identifer, utc_time)

    return identifer, new_entry


for eid, e in old_entries:
    new_id, new_e = rebuild_entry(e)
    entries[new_id] = new_e

with open(path + ".new", "wb") as f:
    f.write(
        pickle.dumps(
            {
                "next_id": next_id,
                "entries": entries,
            }
        )
    )
