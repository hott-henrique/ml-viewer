from sqlalchemy import create_engine, event, inspect, text
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

# table -> {column: DDL type}, applied via ALTER TABLE ADD COLUMN when missing (SQLite).
_SCHEMA_ADDITIONS: dict[str, dict[str, str]] = {
  "models": {
    "title": "JSON",
    "description": "JSON",
  },
  "analyses": {
    "title": "JSON",
  },
}

def _migrate_schema() -> None:
  """Adds newly introduced nullable columns to existing SQLite tables, if missing."""
  import json as _json

  inspector = inspect(engine)
  existing_tables = set(inspector.get_table_names())

  with engine.begin() as connection:
    for table_name, columns in _SCHEMA_ADDITIONS.items():
      if table_name not in existing_tables:
        continue

      existing_columns = {col["name"] for col in inspector.get_columns(table_name)}

      for column_name, column_type in columns.items():
        if column_name in existing_columns:
          continue

        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))

    # `analyses.description` moved from a plain TEXT column to a JSON-encoded one; re-encode
    # any pre-existing raw text values so they can be parsed back as JSON.
    if "analyses" in existing_tables:
      rows = connection.execute(text("SELECT id, description FROM analyses")).fetchall()

      for row_id, raw_description in rows:
        if raw_description is None:
          continue

        try:
          _json.loads(raw_description)
          continue
        except (TypeError, ValueError):
          pass

        connection.execute(
          text("UPDATE analyses SET description = :description WHERE id = :id"),
          {"description": _json.dumps(raw_description), "id": row_id},
        )

def init_db() -> None:
  from application.db import models

  Base.metadata.create_all(engine)
  _migrate_schema()
