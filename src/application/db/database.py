from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from application.db.paths import get_db_path

class Base(DeclarativeBase):
  pass

engine = create_engine(f"sqlite:///{get_db_path()}", future=True)

@event.listens_for(engine, "connect")
def _enable_foreign_keys(dbapi_connection: object, connection_record: object) -> None:
  cursor = dbapi_connection.cursor()
  cursor.execute("PRAGMA foreign_keys=ON")
  cursor.close()

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db() -> None:
  from application.db import models

  Base.metadata.create_all(engine)
