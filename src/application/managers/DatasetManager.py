import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_FILE = os.path.join(BASE_DIR, "datasets_metadata.json")

class DatasetManager:

  @classmethod
  def get_all(cls) -> list[dict]:

    if os.path.exists(DATASETS_FILE):
      with open(DATASETS_FILE, "r", encoding="utf-8") as f:
        try:
          return json.load(f)
        except json.JSONDecodeError:
          return []

    return []

  @classmethod
  def add_dataset(cls, name: str, filepath: str, problem_type: str, target: str) -> dict:
    datasets = cls.get_all()

    new_dataset = {
      "id": str(len(datasets) + 1),
      "name": name,
      "path": filepath,
      "type": problem_type,
      "target": target,
      "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    datasets.append(new_dataset)

    with open(DATASETS_FILE, "w", encoding="utf-8") as f:
      json.dump(datasets, f, indent=4)

    return new_dataset

  @classmethod
  def update_dataset(cls, payload: dict) -> dict:
    datasets = cls.get_all()
    target_id = str(payload.get("id"))
    updated = False
    updated_dataset = None
    
    for ds in datasets:
      if str(ds.get("id")) == target_id:
        ds["name"] = payload.get("name", ds["name"])
        ds["path"] = payload.get("path", ds["path"])
        ds["type"] = payload.get("type", ds["type"])
        ds["target"] = payload.get("target", ds.get("target", ""))

        updated_dataset = ds
        updated = True

        break

    if not updated:
      raise ValueError(f"Dataset com ID {target_id} não encontrado.")

    with open(DATASETS_FILE, "w", encoding="utf-8") as f:
      json.dump(datasets, f, indent=4)

    return updated_dataset
  
  @classmethod
  def delete_dataset(cls, target_id: str):
    datasets = cls.get_all()
    
    updated_datasets = [ds for ds in datasets if str(ds.get("id")) != str(target_id)]
    
    with open(DATASETS_FILE, "w", encoding="utf-8") as f:
        json.dump(updated_datasets, f, indent=4)
