from os import getenv

from sqlalchemy import create_engine

from sozluk.storage.sqlalchemydatabase import SQLAlchemyDatabase

url = getenv("DATABASE_URL", "sqlite:///sozluk.sqlite")
engine = create_engine(url, echo=True)
db = SQLAlchemyDatabase(engine)

db.fix_crlf()
