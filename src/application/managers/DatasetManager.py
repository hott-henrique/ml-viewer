import typing as t
from datetime import datetime
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from application.db.database import SessionLocal
from application.db.models import Dataset as DatasetRow
from application.db.models import DatasetFile as DatasetFileRow
from application.db.paths import get_datasets_dir
from application.db.storage import FileIntegrityError, FileStore, StoredFile
from application.enums import DatasetFileRole, DatasetLayout, ProblemType
from application.i18n import _

SUPERVISED_TYPES = {ProblemType.CLASSIFICATION, ProblemType.REGRESSION}
SEMI_SUPERVISED_TYPES = {
  ProblemType.SEMI_SUPERVISED_CLASSIFICATION,
  ProblemType.SEMI_SUPERVISED_REGRESSION,
}
UNSUPERVISED_TYPES = {
  ProblemType.CLUSTERING,
  ProblemType.DIMENSIONALITY_REDUCTION,
  ProblemType.ASSOCIATION_RULES,
}

LAYOUT_ROLES: dict[DatasetLayout, frozenset[tuple[DatasetFileRole, int]]] = {
  DatasetLayout.NO_SPLIT: frozenset({(DatasetFileRole.FULL, 0)}),
  DatasetLayout.TRAIN_TEST_SPLIT: frozenset({
    (DatasetFileRole.TRAIN, 0),
    (DatasetFileRole.TEST, 0),
  }),
  DatasetLayout.LABELED_UNLABELED: frozenset({
    (DatasetFileRole.LABELED, 0),
    (DatasetFileRole.UNLABELED, 0),
    (DatasetFileRole.TEST, 0),
  }),
}

def validate_problem_target(problem_type: ProblemType, target: int | None) -> int | None:
  if problem_type in SUPERVISED_TYPES or problem_type in SEMI_SUPERVISED_TYPES:
    if target is None:
      key = (
        "dataset.err.semi_supervised_requires_target"
        if problem_type in SEMI_SUPERVISED_TYPES
        else "dataset.err.supervised_requires_target"
      )
      raise ValueError(_(key))
    if not isinstance(target, int) or target < 0:
      raise ValueError(_("dataset.err.invalid_target_index"))
    return target

  if problem_type in UNSUPERVISED_TYPES:
    if target is not None:
      raise ValueError(_("dataset.err.unsupervised_no_target"))
    return None

  raise ValueError(_("dataset.err.unsupported_problem_type").format(problem_type=problem_type))

def read_dataset_frame(path: str | Path, has_header: bool, *, nrows: int | None = None) -> pd.DataFrame:
  """Load a CSV respecting the dataset-level header flag."""
  header: int | None = 0 if has_header else None
  return pd.read_csv(path, header=header, nrows=nrows)

def peek_ncols(path: str | Path, has_header: bool) -> int:
  df = read_dataset_frame(path, has_header, nrows=0)
  return df.shape[1]

def to_binary_item_matrix(df: pd.DataFrame) -> pd.DataFrame:
  """Convert a transaction table into a boolean item matrix (rows=transactions, cols=items)."""
  if df.empty:
    raise ValueError(_("dataset.err.empty_association_frame"))

  binary = df.notna() & (df != 0) & (df != False) & (df != "0") & (df != "")  # noqa: E712
  return binary.astype(bool)

def peek_column_names(path: str | Path, has_header: bool) -> list[str]:
  df = read_dataset_frame(path, has_header, nrows=0)
  return [str(c) for c in df.columns]

def format_target_display(index: int, names: list[str] | None = None) -> str:
  if names is not None and 0 <= index < len(names):
    return f"{index} — {names[index]}"
  return str(index)

def parse_target_display(raw: str) -> int:
  token = raw.split("—", 1)[0].strip()
  return int(token)

class DatasetFileMeta(BaseModel):
  role: DatasetFileRole
  ordinal: int = 0
  original_filename: str
  storage_filename: str
  md5_hash: str
  size_bytes: int

  @property
  def path(self) -> str:
    store = FileStore(get_datasets_dir())

    if not store.verify_integrity(self.storage_filename, self.md5_hash):
      raise FileIntegrityError(_("dataset.err.file_integrity").format(name=self.original_filename))

    return str(store.resolve_path(self.storage_filename))

  @classmethod
  def from_row(cls, row: DatasetFileRow) -> "DatasetFileMeta":
    return cls(
      role=row.role,
      ordinal=row.ordinal,
      original_filename=row.original_filename,
      storage_filename=row.storage_filename,
      md5_hash=row.md5_hash,
      size_bytes=row.size_bytes,
    )

class DatasetMetadata(BaseModel):
  id: int
  name: str
  type: ProblemType
  target: t.Optional[int] = None
  has_header: bool = True
  layout: DatasetLayout = DatasetLayout.NO_SPLIT
  files: list[DatasetFileMeta] = Field(default_factory=list)
  date: str

  def file_for(self, role: DatasetFileRole, ordinal: int = 0) -> DatasetFileMeta:
    for file_meta in self.files:
      if file_meta.role == role and file_meta.ordinal == ordinal:
        return file_meta

    raise ValueError(_("dataset.err.missing_role").format(role=role.value))

  def path_for(self, role: DatasetFileRole, ordinal: int = 0) -> str:
    return self.file_for(role, ordinal).path

  @property
  def path(self) -> str:
    """Primary path: Full for NoSplit, Train for TrainTestSplit, Labeled for LabeledUnlabeled."""
    if self.layout == DatasetLayout.TRAIN_TEST_SPLIT:
      return self.path_for(DatasetFileRole.TRAIN)

    if self.layout == DatasetLayout.LABELED_UNLABELED:
      return self.path_for(DatasetFileRole.LABELED)

    return self.path_for(DatasetFileRole.FULL)

  @property
  def full_path(self) -> str:
    return self.path_for(DatasetFileRole.FULL)

  @property
  def train_path(self) -> str:
    return self.path_for(DatasetFileRole.TRAIN)

  @property
  def test_path(self) -> str:
    return self.path_for(DatasetFileRole.TEST)

  @property
  def labeled_path(self) -> str:
    return self.path_for(DatasetFileRole.LABELED)

  @property
  def unlabeled_path(self) -> str:
    return self.path_for(DatasetFileRole.UNLABELED)

  @classmethod
  def from_row(cls, row: DatasetRow) -> "DatasetMetadata":
    return cls(
      id=row.id,
      name=row.name,
      type=row.problem_type,
      target=row.target,
      has_header=bool(row.has_header),
      layout=row.layout,
      files=[DatasetFileMeta.from_row(f) for f in (row.files or [])],
      date=row.created_at,
    )

def _validate_layout_and_files(
  problem_type: ProblemType,
  layout: DatasetLayout,
  file_specs: list[tuple[DatasetFileRole, int, Path]],
  has_header: bool,
) -> None:
  if problem_type in UNSUPERVISED_TYPES and layout != DatasetLayout.NO_SPLIT:
    raise ValueError(_("dataset.err.unsupervised_requires_nosplit"))

  if problem_type in SUPERVISED_TYPES and layout != DatasetLayout.TRAIN_TEST_SPLIT:
    raise ValueError(_("dataset.err.supervised_requires_train_test_split"))

  if problem_type in SEMI_SUPERVISED_TYPES and layout != DatasetLayout.LABELED_UNLABELED:
    raise ValueError(_("dataset.err.semi_supervised_requires_labeled_unlabeled"))

  if layout == DatasetLayout.NO_SPLIT and problem_type not in UNSUPERVISED_TYPES:
    raise ValueError(_("dataset.err.nosplit_layout_restricted"))

  if layout == DatasetLayout.TRAIN_TEST_SPLIT and problem_type not in SUPERVISED_TYPES:
    raise ValueError(_("dataset.err.train_test_layout_restricted"))

  if layout == DatasetLayout.LABELED_UNLABELED and problem_type not in SEMI_SUPERVISED_TYPES:
    raise ValueError(_("dataset.err.labeled_unlabeled_layout_restricted"))

  expected = LAYOUT_ROLES.get(layout)

  if expected is None:
    raise ValueError(_("dataset.err.unsupported_layout").format(layout=layout.value))

  actual = frozenset((role, ordinal) for role, ordinal, _ in file_specs)

  if actual != expected:
    raise ValueError(_("dataset.err.layout_files_mismatch").format(layout=layout.value))

  if layout == DatasetLayout.TRAIN_TEST_SPLIT:
    paths_by_role = {role: path for role, _ordinal, path in file_specs}
    train_cols = peek_ncols(paths_by_role[DatasetFileRole.TRAIN], has_header)
    test_cols = peek_ncols(paths_by_role[DatasetFileRole.TEST], has_header)

    if train_cols != test_cols:
      raise ValueError(_("dataset.err.ncols_mismatch").format(train=train_cols, test=test_cols))

  if layout == DatasetLayout.LABELED_UNLABELED:
    paths_by_role = {role: path for role, _ordinal, path in file_specs}
    labeled_cols = peek_ncols(paths_by_role[DatasetFileRole.LABELED], has_header)
    unlabeled_cols = peek_ncols(paths_by_role[DatasetFileRole.UNLABELED], has_header)
    test_cols = peek_ncols(paths_by_role[DatasetFileRole.TEST], has_header)

    if labeled_cols != unlabeled_cols or labeled_cols != test_cols:
      raise ValueError(
        _("dataset.err.labeled_unlabeled_ncols_mismatch").format(
          labeled=labeled_cols,
          unlabeled=unlabeled_cols,
          test=test_cols,
        )
      )

def _store_files(
  store: FileStore,
  file_specs: list[tuple[DatasetFileRole, int, Path]],
) -> list[tuple[DatasetFileRole, int, StoredFile]]:
  return [(role, ordinal, store.save(path)) for role, ordinal, path in file_specs]

BASE_QUERY = select(DatasetRow).options(selectinload(DatasetRow.files))

class DatasetManager:

  @classmethod
  def get_all(cls) -> list[DatasetMetadata]:
    with SessionLocal() as session:
      rows = session.scalars(BASE_QUERY.order_by(DatasetRow.id)).all()

      return [DatasetMetadata.from_row(row) for row in rows]

  @classmethod
  def add_dataset(
    cls,
    name: str,
    problem_type: str | ProblemType,
    *,
    layout: DatasetLayout | str = DatasetLayout.NO_SPLIT,
    has_header: bool = True,
    target: int | None = None,
    files: dict[str, str] | None = None,
    filepath: str | None = None,
  ) -> DatasetMetadata:
    """Create a dataset.

    ``files`` maps role value → source path, e.g. ``{"Full": "..."}`` or
    ``{"Train": "...", "Test": "..."}``. Legacy ``filepath`` is treated as Full.
    """
    problem = ProblemType(problem_type)
    layout_enum = DatasetLayout(layout)
    normalized_target = validate_problem_target(problem, target)

    file_specs = cls._build_file_specs(layout_enum, files=files, filepath=filepath)
    _validate_layout_and_files(problem, layout_enum, file_specs, has_header)

    if normalized_target is not None:
      primary = cls._primary_path_from_specs(layout_enum, file_specs)
      ncols = peek_ncols(primary, has_header)

      if normalized_target >= ncols:
        raise ValueError(_("dataset.err.target_out_of_range").format(index=normalized_target, ncols=ncols))

    store = FileStore(get_datasets_dir())
    stored_files = _store_files(store, file_specs)

    with SessionLocal() as session:
      row = DatasetRow(
        name=name,
        problem_type=problem,
        target=normalized_target,
        has_header=has_header,
        layout=layout_enum,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      )
      session.add(row)
      session.flush()

      for role, ordinal, stored in stored_files:
        session.add(DatasetFileRow(
          dataset_id=row.id,
          role=role,
          ordinal=ordinal,
          original_filename=stored.original_filename,
          storage_filename=stored.storage_filename,
          md5_hash=stored.md5_hash,
          size_bytes=stored.size_bytes,
        ))

      session.commit()

      row = session.scalars(BASE_QUERY.where(DatasetRow.id == row.id)).one()

      return DatasetMetadata.from_row(row)

  @classmethod
  def update_dataset(cls, payload: dict[str, t.Any]) -> DatasetMetadata:
    target_id = int(payload["id"])
    store = FileStore(get_datasets_dir())

    with SessionLocal() as session:
      row = session.scalars(BASE_QUERY.where(DatasetRow.id == target_id)).one_or_none()

      if row is None:
        raise ValueError(_("dataset.err.not_found").format(id=target_id))

      if payload.get("name") is not None:
        row.name = payload["name"]

      problem = row.problem_type

      if payload.get("type") is not None:
        problem = ProblemType(payload["type"])
        row.problem_type = problem

      if "has_header" in payload and payload["has_header"] is not None:
        row.has_header = bool(payload["has_header"])

      layout = row.layout

      if payload.get("layout") is not None:
        layout = DatasetLayout(payload["layout"])
        row.layout = layout

      if "target" in payload or payload.get("type") is not None:
        incoming_target = payload["target"] if "target" in payload else row.target
        row.target = validate_problem_target(problem, incoming_target)

      files_payload = payload.get("files")
      filepath = payload.get("path") or payload.get("filepath")
      old_storage = [f.storage_filename for f in row.files]

      if files_payload is not None or filepath is not None:
        file_specs = cls._build_file_specs(layout, files=files_payload, filepath=filepath)
        _validate_layout_and_files(problem, layout, file_specs, row.has_header)

        if row.target is not None:
          ncols = peek_ncols(cls._primary_path_from_specs(layout, file_specs), row.has_header)

          if row.target >= ncols:
            raise ValueError(_("dataset.err.target_out_of_range").format(index=row.target, ncols=ncols))

        stored_files = _store_files(store, file_specs)

        for existing in list(row.files):
          session.delete(existing)

        session.flush()

        for role, ordinal, stored in stored_files:
          session.add(DatasetFileRow(
            dataset_id=row.id,
            role=role,
            ordinal=ordinal,
            original_filename=stored.original_filename,
            storage_filename=stored.storage_filename,
            md5_hash=stored.md5_hash,
            size_bytes=stored.size_bytes,
          ))
      else:
        _validate_layout_and_files(
          problem,
          layout,
          [(f.role, f.ordinal, store.resolve_path(f.storage_filename)) for f in row.files],
          row.has_header,
        )
        old_storage = []

      session.commit()

      row = session.scalars(BASE_QUERY.where(DatasetRow.id == target_id)).one()
      metadata = DatasetMetadata.from_row(row)

    for storage_filename in old_storage:
      store.delete(storage_filename)

    return metadata

  @classmethod
  def delete_dataset(cls, target_id: str | int) -> None:
    store = FileStore(get_datasets_dir())

    with SessionLocal() as session:
      row = session.scalars(BASE_QUERY.where(DatasetRow.id == int(target_id))).one_or_none()

      if row is None:
        return

      storage_filenames = [f.storage_filename for f in row.files]
      session.delete(row)
      session.commit()

    for storage_filename in storage_filenames:
      store.delete(storage_filename)

  @staticmethod
  def _primary_path_from_specs(
    layout: DatasetLayout,
    file_specs: list[tuple[DatasetFileRole, int, Path]],
  ) -> Path:
    by_role = {role: path for role, _ordinal, path in file_specs}

    if layout == DatasetLayout.TRAIN_TEST_SPLIT:
      return by_role[DatasetFileRole.TRAIN]

    if layout == DatasetLayout.LABELED_UNLABELED:
      return by_role[DatasetFileRole.LABELED]

    return by_role[DatasetFileRole.FULL]

  @staticmethod
  def _build_file_specs(
    layout: DatasetLayout,
    *,
    files: dict[str, str] | None = None,
    filepath: str | None = None,
  ) -> list[tuple[DatasetFileRole, int, Path]]:
    if files:
      specs: list[tuple[DatasetFileRole, int, Path]] = []

      for role_key, path_str in files.items():
        role = DatasetFileRole(role_key)
        specs.append((role, 0, Path(path_str)))

      return specs

    if filepath is not None:
      if layout != DatasetLayout.NO_SPLIT:
        raise ValueError(_("dataset.err.layout_files_mismatch").format(layout=layout.value))

      return [(DatasetFileRole.FULL, 0, Path(filepath))]

    raise ValueError(_("dataset.form.err_name_file"))
