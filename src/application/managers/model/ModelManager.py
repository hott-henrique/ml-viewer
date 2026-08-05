import importlib
import importlib.util
import sys
import typing as t
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from application.db.database import SessionLocal
from application.db.models import Model as ModelRow
from application.db.paths import get_models_dir
from application.db.storage import FileStore
from application.enums import ParamType, ProblemType
from application.i18n import TranslatableStr, _
from application.managers.model.base import ModelAPI
from application.managers.model.definitions import (
  CLASSIFICATION_REGISTRY,
  CLUSTERING_REGISTRY,
  DIMENSIONALITY_REGISTRY,
  REGRETION_REGISTRY,
)

class HyperParamConfig(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True)

  name: str
  label: TranslatableStr
  type: ParamType
  default: t.Any = None
  options: list[t.Any] = Field(default_factory=list)
  description: TranslatableStr = ""

  field_validation: t.Optional[t.Callable[[t.Any, dict], t.Optional[str]]] = None

class ModelConfig(BaseModel):
  model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

  class_name: str = Field(..., alias="class")
  type: ProblemType
  title: t.Optional[TranslatableStr] = None
  description: TranslatableStr = ""
  params: list[HyperParamConfig] = Field(default_factory=list)
  module: t.Optional[str] = None
  custom_module: t.Optional[t.Any] = None
  plugin_path: t.Optional[str] = None
  is_native: bool = False

MODELS_DIR = get_models_dir()

NATIVE_MODEL_REGISTRIES: dict[ProblemType, dict[str, dict[str, t.Any]]] = {
  ProblemType.CLASSIFICATION: CLASSIFICATION_REGISTRY,
  ProblemType.REGRESSION: REGRETION_REGISTRY,
  ProblemType.CLUSTERING: CLUSTERING_REGISTRY,
  ProblemType.DIMENSIONALITY_REDUCTION: DIMENSIONALITY_REGISTRY,
}

class ModelManager:
  BASE_MODEL_REGISTRY: dict[ProblemType, dict[str, ModelConfig]] = {}

  @staticmethod
  def registry(problem_type: ProblemType) -> dict[str, ModelConfig]:
    return ModelManager.BASE_MODEL_REGISTRY.get(problem_type, {})

  @staticmethod
  def options(problem_type: ProblemType) -> list[str]:
    return list(ModelManager.registry(problem_type).keys())

  @staticmethod
  def instantiate(problem_type: ProblemType, name: str, params: dict[str, t.Any]) -> ModelAPI:
    registry = ModelManager.registry(problem_type)

    if name not in registry:
      raise ValueError(f'Model not found in registry: {name}')

    config = registry[name]

    if config.module:
      module = importlib.import_module(config.module)
      model_class = getattr(module, config.class_name)
    elif config.custom_module:
      model_class = getattr(config.custom_module, config.class_name)
    else:
      raise ValueError(f"Configuration for '{name}' must have either 'module' or be a local class.")

    return model_class(**params)

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
  def _seed_native_models(cls, session: Session) -> None:
    """Populates the `models` table from the hardcoded native registries, once, on first boot."""
    has_any_model = session.scalar(select(ModelRow.id).limit(1)) is not None

    if has_any_model:
      return

    for prob_type, raw_registry in NATIVE_MODEL_REGISTRIES.items():
      for name, data in raw_registry.items():
        try:
          config = ModelConfig.model_validate({**data, "type": data.get("type", prob_type)})
        except Exception as e:
          print(f"Warning: Native model '{name}' failed validation: {e}")
          continue

        session.add(ModelRow(
          name=name,
          problem_type=prob_type,
          class_name=config.class_name,
          module=config.module,
          title=config.title,
          description=config.description,
          params=[p.model_dump(mode="json") for p in config.params],
          is_native=True,
          created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))

    session.commit()

  @classmethod
  def _register_row_in_memory(cls, row: ModelRow) -> None:
    custom_module: t.Optional[t.Any] = None
    plugin_path: t.Optional[str] = None

    if not row.is_native:
      store = FileStore(MODELS_DIR)

      if not row.storage_filename or not row.md5_hash or not store.verify_integrity(row.storage_filename, row.md5_hash):
        print(f"Warning: Plugin model '{row.name}' failed integrity check, skipping.")
        return

      plugin_path = str(store.resolve_path(row.storage_filename))
      custom_module = cls._load_module_from_path(plugin_path)

    title: t.Optional[TranslatableStr] = row.title
    description: TranslatableStr = row.description or ""
    params = [HyperParamConfig.model_validate(p) for p in row.params]

    if row.is_native:
      native_data = NATIVE_MODEL_REGISTRIES.get(row.problem_type, {}).get(row.name)

      if native_data is not None:
        title = native_data.get("title", title)
        description = native_data.get("description", description)
        params = [HyperParamConfig.model_validate(p) for p in native_data.get("params", [])]

    config = ModelConfig(
      class_name=row.class_name,
      type=row.problem_type,
      title=title,
      description=description,
      params=params,
      module=row.module,
      custom_module=custom_module,
      plugin_path=plugin_path,
      is_native=row.is_native,
    )

    cls.BASE_MODEL_REGISTRY.setdefault(row.problem_type, {})[row.name] = config

  @classmethod
  def boot_models(cls) -> None:
    cls.BASE_MODEL_REGISTRY = {}

    with SessionLocal() as session:
      cls._seed_native_models(session)

      rows = session.scalars(select(ModelRow)).all()

      for row in rows:
        cls._register_row_in_memory(row)

  @classmethod
  def import_from_file(cls, filepath: str) -> list[str]:
    store = FileStore(MODELS_DIR)
    stored = store.save(Path(filepath))
    destination = str(store.resolve_path(stored.storage_filename))

    try:
      module = cls._load_module_from_path(destination)

      if not hasattr(module, 'MODEL_CONFIG'):
        raise ValueError("The imported file must contain a 'MODEL_CONFIG' dictionary.")

      custom_config: dict[str, dict[str, t.Any]] = getattr(module, 'MODEL_CONFIG')

      if not isinstance(custom_config, dict):
        raise ValueError("'MODEL_CONFIG' must be a dictionary.")
    except Exception:
      store.delete(stored.storage_filename)
      raise

    added_models: list[str] = []

    with SessionLocal() as session:
      for model_name, model_data in custom_config.items():
        try:
          config = ModelConfig.model_validate(model_data)

          session.add(ModelRow(
            name=model_name,
            problem_type=config.type,
            class_name=config.class_name,
            module=None,
            title=config.title,
            description=config.description,
            params=[p.model_dump(mode="json") for p in config.params],
            storage_filename=stored.storage_filename,
            original_filename=stored.original_filename,
            md5_hash=stored.md5_hash,
            size_bytes=stored.size_bytes,
            is_native=False,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          ))

          added_models.append(model_name)
        except Exception as e:
          print(f"Warning: Custom plugin '{model_name}' rejected due to validation error: {e}")

      session.commit()

    cls.boot_models()

    return added_models

  @classmethod
  def delete_model(cls, problem_type: ProblemType, name: str) -> None:
    with SessionLocal() as session:
      row = session.scalar(
        select(ModelRow).where(ModelRow.problem_type == problem_type, ModelRow.name == name)
      )

      if row is None:
        return

      if row.is_native:
        raise ValueError(_("model.err.native_cannot_delete"))

      storage_filename = row.storage_filename

      session.delete(row)
      session.commit()

    if storage_filename:
      FileStore(MODELS_DIR).delete(storage_filename)

    cls.boot_models()

ModelManager.boot_models()
