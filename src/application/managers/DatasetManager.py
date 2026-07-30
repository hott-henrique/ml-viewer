import json
import os
from datetime import datetime
from pydantic import BaseModel

from application.enums import ProblemType

class DatasetMetadata(BaseModel):
  id: str
  name: str
  path: str
  type: ProblemType
  target: str
  date: str


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_FILE = os.path.join(BASE_DIR, "datasets_metadata.json")

class DatasetManager:

  @classmethod
  def get_all(cls) -> list[DatasetMetadata]:
    if os.path.exists(DATASETS_FILE):
      with open(DATASETS_FILE, "r", encoding="utf-8") as f:
        try:
          data = json.load(f)
          return [DatasetMetadata.model_validate(ds) for ds in data]
        except (json.JSONDecodeError, ValueError) as e:
          print(f"Warning: Failed to parse datasets JSON: {e}")
          return []

    return []

  @classmethod
  def add_dataset(cls, name: str, filepath: str, problem_type: str | ProblemType, target: str) -> DatasetMetadata:
    datasets = cls.get_all()

    new_dataset = DatasetMetadata(
      id=str(len(datasets) + 1),
      name=name,
      path=filepath,
      type=problem_type,
      target=target,
      date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    datasets.append(new_dataset)

    cls._save_all(datasets)

    return new_dataset

  @classmethod
  def update_dataset(cls, payload: dict) -> DatasetMetadata:
    datasets = cls.get_all()
    target_id = str(payload.get("id"))
    
    for i, ds in enumerate(datasets):
      if ds.id == target_id:
        updates = {k: v for k, v in payload.items() if k in ds.model_fields and v is not None}
        updated_dataset = ds.model_copy(update=updates)
        
        datasets[i] = updated_dataset
        cls._save_all(datasets)
        
        return updated_dataset

    raise ValueError(f"Dataset com ID {target_id} não encontrado.")
  
  @classmethod
  def delete_dataset(cls, target_id: str):
    datasets = cls.get_all()
    
    updated_datasets = [ds for ds in datasets if ds.id != str(target_id)]
    
    cls._save_all(updated_datasets)

  @classmethod
  def _save_all(cls, datasets: list[DatasetMetadata]):
    with open(DATASETS_FILE, "w", encoding="utf-8") as f:
      json.dump([ds.model_dump(mode='json') for ds in datasets], f, indent=4)