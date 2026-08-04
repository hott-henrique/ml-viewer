import typing as t

from matplotlib.figure import Figure
from sklearn.metrics import (
  ConfusionMatrixDisplay,
  accuracy_score,
  classification_report,
  mean_squared_error,
  r2_score,
)

from application.managers.results.base import ExportResult, ImageResult, ResultAnalyzer, TextResult

class ClassificationAnalyzer(ResultAnalyzer):
  def __init__(self, target_col: str) -> None:
    self.target_col = target_col

  def analyze(self, y_true: t.Any, y_pred: t.Any) -> list[ExportResult]:
    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, zero_division=0)

    content = (
      f"Target Column: {self.target_col}\nTest Size: 20%\n\n"
      f"Accuracy: {acc:.4f}\n\nClassification Report:\n{report}"
    )

    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)

    ConfusionMatrixDisplay.from_predictions(y_true, y_pred, ax=ax, cmap="Blues")
    ax.set_title("Confusion Matrix")

    fig.tight_layout()

    return [
      TextResult("metrics.txt", content),
      ImageResult("confusion_matrix.png", fig),
    ]

class RegressionAnalyzer(ResultAnalyzer):
  def __init__(self, target_col: str) -> None:
    self.target_col = target_col

  def analyze(self, y_true: t.Any, y_pred: t.Any) -> list[ExportResult]:
    mse = mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    content = (
      f"Target Column: {self.target_col}\nTest Size: 20%\n\n"
      f"Mean Squared Error (MSE): {mse:.4f}\nR2 Score: {r2:.4f}"
    )

    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)

    ax.scatter(y_true, y_pred, alpha=0.7, edgecolors="k", color="#0984e3")
    ax.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
    ax.set_xlabel("Actual Values")
    ax.set_ylabel("Predicted Values")
    ax.set_title("Actual vs Predicted")

    fig.tight_layout()

    return [
      TextResult("metrics.txt", content),
      ImageResult("actual_vs_predicted.png", fig),
    ]
