import io
import zipfile
import typing as t
from abc import ABC, abstractmethod

from matplotlib.figure import Figure

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

class ImageResult(ExportResult):
  def __init__(self, name: str, figure: Figure) -> None:
    super().__init__(name)
    self.figure = figure

  def include_in_zip(self, zf: zipfile.ZipFile) -> None:
    buf = io.BytesIO()
    self.figure.savefig(buf, format="png", dpi=150)
    zf.writestr(self.name, buf.getvalue())

class ResultAnalyzer(ABC):
  """Base abstraction for a metric/analysis that produces one or more ExportResults."""

  @abstractmethod
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> list[ExportResult]:
    ...
