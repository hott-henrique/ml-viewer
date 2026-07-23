import importlib
import importlib.util
import typing as t
import shutil
import os
import sys

from pydantic import BaseModel, Field, ConfigDict

from application.managers.model.definitions import CLASSIFICATION_REGISTRY, REGRETION_REGISTRY

class ModelAPI(t.Protocol):
  def fit(self, X: t.Any, y: t.Any, **fit_params: t.Any) -> 'ModelAPI':
    ...

  def predict(self, X: t.Any) -> t.Any:
    ...

  def get_params(self) -> dict:
    ...

class HyperParamConfig(BaseModel):
  name: str
  label: str
  type: str
  default: t.Any = None
  options: list[t.Any] = Field(default_factory=list)
  description: str = ""

class ModelConfig(BaseModel):
  model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

  class_name: str = Field(..., alias="class")
  type: str
  params: list[HyperParamConfig] = Field(default_factory=list)
  module: t.Optional[str] = None
  custom_module: t.Optional[t.Any] = None
  plugin_path: t.Optional[str] = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "plugins")

class ModelManager:
  BASE_MODEL_REGISTRY: dict[str, dict[str, ModelConfig]] = {}

  @staticmethod
  def registry(problem_type: str) -> dict[str, ModelConfig]:
    return ModelManager.BASE_MODEL_REGISTRY.get(problem_type, {})

  @staticmethod
  def options(problem_type: str) -> list[str]:
    return list(ModelManager.registry(problem_type).keys())

  @staticmethod
  def instantiate(problem_type: str, name: str, params: dict) -> ModelAPI:
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

  @classmethod
  def _load_native_registry(cls, prob_type: str, raw_registry: dict):
    if prob_type not in cls.BASE_MODEL_REGISTRY:
      cls.BASE_MODEL_REGISTRY[prob_type] = {}
      
    for name, data in raw_registry.items():
      try:
        if 'type' not in data:
          data['type'] = prob_type

        valid_model = ModelConfig.model_validate(data)

        cls.BASE_MODEL_REGISTRY[prob_type][name] = valid_model
      except Exception as e:
        print(f"Warning: Native model '{name}' failed validation: {e}")

  @classmethod
  def boot_models(cls):
    cls._load_native_registry("Classification", CLASSIFICATION_REGISTRY)
    cls._load_native_registry("Regression", REGRETION_REGISTRY)

    if not os.path.exists(MODELS_DIR):
      os.makedirs(MODELS_DIR)
      return

    for filename in os.listdir(MODELS_DIR):
      if filename.endswith(".py"):
        filepath = os.path.join(MODELS_DIR, filename)
        try:
          cls._load_file(filepath)
        except Exception as e:
          print(f"Warning: Failed to auto-load plugin '{filename}': {e}")

  @classmethod
  def import_from_file(cls, filepath: str):
    if not os.path.exists(MODELS_DIR):
      os.makedirs(MODELS_DIR)

    filename = os.path.basename(filepath)
    destination = os.path.join(MODELS_DIR, filename)

    if os.path.abspath(filepath) != os.path.abspath(destination):
      shutil.copy2(filepath, destination)

    return cls._load_file(destination)

  @classmethod
  def _load_file(cls, filepath: str):
    module_name = os.path.basename(filepath).replace('.py', '')

    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec is None or spec.loader is None:
      raise ImportError(f"Could not load the file: {filepath}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    if not hasattr(module, 'MODEL_CONFIG'):
      raise ValueError("The imported file must contain a 'MODEL_CONFIG' dictionary.")

    custom_config: dict[str, dict] = getattr(module, 'MODEL_CONFIG')

    if not isinstance(custom_config, dict):
      raise ValueError("'MODEL_CONFIG' must be a dictionary.")

    added_models = []

    for model_name, model_data in custom_config.items():
      if 'module' not in model_data:
        model_data['custom_module'] = module

      model_data['plugin_path'] = filepath

      try:
        valid_model = ModelConfig.model_validate(model_data)

        prob_type = valid_model.type

        if prob_type not in cls.BASE_MODEL_REGISTRY:
          cls.BASE_MODEL_REGISTRY[prob_type] = {}

        cls.BASE_MODEL_REGISTRY[prob_type][model_name] = valid_model
        added_models.append(model_name)
      except Exception as e:
        print(f"Warning: Custom plugin '{model_name}' rejected due to validation error: {e}")

    return added_models

  @classmethod
  def delete_model(cls, problem_type: str, name: str):
    registry = cls.BASE_MODEL_REGISTRY.get(problem_type, {})

    if name not in registry:
      return

    model_config = registry[name]

    filepath = model_config.plugin_path

    del registry[name]

    if filepath and os.path.exists(filepath):
      try:
        os.remove(filepath)
      except Exception as e:
        print(f"Error deleting file {filepath}: {e}")

ModelManager.boot_models()