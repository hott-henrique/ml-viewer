import typing as t
from datetime import datetime
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from application.db.database import SessionLocal
from application.db.models import Dataset as DatasetRow
from application.db.models import DatasetFile as DatasetFileRow
from application.db.paths import get_datasets_dir
from application.db.storage import FileIntegrityError, FileStore, SavedFile, combine_file_md5, delete_file, save_file
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
  logical_key: t.Optional[str] = None

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
      logical_key=row.logical_key,
    )

class DatasetMetadata(BaseModel):
  id: int
  name: str
  type: ProblemType
  target: t.Optional[int] = None
  has_header: bool = True
  layout: DatasetLayout = DatasetLayout.NO_SPLIT
  files: list[DatasetFileMeta] = Field(default_factory=list)
  version: int = 1
  md5_hash: str = ""
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
      version=row.version,
      md5_hash=row.md5_hash,
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
  file_specs: list[tuple[DatasetFileRole, int, Path]],
  keys: dict[tuple[DatasetFileRole, int], str | None] | None = None,
) -> list[tuple[DatasetFileRole, int, SavedFile]]:
  keys = keys or {}

  return [
    (role, ordinal, save_file(path, key=keys.get((role, ordinal)), scope="datasets"))
    for role, ordinal, path in file_specs
  ]

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

    stored_files = _store_files(file_specs)

    with SessionLocal() as session:
      row = DatasetRow(
        name=name,
        problem_type=problem,
        target=normalized_target,
        has_header=has_header,
        layout=layout_enum,
        version=1,
        md5_hash=combine_file_md5([
          (role.value, ordinal, stored.md5_hash) for role, ordinal, stored in stored_files
        ]),
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
          logical_key=stored.key,
        ))

      session.commit()

      row = session.scalars(BASE_QUERY.where(DatasetRow.id == row.id)).one()

      return DatasetMetadata.from_row(row)

  @classmethod
  def update_dataset(cls, payload: dict[str, t.Any]) -> DatasetMetadata:
    target_id = int(payload["id"])
    store = FileStore(get_datasets_dir())

    with SessionLocal() as session:
      source = session.scalars(BASE_QUERY.where(DatasetRow.id == target_id)).one_or_none()

      if source is None:
        raise ValueError(_("dataset.err.not_found").format(id=target_id))

      name = payload["name"] if payload.get("name") is not None else source.name
      problem = ProblemType(payload["type"]) if payload.get("type") is not None else source.problem_type
      has_header = bool(payload["has_header"]) if payload.get("has_header") is not None else source.has_header
      layout = DatasetLayout(payload["layout"]) if payload.get("layout") is not None else source.layout
      incoming_target = payload["target"] if "target" in payload else source.target
      target = validate_problem_target(problem, incoming_target)

      files_payload = payload.get("files")
      filepath = payload.get("path") or payload.get("filepath")
      copied_files: list[DatasetFileRow] = []
      stored_files: list[tuple[DatasetFileRole, int, SavedFile]] = []

      if files_payload is not None or filepath is not None:
        file_specs = cls._build_file_specs(layout, files=files_payload, filepath=filepath)
        _validate_layout_and_files(problem, layout, file_specs, has_header)

        if target is not None:
          ncols = peek_ncols(cls._primary_path_from_specs(layout, file_specs), has_header)

          if target >= ncols:
            raise ValueError(_("dataset.err.target_out_of_range").format(index=target, ncols=ncols))

        stored_files = _store_files(
          file_specs,
          {(f.role, f.ordinal): f.logical_key for f in source.files},
        )
        md5_hash = combine_file_md5([
          (role.value, ordinal, stored.md5_hash) for role, ordinal, stored in stored_files
        ])
      else:
        _validate_layout_and_files(
          problem,
          layout,
          [(f.role, f.ordinal, store.resolve_path(f.storage_filename)) for f in source.files],
          has_header,
        )
        copied_files = list(source.files)
        md5_hash = combine_file_md5([
          (f.role.value, f.ordinal, f.md5_hash) for f in copied_files
        ])

      current = session.scalar(select(func.max(DatasetRow.version)).where(DatasetRow.name == name))
      version = 1 if current is None else int(current) + 1

      row = DatasetRow(
        name=name,
        problem_type=problem,
        target=target,
        has_header=has_header,
        layout=layout,
        version=version,
        md5_hash=md5_hash,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      )
      session.add(row)
      session.flush()

      if stored_files:
        for role, ordinal, stored in stored_files:
          session.add(DatasetFileRow(
            dataset_id=row.id,
            role=role,
            ordinal=ordinal,
            original_filename=stored.original_filename,
            storage_filename=stored.storage_filename,
            md5_hash=stored.md5_hash,
            size_bytes=stored.size_bytes,
            logical_key=stored.key,
          ))
      else:
        for existing in copied_files:
          session.add(DatasetFileRow(
            dataset_id=row.id,
            role=existing.role,
            ordinal=existing.ordinal,
            original_filename=existing.original_filename,
            storage_filename=existing.storage_filename,
            md5_hash=existing.md5_hash,
            size_bytes=existing.size_bytes,
            logical_key=existing.logical_key,
          ))

      session.commit()

      row = session.scalars(BASE_QUERY.where(DatasetRow.id == row.id)).one()
      return DatasetMetadata.from_row(row)

  @classmethod
  def delete_dataset(cls, target_id: str | int) -> None:
    store = FileStore(get_datasets_dir())

    with SessionLocal() as session:
      row = session.scalars(BASE_QUERY.where(DatasetRow.id == int(target_id))).one_or_none()

      if row is None:
        return

      logical_keys = list({f.logical_key for f in row.files if f.logical_key})
      legacy_filenames = [f.storage_filename for f in row.files if not f.logical_key]
      session.delete(row)
      session.commit()

      unused_keys = [
        key for key in logical_keys
        if session.scalar(select(DatasetFileRow.id).where(DatasetFileRow.logical_key == key)) is None
      ]
      unused_legacy = [
        name for name in legacy_filenames
        if session.scalar(select(DatasetFileRow.id).where(DatasetFileRow.storage_filename == name)) is None
      ]

    for logical_key in unused_keys:
      delete_file(logical_key)

    for storage_filename in unused_legacy:
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
