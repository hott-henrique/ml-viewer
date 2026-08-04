import hashlib
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

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
