import typing as t
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel
from sqlalchemy import select

from application.db.database import SessionLocal
from application.db.models import Dataset as DatasetRow
from application.db.paths import get_datasets_dir
from application.db.storage import FileIntegrityError, FileStore
from application.enums import ProblemType

class DatasetMetadata(BaseModel):
  id: int
  name: str
  type: ProblemType
  target: str
  original_filename: str
  storage_filename: str
  md5_hash: str
  size_bytes: int
  date: str

  @property
  def path(self) -> str:
    """Resolves the on-disk location of the managed dataset file, verifying its MD5 first."""
    store = FileStore(get_datasets_dir())

    if not store.verify_integrity(self.storage_filename, self.md5_hash):
      raise FileIntegrityError(
        f"Dataset '{self.name}' está corrompido ou foi alterado externamente (MD5 não corresponde)."
      )

    return str(store.resolve_path(self.storage_filename))

  @classmethod
  def from_row(cls, row: DatasetRow) -> "DatasetMetadata":
    return cls(
      id=row.id,
      name=row.name,
      type=row.problem_type,
      target=row.target,
      original_filename=row.original_filename,
      storage_filename=row.storage_filename,
      md5_hash=row.md5_hash,
      size_bytes=row.size_bytes,
      date=row.created_at,
    )

class DatasetManager:

  @classmethod
  def get_all(cls) -> list[DatasetMetadata]:
    with SessionLocal() as session:
      rows = session.scalars(select(DatasetRow).order_by(DatasetRow.id)).all()

      return [DatasetMetadata.from_row(row) for row in rows]

  @classmethod
  def add_dataset(cls, name: str, filepath: str, problem_type: str | ProblemType, target: str) -> DatasetMetadata:
    store = FileStore(get_datasets_dir())
    stored = store.save(Path(filepath))

    with SessionLocal() as session:
      row = DatasetRow(
        name=name,
        problem_type=ProblemType(problem_type),
        target=target,
        original_filename=stored.original_filename,
        storage_filename=stored.storage_filename,
        md5_hash=stored.md5_hash,
        size_bytes=stored.size_bytes,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      )

      session.add(row)
      session.commit()
      session.refresh(row)

      return DatasetMetadata.from_row(row)

  @classmethod
  def update_dataset(cls, payload: dict[str, t.Any]) -> DatasetMetadata:
    target_id = int(payload["id"])
    store = FileStore(get_datasets_dir())

    with SessionLocal() as session:
      row = session.get(DatasetRow, target_id)

      if row is None:
        raise ValueError(f"Dataset com ID {target_id} não encontrado.")

      if payload.get("name") is not None:
        row.name = payload["name"]

      if payload.get("type") is not None:
        row.problem_type = ProblemType(payload["type"])

      if payload.get("target") is not None:
        row.target = payload["target"]

      new_path = payload.get("path")
      current_path = str(store.resolve_path(row.storage_filename))

      if new_path is not None and new_path != current_path:
        old_storage_filename = row.storage_filename
        stored = store.save(Path(new_path))

        row.original_filename = stored.original_filename
        row.storage_filename = stored.storage_filename
        row.md5_hash = stored.md5_hash
        row.size_bytes = stored.size_bytes

        store.delete(old_storage_filename)

      session.commit()
      session.refresh(row)

      return DatasetMetadata.from_row(row)

  @classmethod
  def delete_dataset(cls, target_id: str | int) -> None:
    with SessionLocal() as session:
      row = session.get(DatasetRow, int(target_id))

      if row is None:
        return

      storage_filename = row.storage_filename

      session.delete(row)
      session.commit()

    FileStore(get_datasets_dir()).delete(storage_filename)
