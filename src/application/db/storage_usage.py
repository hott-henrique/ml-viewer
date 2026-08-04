import shutil
from pathlib import Path

from application.db.paths import (
  get_analyses_dir,
  get_data_dir,
  get_datasets_dir,
  get_db_path,
  get_experiments_dir,
  get_models_dir,
)


def dir_size_bytes(path: Path) -> int:
  """Recursively sum file sizes under path. Missing paths return 0."""
  if not path.exists():
    return 0

  if path.is_file():
    return path.stat().st_size

  total = 0

  for child in path.rglob("*"):
    if child.is_file():
      total += child.stat().st_size

  return total


def format_bytes(size: int) -> str:
  if size < 1024:
    return f"{size} B"

  value = float(size)

  for unit in ("KB", "MB", "GB", "TB"):
    value /= 1024.0

    if value < 1024.0 or unit == "TB":
      if unit == "KB" and value < 10:
        return f"{value:.1f} {unit}"

      if value < 10:
        return f"{value:.2f} {unit}"

      return f"{value:.1f} {unit}"

  return f"{size} B"


def format_percent(part: int, whole: int) -> str:
  if whole <= 0:
    return "0%"

  ratio = (part / whole) * 100.0

  if ratio == 0:
    return "0%"

  if ratio < 0.01:
    return "<0.01%"

  if ratio < 1:
    return f"{ratio:.2f}%"

  return f"{ratio:.1f}%"


def get_host_disk_usage(path: Path | None = None) -> dict[str, int]:
  """Returns total/used/free bytes for the filesystem that holds the app data dir."""
  usage = shutil.disk_usage(path or get_data_dir())

  return {
    "total": usage.total,
    "used": usage.used,
    "free": usage.free,
  }


def get_app_storage_breakdown() -> dict[str, int]:
  """Returns byte sizes for each application data area plus total."""
  datasets = dir_size_bytes(get_datasets_dir())
  models = dir_size_bytes(get_models_dir())
  analyses = dir_size_bytes(get_analyses_dir())
  experiments = dir_size_bytes(get_experiments_dir())
  database = dir_size_bytes(get_db_path())
  data_dir = dir_size_bytes(get_data_dir())

  return {
    "datasets": datasets,
    "models": models,
    "analyses": analyses,
    "experiments": experiments,
    "database": database,
    "other": max(0, data_dir - datasets - models - analyses - experiments - database),
    "total": data_dir,
  }
