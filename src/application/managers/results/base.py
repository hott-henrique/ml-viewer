import io
import json
import zipfile
import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

from matplotlib import image as mpimg
from matplotlib.figure import Figure

ScalarValue = int | float | bool

class ExportResult(ABC):
  """Base abstraction for a single piece of analysis output that knows how to include itself in an export ZIP."""

  def __init__(self, name: str) -> None:
    self.name = name

  @abstractmethod
  def include_in_zip(self, zf: zipfile.ZipFile) -> None:
    ...

class TextResult(ExportResult):
  def __init__(self, name: str, content: str) -> None:
    super().__init__(name)
    self.content = content

  def include_in_zip(self, zf: zipfile.ZipFile) -> None:
    zf.writestr(self.name, self.content)

class ScalarResult(ExportResult):
  def __init__(self, name: str, value: ScalarValue, label: str) -> None:
    super().__init__(name)
    self.value = value
    self.label = label

  def to_json(self) -> str:
    return json.dumps({"label": self.label, "value": self.value}, indent=2)

  @classmethod
  def from_json(cls, name: str, content: str) -> "ScalarResult":
    data = json.loads(content)
    return cls(name=name, value=data["value"], label=data["label"])

  def include_in_zip(self, zf: zipfile.ZipFile) -> None:
    zf.writestr(self.name, self.to_json())

class ImageResult(ExportResult):
  def __init__(self, name: str, figure: Figure) -> None:
    super().__init__(name)
    self.figure = figure

  def include_in_zip(self, zf: zipfile.ZipFile) -> None:
    buf = io.BytesIO()
    self.figure.savefig(buf, format="png", dpi=150)
    zf.writestr(self.name, buf.getvalue())

class StoredImageResult(ExportResult):
  """Disk-backed image result loaded from a persisted PNG file."""

  def __init__(self, name: str, path: Path) -> None:
    super().__init__(name)
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
  """Analyzer for supervised (classification/regression) problems: analyze(y_true, y_pred)."""

  @abstractmethod
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    ...

class ClusteringAnalyzer(ResultAnalyzer):
  """Analyzer for clustering problems: analyze(X, labels)."""

  @abstractmethod
  def analyze(self, X: t.Any, labels: t.Any) -> ExportResult:
    ...

class DimensionalityReductionAnalyzer(ResultAnalyzer):
  """Analyzer for dimensionality reduction problems: analyze(X, embedding, model=None)."""

  @abstractmethod
  def analyze(self, X: t.Any, embedding: t.Any, model: t.Any = None) -> ExportResult:
    ...
