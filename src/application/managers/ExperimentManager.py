import pickle
import shutil
import tempfile
import typing as t
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from application.db.database import SessionLocal
from application.db.models import Dataset as DatasetRow
from application.db.models import Experiment as ExperimentRow
from application.db.paths import get_experiment_dir, get_experiments_dir
from application.db.storage import FileIntegrityError, FileStore, StoredFile
from application.enums import ExperimentStatus, ProblemType
from application.i18n import _
from application.managers.DatasetManager import DatasetMetadata
from application.managers.model.base import ModelAPI
from application.managers.results import (
  ExportResult,
  ImageResult,
  ScalarResult,
  StoredImageResult,
  TextResult,
  fallback_result_label,
)

HyperParamValue = int | float | bool | str

ArtifactKind = t.Literal["log", "text", "image", "scalar"]

class ExperimentSplitConfig(BaseModel):
  version: t.Literal[1] = 1
  mode: t.Literal["TrainTest"] = "TrainTest"
  test_size: float = 0.2

  @field_validator("test_size")
  @classmethod
  def _validate_test_size(cls, value: float) -> float:
    if not 0.0 < value < 1.0:
      raise ValueError(_("experiment.err.invalid_test_size"))
    return value

class ResultArtifact(BaseModel):
  name: str
  kind: ArtifactKind
  storage_filename: str
  md5_hash: str
  label: t.Optional[str] = None

class ExperimentMetadata(BaseModel):
  id: int
  name: str
  dataset: DatasetMetadata
  dataset_name: str
  problem_type: ProblemType
  model_name: str
  hyperparameters: dict[str, HyperParamValue]
  status: ExperimentStatus
  date: str
  selected_analyses: list[str] = Field(default_factory=list)
  analysis_params: dict[str, dict[str, HyperParamValue]] = Field(default_factory=dict)
  result_artifacts: list[ResultArtifact] = Field(default_factory=list)
  split_config: t.Optional[ExperimentSplitConfig] = None
  model_pickle_filename: t.Optional[str] = None
  model_pickle_md5: t.Optional[str] = None
  model_pickle_size: t.Optional[int] = None

  @property
  def pickle_path(self) -> t.Optional[str]:
    """Resolves the on-disk location of the trained model pickle for this experiment, verifying its MD5 first.

    Returns None when no pickle has been persisted for this experiment.
    """
    if not self.model_pickle_filename or not self.model_pickle_md5:
      return None

    store = FileStore(get_experiment_dir(self.id))

    if not store.verify_integrity(self.model_pickle_filename, self.model_pickle_md5):
      raise FileIntegrityError(_("experiment.err.model_integrity").format(name=self.name))

    return str(store.resolve_path(self.model_pickle_filename))

  @classmethod
  def from_row(cls, row: ExperimentRow) -> "ExperimentMetadata":
    dataset = DatasetMetadata.from_row(row.dataset)
    split_config = None

    if row.split_config:
      split_config = ExperimentSplitConfig.model_validate(row.split_config)

    return cls(
      id=row.id,
      name=row.name,
      dataset=dataset,
      dataset_name=dataset.name,
      problem_type=dataset.type,
      model_name=row.model_name,
      hyperparameters=row.hyperparameters,
      status=row.status,
      date=row.created_at,
      selected_analyses=list(row.selected_analyses or []),
      analysis_params=dict(row.analysis_params or {}),
      result_artifacts=[ResultArtifact.model_validate(a) for a in (row.result_artifacts or [])],
      split_config=split_config,
      model_pickle_filename=row.model_pickle_filename,
      model_pickle_md5=row.model_pickle_md5,
      model_pickle_size=row.model_pickle_size,
    )

BASE_QUERY = (
  select(ExperimentRow)
  .options(selectinload(ExperimentRow.dataset).selectinload(DatasetRow.files))
)

class ExperimentManager:

  @classmethod
  def get_all(cls) -> list[ExperimentMetadata]:
    with SessionLocal() as session:
      rows = session.scalars(BASE_QUERY.order_by(ExperimentRow.id)).all()

      return [ExperimentMetadata.from_row(row) for row in rows]

  @classmethod
  def add_experiment(cls,
                     name: str,
                     dataset: DatasetMetadata,
                     model_name: str,
                     hyperparams: dict[str, HyperParamValue],
                     status: ExperimentStatus = ExperimentStatus.PENDING,
                     selected_analyses: t.Optional[list[str]] = None,
                     analysis_params: t.Optional[dict[str, dict[str, HyperParamValue]]] = None,
                     split_config: t.Optional[ExperimentSplitConfig | dict[str, t.Any]] = None) -> ExperimentMetadata:
    parsed_split: t.Optional[dict[str, t.Any]] = None

    if split_config is not None:
      if isinstance(split_config, ExperimentSplitConfig):
        parsed_split = split_config.model_dump(mode="json")
      else:
        parsed_split = ExperimentSplitConfig.model_validate(split_config).model_dump(mode="json")

    with SessionLocal() as session:
      row = ExperimentRow(
        name=name,
        dataset_id=dataset.id,
        model_name=model_name,
        hyperparameters=hyperparams,
        status=status,
        selected_analyses=list(selected_analyses or []),
        analysis_params=dict(analysis_params or {}),
        result_artifacts=[],
        split_config=parsed_split,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      )

      session.add(row)
      session.commit()

      row = session.scalars(BASE_QUERY.where(ExperimentRow.id == row.id)).one()

      return ExperimentMetadata.from_row(row)

  @classmethod
  def update_experiment(cls, exp_id: str | int, updates: dict[str, t.Any]) -> ExperimentMetadata:
    target_id = int(exp_id)

    with SessionLocal() as session:
      row = session.get(ExperimentRow, target_id)

      if row is None:
        raise ValueError(_("experiment.err.not_found").format(id=target_id))

      for field in ("name", "model_name", "hyperparameters", "status", "selected_analyses", "analysis_params"):
        value = updates.get(field)

        if value is not None:
          setattr(row, field, value)

      session.commit()

      row = session.scalars(BASE_QUERY.where(ExperimentRow.id == target_id)).one()

      return ExperimentMetadata.from_row(row)

  @classmethod
  def _store_text_file(cls, store: FileStore, name: str, content: str) -> StoredFile:
    with tempfile.NamedTemporaryFile(suffix=Path(name).suffix or ".txt", delete=False, mode="w", encoding="utf-8") as tmp_file:
      tmp_file.write(content)
      tmp_path = Path(tmp_file.name)

    try:
      return store.save(tmp_path)
    finally:
      tmp_path.unlink(missing_ok=True)

  @classmethod
  def _store_image_result(cls, store: FileStore, image: ImageResult) -> StoredFile:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
      tmp_path = Path(tmp_file.name)

    try:
      image.figure.savefig(tmp_path, format="png", dpi=150)
      return store.save(tmp_path)
    finally:
      tmp_path.unlink(missing_ok=True)

  @classmethod
  def _append_artifacts(cls, exp_id: int, new_artifacts: list[ResultArtifact]) -> ExperimentMetadata:
    with SessionLocal() as session:
      row = session.get(ExperimentRow, exp_id)

      if row is None:
        raise ValueError(_("experiment.err.not_found").format(id=exp_id))

      existing = list(row.result_artifacts or [])
      existing.extend(a.model_dump(mode="json") for a in new_artifacts)
      row.result_artifacts = existing

      session.commit()

      row = session.scalars(BASE_QUERY.where(ExperimentRow.id == exp_id)).one()

      return ExperimentMetadata.from_row(row)

  @classmethod
  def save_logs(cls, exp_id: int, content: str) -> ExperimentMetadata:
    """Persists execution logs as a file in the experiment's subfolder."""
    store = FileStore(get_experiment_dir(exp_id))
    stored = cls._store_text_file(store, "logs.txt", content)

    return cls._append_artifacts(exp_id, [ResultArtifact(
      name="logs.txt",
      kind="log",
      storage_filename=stored.storage_filename,
      md5_hash=stored.md5_hash,
    )])

  @classmethod
  def load_logs(cls, exp_id: int) -> str:
    """Loads persisted execution logs for an experiment. Returns empty string when none exist."""
    with SessionLocal() as session:
      row = session.get(ExperimentRow, exp_id)

      if row is None:
        raise ValueError(_("experiment.err.not_found").format(id=exp_id))

      artifacts = [ResultArtifact.model_validate(a) for a in (row.result_artifacts or [])]

    log_artifact = next((a for a in artifacts if a.kind == "log"), None)

    if log_artifact is None:
      return ""

    store = FileStore(get_experiment_dir(exp_id))

    if not store.verify_integrity(log_artifact.storage_filename, log_artifact.md5_hash):
      raise FileIntegrityError(_("experiment.err.logs_integrity").format(id=exp_id))

    return store.resolve_path(log_artifact.storage_filename).read_text(encoding="utf-8")

  @classmethod
  def save_results(cls, exp_id: int, results: list[ExportResult]) -> ExperimentMetadata:
    """Persists analysis results (scalar + text + images) to the experiment's subfolder."""
    store = FileStore(get_experiment_dir(exp_id))
    artifacts: list[ResultArtifact] = []

    for result in results:
      if isinstance(result, TextResult):
        stored = cls._store_text_file(store, result.name, result.content)
        artifacts.append(ResultArtifact(
          name=result.name,
          kind="text",
          storage_filename=stored.storage_filename,
          md5_hash=stored.md5_hash,
          label=result.label,
        ))
      elif isinstance(result, ScalarResult):
        stored = cls._store_text_file(store, result.name, result.to_json())
        artifacts.append(ResultArtifact(
          name=result.name,
          kind="scalar",
          storage_filename=stored.storage_filename,
          md5_hash=stored.md5_hash,
          label=result.label,
        ))
      elif isinstance(result, ImageResult):
        stored = cls._store_image_result(store, result)
        artifacts.append(ResultArtifact(
          name=result.name,
          kind="image",
          storage_filename=stored.storage_filename,
          md5_hash=stored.md5_hash,
          label=result.label,
        ))
      else:
        raise TypeError(f"Unsupported result type for persistence: {type(result)!r}")

    return cls._append_artifacts(exp_id, artifacts)

  @classmethod
  def load_results(cls, exp_id: int) -> list[ExportResult]:
    """Loads persisted analysis results (scalar + text + images) for an experiment."""
    with SessionLocal() as session:
      row = session.get(ExperimentRow, exp_id)

      if row is None:
        raise ValueError(_("experiment.err.not_found").format(id=exp_id))

      artifacts = [ResultArtifact.model_validate(a) for a in (row.result_artifacts or [])]

    store = FileStore(get_experiment_dir(exp_id))
    loaded: list[ExportResult] = []

    for artifact in artifacts:
      if artifact.kind == "log":
        continue

      if not store.verify_integrity(artifact.storage_filename, artifact.md5_hash):
        raise FileIntegrityError(_("experiment.err.artifact_integrity").format(name=artifact.name, id=exp_id))

      path = store.resolve_path(artifact.storage_filename)

      label = artifact.label or fallback_result_label(artifact.name)

      if artifact.kind == "text":
        loaded.append(TextResult(artifact.name, path.read_text(encoding="utf-8"), label=label))
      elif artifact.kind == "scalar":
        scalar = ScalarResult.from_json(artifact.name, path.read_text(encoding="utf-8"))
        if artifact.label:
          scalar.label = artifact.label
        loaded.append(scalar)
      elif artifact.kind == "image":
        loaded.append(StoredImageResult(artifact.name, path, label=label))

    return loaded

  @classmethod
  def save_trained_model(cls, exp_id: int, trained_model: ModelAPI) -> ExperimentMetadata:
    """Persists a trained model's pickle to the experiment's own subfolder and records its metadata."""
    store = FileStore(get_experiment_dir(exp_id))

    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp_file:
      pickle.dump(trained_model, tmp_file)
      tmp_path = Path(tmp_file.name)

    try:
      stored = store.save(tmp_path)
    finally:
      tmp_path.unlink(missing_ok=True)

    with SessionLocal() as session:
      row = session.get(ExperimentRow, exp_id)

      if row is None:
        raise ValueError(_("experiment.err.not_found").format(id=exp_id))

      row.model_pickle_filename = stored.storage_filename
      row.model_pickle_md5 = stored.md5_hash
      row.model_pickle_size = stored.size_bytes

      session.commit()

      row = session.scalars(BASE_QUERY.where(ExperimentRow.id == exp_id)).one()

      return ExperimentMetadata.from_row(row)

  @classmethod
  def delete_experiment(cls, target_id: str | int) -> None:
    exp_id = int(target_id)

    with SessionLocal() as session:
      row = session.get(ExperimentRow, exp_id)

      if row is not None:
        session.delete(row)
        session.commit()

    experiment_dir = get_experiments_dir() / str(exp_id)

    if experiment_dir.exists():
      shutil.rmtree(experiment_dir)
