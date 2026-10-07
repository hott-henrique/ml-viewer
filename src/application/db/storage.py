import hashlib
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sqlalchemy import func, select

from application.db.database import SessionLocal
from application.db.models import StoredFileRecord
from application.db.paths import get_data_dir

class FileIntegrityError(RuntimeError):
  """Raised when a file managed by the application fails its MD5 integrity check."""

def compute_md5(path: Path) -> str:
  digest = hashlib.md5()

  with open(path, "rb") as f:
    for chunk in iter(lambda: f.read(8192), b""):
      digest.update(chunk)

  return digest.hexdigest()

@dataclass(frozen=True)
class StoredFile:
  storage_filename: str
  original_filename: str
  md5_hash: str
  size_bytes: int

class FileStore:
  """Owns a directory of application-managed files, tracking MD5 integrity per file."""

  def __init__(self, root: Path) -> None:
    self.root = root
    self.root.mkdir(parents=True, exist_ok=True)

  def save(self, source_path: Path) -> StoredFile:
    original_filename = source_path.name
    storage_filename = f"{uuid.uuid4().hex}_{original_filename}"
    destination = self.root / storage_filename

    shutil.copy2(source_path, destination)

    return StoredFile(
      storage_filename=storage_filename,
      original_filename=original_filename,
      md5_hash=compute_md5(destination),
      size_bytes=destination.stat().st_size,
    )

  def resolve_path(self, storage_filename: str) -> Path:
    return self.root / storage_filename

  def verify_integrity(self, storage_filename: str, expected_md5: str) -> bool:
    path = self.resolve_path(storage_filename)

    if not path.exists():
      return False

    return compute_md5(path) == expected_md5

  def delete(self, storage_filename: str) -> None:
    path = self.resolve_path(storage_filename)

    if path.exists():
      path.unlink()

@dataclass(frozen=True)
class SavedFile:
  key: str
  version: int
  storage_filename: str
  original_filename: str
  md5_hash: str
  size_bytes: int
  path: Path
  scope: str

def _scope_root(scope: str) -> Path:
  parts = Path(scope).parts

  if not scope or scope.startswith("/") or ".." in parts:
    raise ValueError(f"Invalid file scope: {scope}")

  root = get_data_dir() / scope
  root.mkdir(parents=True, exist_ok=True)

  return root

def _to_saved(row: StoredFileRecord) -> SavedFile:
  path = FileStore(_scope_root(row.scope)).resolve_path(row.storage_filename)

  return SavedFile(
    key=row.logical_key,
    version=row.version,
    storage_filename=row.storage_filename,
    original_filename=row.original_filename,
    md5_hash=row.md5_hash,
    size_bytes=row.size_bytes,
    path=path,
    scope=row.scope,
  )

def save_file(path: str | Path, *, key: str | None = None, scope: str = "files") -> SavedFile:
  """Copy a file into the application store and record a new version.

  Without ``key``, this starts a new logical file at version 1. With an existing
  ``key``, the previous blob stays on disk and the new row uses ``max(version) + 1``.
  """
  source = Path(path)

  with SessionLocal() as session:
    existing_scope = None

    if key is not None:
      existing_scope = session.scalar(
        select(StoredFileRecord.scope)
        .where(StoredFileRecord.logical_key == key)
        .limit(1)
      )

    target_scope = existing_scope or scope
    stored = FileStore(_scope_root(target_scope)).save(source)

    if key is None:
      logical_key = uuid.uuid4().hex
      version = 1
    else:
      logical_key = key
      current = session.scalar(
        select(func.max(StoredFileRecord.version)).where(StoredFileRecord.logical_key == key)
      )
      version = 1 if current is None else int(current) + 1

    row = StoredFileRecord(
      logical_key=logical_key,
      version=version,
      storage_filename=stored.storage_filename,
      original_filename=stored.original_filename,
      md5_hash=stored.md5_hash,
      size_bytes=stored.size_bytes,
      scope=target_scope,
      created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    session.add(row)
    session.commit()
    session.refresh(row)

    return _to_saved(row)

def load_file(key: str, version: int | None = None) -> SavedFile:
  """Return one version of a stored file. Omitting ``version`` returns the highest."""
  with SessionLocal() as session:
    query = select(StoredFileRecord).where(StoredFileRecord.logical_key == key)

    if version is None:
      query = query.order_by(StoredFileRecord.version.desc())
    else:
      query = query.where(StoredFileRecord.version == version)

    row = session.scalars(query).first()

    if row is None:
      label = key if version is None else f"{key}@{version}"
      raise FileNotFoundError(label)

    return _to_saved(row)

def discard_file(saved: SavedFile) -> None:
  """Remove one just-written version and its blob. Used to roll back a failed import."""
  with SessionLocal() as session:
    row = session.scalar(
      select(StoredFileRecord).where(
        StoredFileRecord.logical_key == saved.key,
        StoredFileRecord.version == saved.version,
      )
    )

    if row is not None:
      session.delete(row)
      session.commit()

  FileStore(_scope_root(saved.scope)).delete(saved.storage_filename)

def delete_file(key: str) -> None:
  """Remove every version of a logical file, including blobs."""
  with SessionLocal() as session:
    rows = list(session.scalars(select(StoredFileRecord).where(StoredFileRecord.logical_key == key)).all())

    for row in rows:
      session.delete(row)

    session.commit()

  for row in rows:
    FileStore(_scope_root(row.scope)).delete(row.storage_filename)
