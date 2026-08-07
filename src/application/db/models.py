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

HyperParamValue = int | float | bool | str

def _str_enum(enum_cls: type) -> SAEnum:
  """Maps a StrEnum to its `.value` (not `.name`) when stored in SQLite."""
  return SAEnum(enum_cls, values_callable=lambda cls: [member.value for member in cls])

class Dataset(Base):
  __tablename__ = "datasets"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str]
  problem_type: Mapped[ProblemType] = mapped_column(_str_enum(ProblemType))
  target: Mapped[t.Optional[int]] = mapped_column(default=None)
  has_header: Mapped[bool] = mapped_column(default=True)
  layout: Mapped[DatasetLayout] = mapped_column(_str_enum(DatasetLayout), default=DatasetLayout.NO_SPLIT)
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

  dataset: Mapped["Dataset"] = relationship(back_populates="files")

class Experiment(Base):
  __tablename__ = "experiments"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str]
  dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id", ondelete="RESTRICT"))
  model_name: Mapped[str]
  hyperparameters: Mapped[dict[str, HyperParamValue]] = mapped_column(JSON)
  status: Mapped[ExperimentStatus] = mapped_column(_str_enum(ExperimentStatus))
  analyses: Mapped[list[dict[str, t.Any]]] = mapped_column(JSON, default=list)
  result_artifacts: Mapped[list[dict[str, t.Any]]] = mapped_column(JSON, default=list)
  split_config: Mapped[t.Optional[dict[str, t.Any]]] = mapped_column(JSON, default=None)
  model_pickle_filename: Mapped[t.Optional[str]] = mapped_column(default=None)
  model_pickle_md5: Mapped[t.Optional[str]] = mapped_column(default=None)
  model_pickle_size: Mapped[t.Optional[int]] = mapped_column(default=None)
  created_at: Mapped[str]

  dataset: Mapped["Dataset"] = relationship(back_populates="experiments")

class Model(Base):
  __tablename__ = "models"

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
  is_native: Mapped[bool] = mapped_column(default=False)
  created_at: Mapped[str]

class Analysis(Base):
  __tablename__ = "analyses"

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
  is_native: Mapped[bool] = mapped_column(default=False)
  created_at: Mapped[str]
