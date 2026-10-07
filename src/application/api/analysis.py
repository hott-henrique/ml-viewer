"""Analysis plugin bases: inherit one analyzer ABC and return an ExportResult."""

from __future__ import annotations

import io
import json
import typing as t
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path

from matplotlib import image as mpimg
from matplotlib.figure import Figure

ScalarValue = int | float | bool


def fallback_result_label(name: str) -> str:
  """Humanize a result filename when no label was persisted (e.g. confusion_matrix.png → Confusion Matrix)."""
  return Path(name).stem.replace("_", " ").title()


class ExportResult(ABC):
  """Single analysis output that knows how to include itself in an export ZIP."""

  def __init__(self, name: str, label: str) -> None:
    self.name = name
    self.label = label

  @abstractmethod
  def include_in_zip(self, zf: zipfile.ZipFile) -> None:
    ...


class TextResult(ExportResult):
  def __init__(self, name: str, content: str, label: str) -> None:
    super().__init__(name, label)
    self.content = content

  def include_in_zip(self, zf: zipfile.ZipFile) -> None:
    zf.writestr(self.name, self.content)


class ScalarResult(ExportResult):
  def __init__(self, name: str, value: ScalarValue, label: str) -> None:
    super().__init__(name, label)
    self.value = value

  def to_json(self) -> str:
    return json.dumps({"label": self.label, "value": self.value}, indent=2)

  @classmethod
  def from_json(cls, name: str, content: str) -> "ScalarResult":
    data = json.loads(content)
    return cls(name=name, value=data["value"], label=data["label"])

  def include_in_zip(self, zf: zipfile.ZipFile) -> None:
    zf.writestr(self.name, self.to_json())

  @property
  def metric_id(self) -> str:
    """Stable metric id (analysis key), not the on-disk filename."""
    return Path(self.name).stem


def write_metrics_json(zf: zipfile.ZipFile, scalars: list[ScalarResult]) -> None:
  """Write all scalar metrics into a single metrics.json entry in the ZIP."""
  if not scalars:
    return
  payload = {
    "metrics": [
      {"id": s.metric_id, "label": s.label, "value": s.value}
      for s in scalars
    ]
  }
  zf.writestr("metrics.json", json.dumps(payload, indent=2))


class ImageResult(ExportResult):
  def __init__(self, name: str, figure: Figure, label: str) -> None:
    super().__init__(name, label)
    self.figure = figure

  def include_in_zip(self, zf: zipfile.ZipFile) -> None:
    buf = io.BytesIO()
    self.figure.savefig(buf, format="png", dpi=150)
    zf.writestr(self.name, buf.getvalue())


class StoredImageResult(ExportResult):
  """Disk-backed image result loaded from a persisted PNG file."""

  def __init__(self, name: str, path: Path, label: str) -> None:
    super().__init__(name, label)
    self.path = path

  @property
  def figure(self) -> Figure:
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.imshow(mpimg.imread(self.path))
    ax.axis("off")
    fig.tight_layout()
    return fig

  def include_in_zip(self, zf: zipfile.ZipFile) -> None:
    zf.write(self.path, self.name)


class ResultAnalyzer(ABC):
  """Atomic analysis that produces exactly one typed ExportResult."""

  @abstractmethod
  def analyze(self, *args: t.Any, **kwargs: t.Any) -> ExportResult:
    ...


class SupervisedAnalyzer(ResultAnalyzer):
  """Analyzer for supervised problems: analyze(y_true, y_pred)."""

  @abstractmethod
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    ...


class ClusteringAnalyzer(ResultAnalyzer):
  """Analyzer for clustering: analyze(X, labels)."""

  @abstractmethod
  def analyze(self, X: t.Any, labels: t.Any) -> ExportResult:
    ...


class DimensionalityReductionAnalyzer(ResultAnalyzer):
  """Analyzer for dimensionality reduction: analyze(X, embedding, model=None)."""

  @abstractmethod
  def analyze(self, X: t.Any, embedding: t.Any, model: t.Any = None) -> ExportResult:
    ...


class AssociationRulesAnalyzer(ResultAnalyzer):
  """Analyzer for association rules: analyze(model, X=None)."""

  @abstractmethod
  def analyze(self, model: t.Any, X: t.Any = None) -> ExportResult:
    ...


class ReinforcementLearningAnalyzer(ResultAnalyzer):
  """Analyzer for RL: analyze(agent, train_result)."""

  @abstractmethod
  def analyze(self, agent: t.Any, train_result: t.Any) -> ExportResult:
    ...
