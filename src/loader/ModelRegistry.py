import importlib
import importlib.util
import typing as t
import shutil
import os
import sys

from loader.definitions import *

class ModelAPI(t.Protocol):
  def fit(self, X: t.Any, y: t.Any, **fit_params: t.Any) -> 'ModelAPI':
    ...

  def predict(self, X: t.Any) -> t.Any:
    ...

  def get_params(self) -> dict:
    ...

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "plugins")

class ModelsRegistry:
  BASE_MODEL_REGISTRY: dict[str, dict] = {
    "Classification": CLASSIFICATION_REGISTRY,
    "Regression": REGRETION_REGISTRY
  }

  @staticmethod
  def registry(problem_type: str) -> dict[str, dict]:
    return ModelsRegistry.BASE_MODEL_REGISTRY.get(problem_type, {})

  @staticmethod
  def options(problem_type: str) -> list[str]:
    return list(ModelsRegistry.registry(problem_type).keys())

  @staticmethod
  def instantiate(problem_type: str, name: str, params: dict) -> ModelAPI:
    registry = ModelsRegistry.registry(problem_type)

    if name not in registry:
      raise ValueError('Model not found in registry.', name)

    config: dict = registry.get(name)

    if 'module' in config:
      module = importlib.import_module(config['module'])
      model_class = getattr(module, config['class'])
    elif 'custom_module' in config:
      model_class = getattr(config['custom_module'], config['class'])
    else:
      raise ValueError(f"Configuration for '{name}' must have either 'module' or be a local class.")

    return model_class(**params)

  @classmethod
  def boot_models(cls):
    if not os.path.exists(MODELS_DIR):
      os.makedirs(MODELS_DIR)
      return
      
    for filename in os.listdir(MODELS_DIR):
      if filename.endswith(".py"):
        filepath = os.path.join(MODELS_DIR, filename)
        try:
          cls._load_file(filepath)
        except Exception as e:
          print(f"Warning: Failed to auto-load model '{filename}': {e}")

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
      raise ValueError("The imported file must contain an 'MODEL_CONFIG' dictionary.")

    custom_config = getattr(module, 'MODEL_CONFIG')

    if not isinstance(custom_config, dict):
      raise ValueError("'MODEL_CONFIG' must be a dictionary.")

    added_models = []

    for model_name, model_data in custom_config.items():
      if 'module' not in model_data:
        model_data['custom_module'] = module

      model_data['plugin_path'] = filepath

      prob_type = model_data.get('type')

      if prob_type not in cls.BASE_MODEL_REGISTRY:
        cls.BASE_MODEL_REGISTRY[prob_type] = {}

      cls.BASE_MODEL_REGISTRY[prob_type][model_name] = model_data

      added_models.append(model_name)

    return added_models

  @classmethod
  def delete_model(cls, problem_type: str, name: str):
    registry = cls.BASE_MODEL_REGISTRY.get(problem_type, {})

    if name not in registry:
      return

    model_data = registry[name]
    filepath = model_data.get('plugin_path')

    del registry[name]

    if filepath and os.path.exists(filepath):
      try:
        os.remove(filepath)
      except Exception as e:
        print(f"Error deleting file {filepath}: {e}")

ModelsRegistry.boot_models()