from datetime import UTC, datetime

import sqlalchemy
from sqlalchemy import delete, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from sozluk.authorname import AuthorName
from sozluk.entry import Entry, EntryID, EntrySketch, EntryText
from sozluk.storage import EntryAddResponse, EntryDeleteResponse, SozlukStorage
from sozluk.topicname import TopicName


class Base(DeclarativeBase):
    pass


class SQLAlchemyEntry(Base):
    __tablename__ = "entries"
    __table_args__ = {"sqlite_autoincrement": True}
    identifier = sqlalchemy.Column(
        "id", sqlalchemy.Integer, primary_key=True, autoincrement=True
    )
    topic_name = mapped_column(sqlalchemy.ForeignKey("topics.name"))
    topic = relationship("SQLAlchemyTopic", back_populates="entries")
    author_name = mapped_column(sqlalchemy.ForeignKey("authors.name"))
    author = relationship("SQLAlchemyAuthor", back_populates="entries")
    utc_time = sqlalchemy.Column("utc_time", sqlalchemy.DateTime(), nullable=False)
    text = sqlalchemy.Column("text", sqlalchemy.UnicodeText(), nullable=False)

    def to_Entry(self):
        return Entry(
            topic=self.topic.to_TopicName(),
            author=self.author.to_AuthorName(),
            utc_time=self.utc_time,
            identifier=self.to_EntryID(),
            text=EntryText(self.text),
        )

    def to_EntryID(self):
        return EntryID(self.identifier)


class SQLAlchemyTopic(Base):
    __tablename__ = "topics"
    name = sqlalchemy.Column(
        "name", sqlalchemy.String(50), nullable=False, unique=True, primary_key=True
    )
    entries = relationship(
        "SQLAlchemyEntry", back_populates="topic", cascade="all,delete"
    )

    def to_TopicName(self):
        return TopicName(self.name)


class SQLAlchemyAuthor(Base):
    __tablename__ = "authors"
    name = sqlalchemy.Column(
        "name", sqlalchemy.String(40), nullable=False, unique=True, primary_key=True
    )
    entries = relationship(
        "SQLAlchemyEntry", back_populates="author", cascade="all,delete"
    )

    def to_AuthorName(self):
        return AuthorName(self.name)


class SQLAlchemyDatabase(SozlukStorage):
    def __init__(
        self,
        engine: sqlalchemy.Engine,
    ) -> None:
        self.engine = engine

        Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(self.engine)

    @staticmethod
    def _get_or_create(session, model, **kwargs):
        instance = session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            session.add(instance)
            session.commit()
            return instance

    async def get_entry(self, entry_id: EntryID) -> Entry | None:
        with Session(self.engine) as session:
            entry = session.scalar(
                select(SQLAlchemyEntry).where(
                    SQLAlchemyEntry.identifier == entry_id.value
                )
            )

            if entry is None:
                return None

            return entry.to_Entry()

    async def add_entry(
        self, sketch: EntrySketch
    ) -> tuple[EntryAddResponse, EntryID | None]:
        with Session(self.engine) as session:
            if session.scalar(
                select(SQLAlchemyEntry).where(
                    (SQLAlchemyEntry.topic.has(SQLAlchemyTopic.name == sketch.topic))
                    & (SQLAlchemyEntry.text == sketch.text)
                )
            ):
                # not sure if some race condition could happen here
                return EntryAddResponse.DEFINITION_EXISTS, None

            new_entry = SQLAlchemyEntry(
                text=sketch.text,
                utc_time=datetime.now(UTC),
                topic=self._get_or_create(session, SQLAlchemyTopic, name=sketch.topic),
                author=self._get_or_create(
                    session, SQLAlchemyAuthor, name=sketch.author
                ),
            )
            session.add(new_entry)
            session.commit()

            new_id = new_entry.to_EntryID()

        return EntryAddResponse.SUCCESS, new_id

    async def get_topic(self, topic_name: TopicName) -> list[Entry]:
        with Session(self.engine) as session:
            topic = session.scalar(
                select(SQLAlchemyTopic).where(SQLAlchemyTopic.name == topic_name)
            )

            if topic is None:
                return []

            entries = map(lambda sql_entry: sql_entry.to_Entry(), topic.entries)

            return list(entries)

    async def get_author(self, author_name: AuthorName) -> list[Entry]:
        with Session(self.engine) as session:
            author = session.scalar(
                select(SQLAlchemyAuthor).where(SQLAlchemyAuthor.name == author_name)
            )

            if author is None:
                return []

            entries = map(lambda sql_entry: sql_entry.to_Entry(), author.entries)

            return list(entries)

    async def del_entry(self, entry_id: EntryID) -> EntryDeleteResponse:
        with Session(self.engine) as session:
            result = session.scalar(
                delete(SQLAlchemyEntry)
                .where(SQLAlchemyEntry.identifier == entry_id.value)
                .returning(SQLAlchemyEntry)
            )

            if not result:
                return EntryDeleteResponse.ENTRY_NOT_FOUND
            session.commit()
            return EntryDeleteResponse.SUCCESS

    @property
    async def author_count(self) -> int:
        with self.Session() as session:
            return session.scalar(
                select(sqlalchemy.func.count())
                .select_from(SQLAlchemyAuthor)
                .where(SQLAlchemyAuthor.entries.any())
            )

    @property
    async def topic_count(self) -> int:
        with self.Session() as session:
            return session.scalar(
                select(sqlalchemy.func.count())
                .select_from(SQLAlchemyTopic)
                .where(SQLAlchemyTopic.entries.any())
            )

    @property
    async def entry_count(self) -> int:
        with self.Session() as session:
            return session.scalar(
                select(sqlalchemy.func.count()).select_from(SQLAlchemyEntry)
            )

    async def topic_search_basic(
        self, query: str, limit: int | None = None
    ) -> list[TopicName]:
        with self.Session() as session:
            topics = session.scalars(
                select(SQLAlchemyTopic.name)
                .where(SQLAlchemyTopic.name.like(rf"%{query}%"))
                .order_by(SQLAlchemyTopic.name)
            )

            return list(map(TopicName, topics))

    async def get_latest_authors(self, limit: int | None = None) -> list[AuthorName]:
        with self.Session() as session:
            authors = session.scalars(
                sqlalchemy.select(SQLAlchemyEntry.author_name)
                .distinct()
                .order_by(SQLAlchemyEntry.identifier.desc())
                .limit(limit)
            )

            authors = list(map(AuthorName, authors))

            return authors

    async def get_latest_topics(self, limit: int | None = None) -> list[TopicName]:
        with self.Session() as session:
            topics = session.scalars(
                select(SQLAlchemyEntry.topic_name)
                .distinct()
                .order_by(SQLAlchemyEntry.identifier.desc())
                .limit(limit)
            )

            topics = list(map(TopicName, topics))

            return topics

    async def get_random_entries(self, limit: int = 10) -> list[Entry]:
        with self.Session() as session:
            rows = session.scalars(
                select(SQLAlchemyEntry).order_by(sqlalchemy.func.random()).limit(limit)
            )
            return list(map(lambda row: row.to_Entry(), rows))


async def main():
    engine = sqlalchemy.create_engine("sqlite://", echo=True)

    db = SQLAlchemyDatabase(engine)

    resp, ident = await db.add_entry(
        EntrySketch(
            topic=TopicName("can sikintisi"),
            author=AuthorName("eren"),
            text=EntryText("yasadigim."),
        )
    )

    entry = await db.get_entry(ident)

    print(entry)
    print(await db.author_count)

    entries = await db.get_topic(TopicName("can sikintisi"))

    print(await db.get_latest_authors())

    print(entries)

    print(await db.del_entry(EntryID(15)))
    print(await db.del_entry(ident))
    print(entry)

    entries = await db.get_topic(TopicName("can sikintisi"))

    print(entries)
    print(await db.author_count)

    engine.dispose()
