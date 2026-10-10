import typing as t

from sqlalchemy import Enum as SAEnum
from sqlalchemy import JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.db.database import Base
from application.enums import (
  AnalysisOutputKind,
  DatasetFileRole,
  DatasetLayout,
  ExperimentStatus,
  ProblemType,
)

FileRef = dict[str, t.Any]
HyperParamValue = int | float | bool | str | FileRef | list[FileRef]

def _str_enum(enum_cls: type) -> SAEnum:
  """Maps a StrEnum to its `.value` (not `.name`) when stored in SQLite."""
  return SAEnum(enum_cls, values_callable=lambda cls: [member.value for member in cls])

class Dataset(Base):
  __tablename__ = "datasets"
  __table_args__ = (UniqueConstraint("name", "version", name="uq_dataset_name_version"),)

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str]
  problem_type: Mapped[ProblemType] = mapped_column(_str_enum(ProblemType))
  target: Mapped[t.Optional[int]] = mapped_column(default=None)
  has_header: Mapped[bool] = mapped_column(default=True)
  layout: Mapped[DatasetLayout] = mapped_column(_str_enum(DatasetLayout), default=DatasetLayout.NO_SPLIT)
  version: Mapped[int] = mapped_column(default=1)
  md5_hash: Mapped[str] = mapped_column(default="")
  created_at: Mapped[str]

  files: Mapped[list["DatasetFile"]] = relationship(
    back_populates="dataset",
    cascade="all, delete-orphan",
  )
  experiments: Mapped[list["Experiment"]] = relationship(back_populates="dataset")

class DatasetFile(Base):
  __tablename__ = "dataset_files"
  __table_args__ = (
    UniqueConstraint("dataset_id", "role", "ordinal", name="uq_dataset_file_role_ordinal"),
  )

  id: Mapped[int] = mapped_column(primary_key=True)
  dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"))
  role: Mapped[DatasetFileRole] = mapped_column(_str_enum(DatasetFileRole))
  ordinal: Mapped[int] = mapped_column(default=0)
  original_filename: Mapped[str]
  storage_filename: Mapped[str]
  md5_hash: Mapped[str]
  size_bytes: Mapped[int]
  logical_key: Mapped[t.Optional[str]] = mapped_column(default=None)

  dataset: Mapped["Dataset"] = relationship(back_populates="files")

class Environment(Base):
  """Catalog of environment kinds (native + imported plugins), analogous to Model."""

  __tablename__ = "environments"
  __table_args__ = (UniqueConstraint("name", "version", name="uq_environment_name_version"),)

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str]
  class_name: Mapped[str]
  module: Mapped[t.Optional[str]] = mapped_column(default=None)
  title: Mapped[t.Optional[t.Any]] = mapped_column(JSON, default=None)
  description: Mapped[t.Optional[t.Any]] = mapped_column(JSON, default=None)
  params: Mapped[list[dict[str, t.Any]]] = mapped_column(JSON, default=list)
  storage_filename: Mapped[t.Optional[str]] = mapped_column(default=None)
  original_filename: Mapped[t.Optional[str]] = mapped_column(default=None)
  md5_hash: Mapped[t.Optional[str]] = mapped_column(default=None)
  size_bytes: Mapped[t.Optional[int]] = mapped_column(default=None)
  logical_key: Mapped[t.Optional[str]] = mapped_column(default=None)
  version: Mapped[int] = mapped_column(default=1)
  is_native: Mapped[bool] = mapped_column(default=False)
  created_at: Mapped[str]

class AgentEnvironmentCompat(Base):
  __tablename__ = "agent_environment_compat"
  __table_args__ = (UniqueConstraint("agent", "env", name="uq_agent_env_compat"),)

  id: Mapped[int] = mapped_column(primary_key=True)
  agent: Mapped[str]
  env: Mapped[str]

class Experiment(Base):
  __tablename__ = "experiments"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str]
  dataset_id: Mapped[t.Optional[int]] = mapped_column(
    ForeignKey("datasets.id", ondelete="RESTRICT"),
    nullable=True,
    default=None,
  )
  environment_kind: Mapped[t.Optional[str]] = mapped_column(nullable=True, default=None)
  environment_params: Mapped[t.Optional[dict[str, t.Any]]] = mapped_column(JSON, default=None)
  model_name: Mapped[str]
  model_version: Mapped[int] = mapped_column(default=1)
  hyperparameters: Mapped[dict[str, HyperParamValue]] = mapped_column(JSON)
  status: Mapped[ExperimentStatus] = mapped_column(_str_enum(ExperimentStatus))
  analyses: Mapped[list[dict[str, t.Any]]] = mapped_column(JSON, default=list)
  result_artifacts: Mapped[list[dict[str, t.Any]]] = mapped_column(JSON, default=list)
  split_config: Mapped[t.Optional[dict[str, t.Any]]] = mapped_column(JSON, default=None)
  train_config: Mapped[t.Optional[dict[str, t.Any]]] = mapped_column(JSON, default=None)
  model_pickle_filename: Mapped[t.Optional[str]] = mapped_column(default=None)
  model_pickle_md5: Mapped[t.Optional[str]] = mapped_column(default=None)
  model_pickle_size: Mapped[t.Optional[int]] = mapped_column(default=None)
  model_pickle_key: Mapped[t.Optional[str]] = mapped_column(default=None)
  created_at: Mapped[str]

  dataset: Mapped[t.Optional["Dataset"]] = relationship(back_populates="experiments")

class Model(Base):
  __tablename__ = "models"
  __table_args__ = (
    UniqueConstraint("name", "problem_type", "version", name="uq_model_name_type_version"),
  )

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str]
  problem_type: Mapped[ProblemType] = mapped_column(_str_enum(ProblemType))
  class_name: Mapped[str]
  module: Mapped[t.Optional[str]] = mapped_column(default=None)
  title: Mapped[t.Optional[t.Any]] = mapped_column(JSON, default=None)
  description: Mapped[t.Optional[t.Any]] = mapped_column(JSON, default=None)
  params: Mapped[list[dict[str, t.Any]]] = mapped_column(JSON, default=list)
  storage_filename: Mapped[t.Optional[str]] = mapped_column(default=None)
  original_filename: Mapped[t.Optional[str]] = mapped_column(default=None)
  md5_hash: Mapped[t.Optional[str]] = mapped_column(default=None)
  size_bytes: Mapped[t.Optional[int]] = mapped_column(default=None)
  logical_key: Mapped[t.Optional[str]] = mapped_column(default=None)
  version: Mapped[int] = mapped_column(default=1)
  is_native: Mapped[bool] = mapped_column(default=False)
  created_at: Mapped[str]

class Analysis(Base):
  __tablename__ = "analyses"
  __table_args__ = (
    UniqueConstraint("name", "problem_type", "version", name="uq_analysis_name_type_version"),
  )

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str]
  problem_type: Mapped[ProblemType] = mapped_column(_str_enum(ProblemType))
  class_name: Mapped[str]
  module: Mapped[t.Optional[str]] = mapped_column(default=None)
  output_kind: Mapped[AnalysisOutputKind] = mapped_column(_str_enum(AnalysisOutputKind))
  title: Mapped[t.Optional[t.Any]] = mapped_column(JSON, default=None)
  description: Mapped[t.Optional[t.Any]] = mapped_column(JSON, default=None)
  params: Mapped[list[dict[str, t.Any]]] = mapped_column(JSON, default=list)
  storage_filename: Mapped[t.Optional[str]] = mapped_column(default=None)
  original_filename: Mapped[t.Optional[str]] = mapped_column(default=None)
  md5_hash: Mapped[t.Optional[str]] = mapped_column(default=None)
  size_bytes: Mapped[t.Optional[int]] = mapped_column(default=None)
  logical_key: Mapped[t.Optional[str]] = mapped_column(default=None)
  version: Mapped[int] = mapped_column(default=1)
  is_native: Mapped[bool] = mapped_column(default=False)
  created_at: Mapped[str]

class StoredFileRecord(Base):
  """Versioned catalog of files copied into the application data directory."""

  __tablename__ = "stored_files"
  __table_args__ = (
    UniqueConstraint("logical_key", "version", name="uq_stored_file_key_version"),
  )

  id: Mapped[int] = mapped_column(primary_key=True)
  logical_key: Mapped[str]
  version: Mapped[int]
  storage_filename: Mapped[str]
  original_filename: Mapped[str]
  md5_hash: Mapped[str]
  size_bytes: Mapped[int]
  scope: Mapped[str]
  created_at: Mapped[str]
