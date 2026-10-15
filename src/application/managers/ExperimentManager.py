import pickle
import shutil
import tempfile
import typing as t
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from application.db.database import SessionLocal
from application.db.models import Dataset as DatasetRow
from application.db.models import Experiment as ExperimentRow
from application.db.models import Model as ModelRow
from application.db.paths import get_experiment_dir, get_experiments_dir
from application.db.storage import FileIntegrityError, FileStore, SavedFile, save_file
from application.enums import ExperimentStatus, ProblemType
from application.i18n import _, display_title
from application.managers.DatasetManager import DatasetMetadata
from application.managers.environment import TrainConfig
from application.managers.model.base import ModelAPI
from application.managers.results import (
  ExportResult,
  ImageResult,
  ScalarResult,
  StoredImageResult,
  TextResult,
  fallback_result_label,
)

HyperParamValue = int | float | bool | str | dict[str, t.Any] | list[dict[str, t.Any]]

ArtifactKind = t.Literal["log", "text", "image", "scalar"]

class AnalysisRunSpec(BaseModel):
  name: str
  label: str
  params: dict[str, HyperParamValue] = Field(default_factory=dict)

class ExperimentTrainConfig(BaseModel):
  """Persisted RL training config (maps to TrainingRunner TrainConfig)."""

  version: t.Literal[1] = 1
  n_episodes: int = 500
  seed: t.Optional[int] = 42
  watch_during: bool = True
  watch_last_episodes: int = 5
  watch_delay_ms: int = 100

  @field_validator("n_episodes")
  @classmethod
  def _validate_n_episodes(cls, value: int) -> int:
    if value < 1:
      raise ValueError(_("experiment.err.invalid_n_episodes"))
    return value

  @field_validator("watch_last_episodes")
  @classmethod
  def _validate_watch_last(cls, value: int) -> int:
    if value < 0:
      raise ValueError(_("experiment.err.invalid_watch_last_episodes"))
    return value

  @field_validator("watch_delay_ms")
  @classmethod
  def _validate_watch_delay(cls, value: int) -> int:
    if value < 0:
      raise ValueError(_("experiment.err.invalid_watch_delay_ms"))
    return value

  def to_runner_config(self) -> TrainConfig:
    return TrainConfig(
      n_episodes=self.n_episodes,
      seed=self.seed,
      watch_during=self.watch_during,
      watch_last_episodes=self.watch_last_episodes,
      watch_delay_ms=self.watch_delay_ms,
    )

class ResultArtifact(BaseModel):
  name: str
  kind: ArtifactKind
  storage_filename: str
  md5_hash: str
  label: t.Optional[str] = None
  logical_key: t.Optional[str] = None
  version: t.Optional[int] = None

class ExperimentMetadata(BaseModel):
  id: int
  name: str
  dataset: t.Optional[DatasetMetadata] = None
  environment_kind: t.Optional[str] = None
  environment_params: dict[str, HyperParamValue] = Field(default_factory=dict)
  dataset_name: str
  problem_type: ProblemType
  model_name: str
  model_version: int = 1
  hyperparameters: dict[str, HyperParamValue]
  status: ExperimentStatus
  date: str
  analyses: list[AnalysisRunSpec] = Field(default_factory=list)
  result_artifacts: list[ResultArtifact] = Field(default_factory=list)
  train_config: t.Optional[ExperimentTrainConfig] = None
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
    # Lazy import avoids circular import with EnvironmentManager boot.
    from application.managers.environment import EnvironmentManager

    dataset = DatasetMetadata.from_row(row.dataset) if row.dataset is not None else None
    environment_kind = row.environment_kind
    environment_params = dict(row.environment_params or {})

    if dataset is not None and environment_kind is not None:
      raise ValueError(_("experiment.err.dataset_and_environment"))
    if dataset is None and not environment_kind:
      raise ValueError(_("experiment.err.missing_dataset_or_environment"))

    if dataset is not None:
      problem_type = dataset.type
      source_name = dataset.name
    else:
      assert environment_kind is not None
      problem_type = ProblemType.REINFORCEMENT_LEARNING
      try:
        config = EnvironmentManager.kind_config(environment_kind)
        source_name = display_title(config.title, environment_kind)
      except Exception:
        source_name = environment_kind

    train_config = None
    if row.train_config:
      train_config = ExperimentTrainConfig.model_validate(row.train_config)

    return cls(
      id=row.id,
      name=row.name,
      dataset=dataset,
      environment_kind=environment_kind,
      environment_params=environment_params,
      dataset_name=source_name,
      problem_type=problem_type,
      model_name=row.model_name,
      model_version=row.model_version,
      hyperparameters=row.hyperparameters,
      status=row.status,
      date=row.created_at,
      analyses=[AnalysisRunSpec.model_validate(a) for a in (row.analyses or [])],
      result_artifacts=[ResultArtifact.model_validate(a) for a in (row.result_artifacts or [])],
      train_config=train_config,
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
  def add_experiment(
    cls,
    name: str,
    model_name: str,
    hyperparams: dict[str, HyperParamValue],
    status: ExperimentStatus = ExperimentStatus.PENDING,
    analyses: t.Optional[list[AnalysisRunSpec | dict[str, t.Any]]] = None,
    train_config: t.Optional[ExperimentTrainConfig | dict[str, t.Any]] = None,
    dataset: t.Optional[DatasetMetadata] = None,
    environment_kind: t.Optional[str] = None,
    environment_params: t.Optional[dict[str, HyperParamValue]] = None,
  ) -> ExperimentMetadata:
    if (dataset is None) == (not environment_kind):
      raise ValueError(_("experiment.err.exactly_one_source"))

    from application.managers.environment import EnvironmentManager

    with SessionLocal() as session:
      if dataset is not None and session.get(DatasetRow, dataset.id) is None:
        raise ValueError(_("dataset.err.not_found").format(id=dataset.id))

    if environment_kind is not None:
      EnvironmentManager.kind_config(environment_kind)

    parsed_train: t.Optional[dict[str, t.Any]] = None
    if train_config is not None:
      if isinstance(train_config, ExperimentTrainConfig):
        parsed_train = train_config.model_dump(mode="json")
      else:
        parsed_train = ExperimentTrainConfig.model_validate(train_config).model_dump(mode="json")

    parsed_analyses = [
      AnalysisRunSpec.model_validate(a).model_dump(mode="json")
      for a in (analyses or [])
    ]

    problem_type = dataset.type if dataset is not None else ProblemType.REINFORCEMENT_LEARNING

    with SessionLocal() as session:
      current_model_version = session.scalar(
        select(func.max(ModelRow.version)).where(
          ModelRow.name == model_name,
          ModelRow.problem_type == problem_type,
        )
      )
      row = ExperimentRow(
        name=name,
        dataset_id=dataset.id if dataset is not None else None,
        environment_kind=environment_kind,
        environment_params=dict(environment_params or {}) if environment_kind else None,
        model_name=model_name,
        model_version=1 if current_model_version is None else int(current_model_version),
        hyperparameters=hyperparams,
        status=status,
        analyses=parsed_analyses,
        result_artifacts=[],
        train_config=parsed_train,
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

      for field in ("name", "model_name", "hyperparameters", "status", "analyses"):
        value = updates.get(field)

        if value is not None:
          if field == "analyses":
            value = [
              AnalysisRunSpec.model_validate(a).model_dump(mode="json")
              for a in value
            ]
          setattr(row, field, value)

      session.commit()

      row = session.scalars(BASE_QUERY.where(ExperimentRow.id == target_id)).one()

      return ExperimentMetadata.from_row(row)

  @classmethod
  def _store_text_file(cls, exp_id: int, name: str, content: str) -> SavedFile:
    with tempfile.NamedTemporaryFile(suffix=Path(name).suffix or ".txt", delete=False, mode="w", encoding="utf-8") as tmp_file:
      tmp_file.write(content)
      tmp_path = Path(tmp_file.name)

    try:
      return save_file(tmp_path, scope=f"experiments/{exp_id}")
    finally:
      tmp_path.unlink(missing_ok=True)

  @classmethod
  def _store_image_result(cls, exp_id: int, image: ImageResult) -> SavedFile:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
      tmp_path = Path(tmp_file.name)

    try:
      image.figure.savefig(tmp_path, format="png", dpi=150)
      return save_file(tmp_path, scope=f"experiments/{exp_id}")
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
    stored = cls._store_text_file(exp_id, "logs.txt", content)

    return cls._append_artifacts(exp_id, [ResultArtifact(
      name="logs.txt",
      kind="log",
      storage_filename=stored.storage_filename,
      md5_hash=stored.md5_hash,
      logical_key=stored.key,
      version=stored.version,
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
    artifacts: list[ResultArtifact] = []

    for result in results:
      if isinstance(result, TextResult):
        stored = cls._store_text_file(exp_id, result.name, result.content)
        artifacts.append(ResultArtifact(
          name=result.name,
          kind="text",
          storage_filename=stored.storage_filename,
          md5_hash=stored.md5_hash,
          label=result.label,
          logical_key=stored.key,
          version=stored.version,
        ))
      elif isinstance(result, ScalarResult):
        stored = cls._store_text_file(exp_id, result.name, result.to_json())
        artifacts.append(ResultArtifact(
          name=result.name,
          kind="scalar",
          storage_filename=stored.storage_filename,
          md5_hash=stored.md5_hash,
          label=result.label,
          logical_key=stored.key,
          version=stored.version,
        ))
      elif isinstance(result, ImageResult):
        stored = cls._store_image_result(exp_id, result)
        artifacts.append(ResultArtifact(
          name=result.name,
          kind="image",
          storage_filename=stored.storage_filename,
          md5_hash=stored.md5_hash,
          label=result.label,
          logical_key=stored.key,
          version=stored.version,
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
    with SessionLocal() as session:
      existing = session.get(ExperimentRow, exp_id)
      existing_key = existing.model_pickle_key if existing is not None else None

    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp_file:
      pickle.dump(trained_model, tmp_file)
      tmp_path = Path(tmp_file.name)

    try:
      stored = save_file(tmp_path, key=existing_key, scope=f"experiments/{exp_id}")
    finally:
      tmp_path.unlink(missing_ok=True)

    with SessionLocal() as session:
      row = session.get(ExperimentRow, exp_id)

      if row is None:
        raise ValueError(_("experiment.err.not_found").format(id=exp_id))

      row.model_pickle_filename = stored.storage_filename
      row.model_pickle_md5 = stored.md5_hash
      row.model_pickle_size = stored.size_bytes
      row.model_pickle_key = stored.key

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
