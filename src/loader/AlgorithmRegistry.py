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
PLUGINS_DIR = os.path.join(BASE_DIR, "plugins")

class AlgorithmRegistry:
  BASE_ALGORITHM_REGISTRY: dict[str, dict] = {
    "Classification": CLASSIFICATION_REGISTRY,
    "Regression": REGRETION_REGISTRY
  }

  @staticmethod
  def registry(problem_type: str) -> dict[str, dict]:
    return AlgorithmRegistry.BASE_ALGORITHM_REGISTRY.get(problem_type, {})

  @staticmethod
  def options(problem_type: str) -> list[str]:
    return list(AlgorithmRegistry.registry(problem_type).keys())

  @staticmethod
  def instantiate(problem_type: str, name: str, params: dict) -> ModelAPI:
    registry = AlgorithmRegistry.registry(problem_type)

    if name not in registry:
      raise ValueError('Algorithm not found in registry.', name)

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
  def boot_plugins(cls):
    if not os.path.exists(PLUGINS_DIR):
      os.makedirs(PLUGINS_DIR)
      return
      
    for filename in os.listdir(PLUGINS_DIR):
      if filename.endswith(".py"):
        filepath = os.path.join(PLUGINS_DIR, filename)
        try:
          cls._load_file(filepath)
        except Exception as e:
          print(f"Warning: Failed to auto-load plugin '{filename}': {e}")

  @classmethod
  def import_from_file(cls, filepath: str):
    if not os.path.exists(PLUGINS_DIR):
      os.makedirs(PLUGINS_DIR)

    filename = os.path.basename(filepath)
    destination = os.path.join(PLUGINS_DIR, filename)

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

    if not hasattr(module, 'ALGORITHM_CONFIG'):
      raise ValueError("The imported file must contain an 'ALGORITHM_CONFIG' dictionary.")

    custom_config = getattr(module, 'ALGORITHM_CONFIG')

    if not isinstance(custom_config, dict):
      raise ValueError("'ALGORITHM_CONFIG' must be a dictionary.")

    added_algos = []

    for algo_name, algo_data in custom_config.items():
      if 'module' not in algo_data:
        algo_data['custom_module'] = module

      algo_data['plugin_path'] = filepath

      prob_type = algo_data.get('type')

      if prob_type not in cls.BASE_ALGORITHM_REGISTRY:
        cls.BASE_ALGORITHM_REGISTRY[prob_type] = {}

      cls.BASE_ALGORITHM_REGISTRY[prob_type][algo_name] = algo_data

      added_algos.append(algo_name)

    return added_algos

  @classmethod
  def delete_algorithm(cls, problem_type: str, name: str):
    registry = cls.BASE_ALGORITHM_REGISTRY.get(problem_type, {})

    if name not in registry:
      return

    algo_data = registry[name]
    filepath = algo_data.get('plugin_path')

    del registry[name]

    if filepath and os.path.exists(filepath):
      try:
        os.remove(filepath)
      except Exception as e:
        print(f"Error deleting file {filepath}: {e}")

AlgorithmRegistry.boot_plugins()