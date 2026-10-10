import importlib
import importlib.util
import sys
import typing as t
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from application.db.database import SessionLocal
from application.db.models import Analysis as AnalysisRow
from application.db.paths import get_analyses_dir
from application.db.storage import FileStore, delete_file, save_file_groups
from application.enums import AnalysisOutputKind, ProblemType
from application.i18n import TranslatableStr, _
from application.api.params import HyperParamConfig
from application.api.analysis import (
  AssociationRulesAnalyzer,
  ClusteringAnalyzer,
  DimensionalityReductionAnalyzer,
  ReinforcementLearningAnalyzer,
  ResultAnalyzer,
  SupervisedAnalyzer,
)
from application.managers.analysis.natives import NATIVE_ANALYSIS_REGISTRY

_ANALYZER_BASES = (
  SupervisedAnalyzer,
  ClusteringAnalyzer,
  DimensionalityReductionAnalyzer,
  AssociationRulesAnalyzer,
  ReinforcementLearningAnalyzer,
)

class AnalysisConfig(BaseModel):
  model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

  class_name: str = Field(..., alias="class")
  type: ProblemType
  title: t.Optional[TranslatableStr] = None
  output_kind: AnalysisOutputKind
  description: TranslatableStr = ""
  params: list[HyperParamConfig] = Field(default_factory=list)
  module: t.Optional[str] = None
  custom_module: t.Optional[t.Any] = None
  plugin_path: t.Optional[str] = None
  is_native: bool = False

@dataclass(frozen=True)
class AnalysisVersion:
  id: int
  name: str
  problem_type: ProblemType
  output_kind: AnalysisOutputKind
  version: int
  md5_hash: t.Optional[str]
  is_native: bool
  title: t.Optional[TranslatableStr]
  description: TranslatableStr
  params: list[HyperParamConfig]

ANALYSES_DIR = get_analyses_dir()

class AnalysisManager:
  BASE_ANALYSIS_REGISTRY: dict[ProblemType, dict[str, AnalysisConfig]] = {}

  @staticmethod
  def registry(problem_type: ProblemType | str) -> dict[str, AnalysisConfig]:
    return AnalysisManager.BASE_ANALYSIS_REGISTRY.get(ProblemType(problem_type), {})

  @staticmethod
  def options(problem_type: ProblemType | str) -> list[str]:
    return list(AnalysisManager.registry(problem_type).keys())

  @staticmethod
  def instantiate(
    problem_type: ProblemType | str,
    name: str,
    params: t.Optional[dict[str, t.Any]] = None,
  ) -> ResultAnalyzer:
    registry = AnalysisManager.registry(problem_type)

    if name not in registry:
      raise ValueError(f"Analysis not found in registry: {name}")

    config = registry[name]

    if config.module:
      module = importlib.import_module(config.module)
      analysis_class = getattr(module, config.class_name)
    elif config.custom_module:
      analysis_class = getattr(config.custom_module, config.class_name)
    else:
      raise ValueError(f"Configuration for '{name}' must have either 'module' or be a local class.")

    instance = analysis_class(**(params or {}))

    if not callable(getattr(instance, "analyze", None)):
      raise ValueError(f"Analysis class '{config.class_name}' must implement analyze(...).")

    if not isinstance(instance, _ANALYZER_BASES):
      raise ValueError(
        f"Analysis class '{config.class_name}' must inherit SupervisedAnalyzer, "
        "ClusteringAnalyzer, DimensionalityReductionAnalyzer, AssociationRulesAnalyzer, "
        "or ReinforcementLearningAnalyzer."
      )

    return instance

  @staticmethod
  def _load_module_from_path(filepath: str) -> t.Any:
    module_name = Path(filepath).stem

    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec is None or spec.loader is None:
      raise ImportError(f"Could not load the file: {filepath}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module

  @classmethod
  def _seed_native_analyses(cls, session: Session) -> None:
    has_any = session.scalar(select(AnalysisRow.id).limit(1)) is not None

    if has_any:
      return

    for problem_type, raw_registry in NATIVE_ANALYSIS_REGISTRY.items():
      for name, data in raw_registry.items():
        try:
          config = AnalysisConfig.model_validate({**data, "type": data.get("type", problem_type)})
        except Exception as e:
          print(f"Warning: Native analysis '{name}' failed validation: {e}")
          continue

        session.add(AnalysisRow(
          name=name,
          problem_type=problem_type,
          class_name=config.class_name,
          module=config.module,
          output_kind=config.output_kind,
          title=config.title,
          description=config.description,
          params=[p.model_dump(mode="json") for p in config.params],
          is_native=True,
          version=1,
          created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))

    session.commit()

  @classmethod
  def _register_row_in_memory(cls, row: AnalysisRow) -> None:
    custom_module: t.Optional[t.Any] = None
    plugin_path: t.Optional[str] = None

    if not row.is_native:
      store = FileStore(ANALYSES_DIR)

      if not row.storage_filename or not row.md5_hash or not store.verify_integrity(row.storage_filename, row.md5_hash):
        print(f"Warning: Custom analysis '{row.name}' failed integrity check, skipping.")
        return

      plugin_path = str(store.resolve_path(row.storage_filename))
      custom_module = cls._load_module_from_path(plugin_path)

    title: t.Optional[TranslatableStr] = row.title
    description: TranslatableStr = row.description or ""
    params = [HyperParamConfig.model_validate(p) for p in (row.params or [])]

    if row.is_native:
      native_data = NATIVE_ANALYSIS_REGISTRY.get(row.problem_type, {}).get(row.name)

      if native_data is not None:
        title = native_data.get("title", title)
        description = native_data.get("description", description)
        params = [HyperParamConfig.model_validate(p) for p in native_data.get("params", [])]

    config = AnalysisConfig(
      class_name=row.class_name,
      type=row.problem_type,
      output_kind=row.output_kind,
      title=title,
      description=description,
      params=params,
      module=row.module,
      custom_module=custom_module,
      plugin_path=plugin_path,
      is_native=row.is_native,
    )

    cls.BASE_ANALYSIS_REGISTRY.setdefault(row.problem_type, {})[row.name] = config

  @classmethod
  def boot_analyses(cls) -> None:
    cls.BASE_ANALYSIS_REGISTRY = {}

    with SessionLocal() as session:
      cls._seed_native_analyses(session)

      rows = session.scalars(select(AnalysisRow).order_by(AnalysisRow.version)).all()

      for row in rows:
        cls._register_row_in_memory(row)

  @classmethod
  def list_versions(cls) -> list[AnalysisVersion]:
    with SessionLocal() as session:
      rows = session.scalars(select(AnalysisRow).order_by(AnalysisRow.name, AnalysisRow.version)).all()
      versions: list[AnalysisVersion] = []

      for row in rows:
        title: t.Optional[TranslatableStr] = row.title
        description: TranslatableStr = row.description or ""
        params = [HyperParamConfig.model_validate(p) for p in (row.params or [])]

        if row.is_native:
          native_data = NATIVE_ANALYSIS_REGISTRY.get(row.problem_type, {}).get(row.name)

          if native_data is not None:
            title = native_data.get("title", title)
            description = native_data.get("description", description)
            params = [HyperParamConfig.model_validate(p) for p in native_data.get("params", [])]

        versions.append(AnalysisVersion(
          id=row.id,
          name=row.name,
          problem_type=row.problem_type,
          output_kind=row.output_kind,
          version=row.version,
          md5_hash=row.md5_hash,
          is_native=row.is_native,
          title=title,
          description=description,
          params=params,
        ))

      return versions

  @classmethod
  def import_from_file(cls, filepath: str) -> list[str]:
    module = cls._load_module_from_path(filepath)

    if not hasattr(module, "ANALYSIS_CONFIG"):
      raise ValueError("The imported file must contain an 'ANALYSIS_CONFIG' dictionary.")

    custom_config = getattr(module, "ANALYSIS_CONFIG")

    if not isinstance(custom_config, dict):
      raise ValueError("'ANALYSIS_CONFIG' must be a dictionary.")

    pending: list[tuple[str, AnalysisConfig, int, str | None]] = []

    with SessionLocal() as session:
      for analysis_name, analysis_data in custom_config.items():
        try:
          config = AnalysisConfig.model_validate(analysis_data)
          analysis_class = getattr(module, config.class_name, None)

          if analysis_class is None:
            raise ValueError(f"Class '{config.class_name}' not found in the imported file.")

          if not issubclass(analysis_class, _ANALYZER_BASES):
            raise ValueError(
              f"Class '{config.class_name}' must inherit SupervisedAnalyzer, "
              "ClusteringAnalyzer, DimensionalityReductionAnalyzer, AssociationRulesAnalyzer, "
              "or ReinforcementLearningAnalyzer."
            )

          latest = session.scalar(
            select(AnalysisRow)
            .where(AnalysisRow.name == analysis_name, AnalysisRow.problem_type == config.type)
            .order_by(AnalysisRow.version.desc())
            .limit(1)
          )
          version = 1 if latest is None else latest.version + 1
          previous_key = None if latest is None else latest.logical_key
          pending.append((analysis_name, config, version, previous_key))
        except Exception as e:
          print(f"Warning: Custom analysis '{analysis_name}' rejected due to validation error: {e}")

    if not pending:
      raise ValueError("No analyses were added from the imported file.")

    saved_by_key = save_file_groups(filepath, [item[3] for item in pending], "analyses")
    added: list[str] = []

    with SessionLocal() as session:
      for analysis_name, config, version, previous_key in pending:
        stored = saved_by_key[previous_key]
        session.add(AnalysisRow(
          name=analysis_name,
          problem_type=config.type,
          class_name=config.class_name,
          module=None,
          output_kind=config.output_kind,
          title=config.title,
          description=config.description,
          params=[p.model_dump(mode="json") for p in config.params],
          storage_filename=stored.storage_filename,
          original_filename=stored.original_filename,
          md5_hash=stored.md5_hash,
          size_bytes=stored.size_bytes,
          logical_key=stored.key,
          version=version,
          is_native=False,
          created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        added.append(analysis_name)

      session.commit()

    cls.boot_analyses()

    return added

  @classmethod
  def delete_analysis(cls, analysis_id: int) -> None:
    with SessionLocal() as session:
      row = session.get(AnalysisRow, analysis_id)

      if row is None:
        return

      if row.is_native:
        raise ValueError(_("analysis.err.native_cannot_delete"))

      storage_filename = row.storage_filename
      logical_key = row.logical_key

      session.delete(row)
      session.commit()

      still_used = False

      if logical_key:
        still_used = session.scalar(
          select(AnalysisRow.id).where(AnalysisRow.logical_key == logical_key)
        ) is not None

    if logical_key and not still_used:
      delete_file(logical_key)
    elif storage_filename and not logical_key:
      FileStore(ANALYSES_DIR).delete(storage_filename)

    cls.boot_analyses()

AnalysisManager.boot_analyses()
