import typing as t

from matplotlib.figure import Figure
from sklearn.metrics import (
  ConfusionMatrixDisplay,
  accuracy_score,
  classification_report,
  mean_squared_error,
  r2_score,
)

from application.enums import AnalysisOutputKind, ProblemType
from application.managers.results.base import ExportResult, ImageResult, ResultAnalyzer, ScalarResult, TextResult

class AccuracyAnalysis(ResultAnalyzer):
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    return ScalarResult("accuracy.json", float(accuracy_score(y_true, y_pred)), label="Accuracy")

class ClassificationReportAnalysis(ResultAnalyzer):
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    report = classification_report(y_true, y_pred, zero_division=0)
    return TextResult("classification_report.txt", f"Classification Report:\n{report}")

class ConfusionMatrixAnalysis(ResultAnalyzer):
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ConfusionMatrixDisplay.from_predictions(y_true, y_pred, ax=ax, cmap="Blues")
    ax.set_title("Confusion Matrix")
    fig.tight_layout()
    return ImageResult("confusion_matrix.png", fig)

class MseAnalysis(ResultAnalyzer):
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    return ScalarResult("mse.json", float(mean_squared_error(y_true, y_pred)), label="Mean Squared Error")

class R2Analysis(ResultAnalyzer):
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    return ScalarResult("r2.json", float(r2_score(y_true, y_pred)), label="R2 Score")

class ActualVsPredictedAnalysis(ResultAnalyzer):
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.scatter(y_true, y_pred, alpha=0.7, edgecolors="k", color="#0984e3")
    ax.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], "r--", lw=2)
    ax.set_xlabel("Actual Values")
    ax.set_ylabel("Predicted Values")
    ax.set_title("Actual vs Predicted")
    fig.tight_layout()
    return ImageResult("actual_vs_predicted.png", fig)

NATIVE_ANALYSIS_REGISTRY: dict[ProblemType, dict[str, dict[str, t.Any]]] = {
  ProblemType.CLASSIFICATION: {
    "Accuracy": {
      "type": ProblemType.CLASSIFICATION,
      "class": "AccuracyAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "description": "Overall classification accuracy (fraction of correct predictions).",
    },
    "Classification Report": {
      "type": ProblemType.CLASSIFICATION,
      "class": "ClassificationReportAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.TEXT,
      "description": "Precision, recall, F1 and support per class.",
    },
    "Confusion Matrix": {
      "type": ProblemType.CLASSIFICATION,
      "class": "ConfusionMatrixAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.IMAGE,
      "description": "Confusion matrix heatmap of true vs predicted labels.",
    },
  },
  ProblemType.REGRESSION: {
    "MSE": {
      "type": ProblemType.REGRESSION,
      "class": "MseAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "description": "Mean squared error between actual and predicted values.",
    },
    "R2 Score": {
      "type": ProblemType.REGRESSION,
      "class": "R2Analysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "description": "Coefficient of determination (R²).",
    },
    "Actual vs Predicted": {
      "type": ProblemType.REGRESSION,
      "class": "ActualVsPredictedAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.IMAGE,
      "description": "Scatter plot of actual versus predicted values.",
    },
  },
}
