import typing as t

from matplotlib.figure import Figure
from sklearn.decomposition import PCA
from sklearn.metrics import (
  ConfusionMatrixDisplay,
  accuracy_score,
  classification_report,
  davies_bouldin_score,
  mean_squared_error,
  r2_score,
  silhouette_score,
)
import numpy as np

from application.enums import AnalysisOutputKind, ProblemType
from application.managers.results.base import (
  ClusteringAnalyzer,
  DimensionalityReductionAnalyzer,
  ExportResult,
  ImageResult,
  ScalarResult,
  SupervisedAnalyzer,
  TextResult,
)

# --- Supervised ---

class AccuracyAnalysis(SupervisedAnalyzer):
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    return ScalarResult("accuracy.json", float(accuracy_score(y_true, y_pred)), label="Accuracy")

class ClassificationReportAnalysis(SupervisedAnalyzer):
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    report = classification_report(y_true, y_pred, zero_division=0)
    return TextResult("classification_report.txt", f"Classification Report:\n{report}")

class ConfusionMatrixAnalysis(SupervisedAnalyzer):
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ConfusionMatrixDisplay.from_predictions(y_true, y_pred, ax=ax, cmap="Blues")
    ax.set_title("Confusion Matrix")
    fig.tight_layout()
    return ImageResult("confusion_matrix.png", fig)

class MseAnalysis(SupervisedAnalyzer):
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    return ScalarResult("mse.json", float(mean_squared_error(y_true, y_pred)), label="Mean Squared Error")

class R2Analysis(SupervisedAnalyzer):
  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    return ScalarResult("r2.json", float(r2_score(y_true, y_pred)), label="R2 Score")

class ActualVsPredictedAnalysis(SupervisedAnalyzer):
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

# --- Clustering ---

class SilhouetteScoreAnalysis(ClusteringAnalyzer):
  def analyze(self, X: t.Any, labels: t.Any) -> ExportResult:
    unique = np.unique(labels)

    if len(unique) < 2:
      raise ValueError("Silhouette score requires at least 2 clusters.")

    return ScalarResult(
      "silhouette_score.json",
      float(silhouette_score(X, labels)),
      label="Silhouette Score",
    )

class DaviesBouldinAnalysis(ClusteringAnalyzer):
  def analyze(self, X: t.Any, labels: t.Any) -> ExportResult:
    unique = np.unique(labels)

    if len(unique) < 2:
      raise ValueError("Davies-Bouldin score requires at least 2 clusters.")

    return ScalarResult(
      "davies_bouldin.json",
      float(davies_bouldin_score(X, labels)),
      label="Davies-Bouldin Index",
    )

class ClusterSizesAnalysis(ClusteringAnalyzer):
  def analyze(self, X: t.Any, labels: t.Any) -> ExportResult:
    unique, counts = np.unique(labels, return_counts=True)
    lines = [f"Cluster {label}: {count} samples" for label, count in zip(unique, counts)]
    content = f"Total samples: {len(labels)}\nClusters: {len(unique)}\n\n" + "\n".join(lines)
    return TextResult("cluster_sizes.txt", content)

class Clusters2DScatterAnalysis(ClusteringAnalyzer):
  def analyze(self, X: t.Any, labels: t.Any) -> ExportResult:
    X_arr = np.asarray(X)

    if X_arr.ndim != 2:
      raise ValueError("X must be a 2D feature matrix.")

    if X_arr.shape[1] > 2:
      coords = PCA(n_components=2, random_state=42).fit_transform(X_arr)
      xlabel, ylabel = "PC1", "PC2"
    else:
      coords = X_arr[:, :2] if X_arr.shape[1] == 2 else np.column_stack([X_arr[:, 0], np.zeros(len(X_arr))])
      xlabel, ylabel = "Feature 1", "Feature 2"

    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    scatter = ax.scatter(coords[:, 0], coords[:, 1], c=labels, cmap="tab10", alpha=0.8, edgecolors="k")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title("Clusters (2D)")
    fig.colorbar(scatter, ax=ax, label="Cluster")
    fig.tight_layout()
    return ImageResult("clusters_2d.png", fig)

# --- Dimensionality Reduction ---

class ExplainedVarianceRatioAnalysis(DimensionalityReductionAnalyzer):
  def analyze(self, X: t.Any, embedding: t.Any, model: t.Any = None) -> ExportResult:
    if model is None or not hasattr(model, "explained_variance_ratio_"):
      raise ValueError("Explained variance requires a fitted model with explained_variance_ratio_.")

    total = float(np.sum(model.explained_variance_ratio_))
    return ScalarResult("explained_variance_ratio.json", total, label="Explained Variance Ratio (sum)")

class EmbeddingScatterAnalysis(DimensionalityReductionAnalyzer):
  def analyze(self, X: t.Any, embedding: t.Any, model: t.Any = None) -> ExportResult:
    emb = np.asarray(embedding)

    if emb.ndim != 2 or emb.shape[1] < 1:
      raise ValueError("Embedding must be a 2D matrix with at least one component.")

    x = emb[:, 0]
    y = emb[:, 1] if emb.shape[1] > 1 else np.zeros(len(emb))

    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.scatter(x, y, alpha=0.7, edgecolors="k", color="#0984e3")
    ax.set_xlabel("Component 1")
    ax.set_ylabel("Component 2" if emb.shape[1] > 1 else "(padded)")
    ax.set_title("Embedding Scatter")
    fig.tight_layout()
    return ImageResult("embedding_scatter.png", fig)

class ComponentSummaryAnalysis(DimensionalityReductionAnalyzer):
  def analyze(self, X: t.Any, embedding: t.Any, model: t.Any = None) -> ExportResult:
    emb = np.asarray(embedding)
    lines = [
      f"Original features: {np.asarray(X).shape[1] if np.asarray(X).ndim == 2 else 'n/a'}",
      f"Embedding shape: {emb.shape}",
      f"Components: {emb.shape[1] if emb.ndim == 2 else 'n/a'}",
    ]

    if model is not None and hasattr(model, "explained_variance_ratio_"):
      ratios = model.explained_variance_ratio_
      lines.append("Explained variance per component:")
      for i, ratio in enumerate(ratios):
        lines.append(f"  C{i + 1}: {float(ratio):.4f}")

    return TextResult("component_summary.txt", "\n".join(lines))

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
  ProblemType.CLUSTERING: {
    "Silhouette Score": {
      "type": ProblemType.CLUSTERING,
      "class": "SilhouetteScoreAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "description": "Mean silhouette coefficient of all samples (higher is better).",
    },
    "Davies-Bouldin Index": {
      "type": ProblemType.CLUSTERING,
      "class": "DaviesBouldinAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "description": "Average similarity between clusters (lower is better).",
    },
    "Cluster Sizes": {
      "type": ProblemType.CLUSTERING,
      "class": "ClusterSizesAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.TEXT,
      "description": "Number of samples assigned to each cluster.",
    },
    "Clusters 2D Scatter": {
      "type": ProblemType.CLUSTERING,
      "class": "Clusters2DScatterAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.IMAGE,
      "description": "2D scatter of clusters (PCA projection when needed).",
    },
  },
  ProblemType.DIMENSIONALITY_REDUCTION: {
    "Explained Variance Ratio": {
      "type": ProblemType.DIMENSIONALITY_REDUCTION,
      "class": "ExplainedVarianceRatioAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "description": "Sum of explained variance ratios of retained components.",
    },
    "Embedding Scatter": {
      "type": ProblemType.DIMENSIONALITY_REDUCTION,
      "class": "EmbeddingScatterAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.IMAGE,
      "description": "Scatter of the first two embedding components.",
    },
    "Component Summary": {
      "type": ProblemType.DIMENSIONALITY_REDUCTION,
      "class": "ComponentSummaryAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.TEXT,
      "description": "Embedding shape and per-component explained variance when available.",
    },
  },
}
