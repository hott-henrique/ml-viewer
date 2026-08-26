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

from application.enums import AnalysisOutputKind, ParamType, ProblemType
from application.managers.results.base import (
  AssociationRulesAnalyzer,
  ClusteringAnalyzer,
  DimensionalityReductionAnalyzer,
  ExportResult,
  ImageResult,
  ScalarResult,
  SupervisedAnalyzer,
  TextResult,
  ReinforcementLearningAnalyzer,
)

# --- Supervised ---

class AccuracyAnalysis(SupervisedAnalyzer):
  def __init__(self, **params: t.Any) -> None:
    pass

  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    return ScalarResult("accuracy.json", float(accuracy_score(y_true, y_pred)), label="Accuracy")

class ClassificationReportAnalysis(SupervisedAnalyzer):
  def __init__(self, digits: int = 2, zero_division: int = 0, **params: t.Any) -> None:
    self.digits = int(digits)
    self.zero_division = int(zero_division)

  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    report = classification_report(
      y_true,
      y_pred,
      digits=self.digits,
      zero_division=self.zero_division,
    )
    return TextResult("classification_report.txt", report, label="Classification Report")

class ConfusionMatrixAnalysis(SupervisedAnalyzer):
  def __init__(self, cmap: str = "Blues", normalize: str = "none", **params: t.Any) -> None:
    self.cmap = cmap
    self.normalize = None if normalize == "none" else normalize

  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ConfusionMatrixDisplay.from_predictions(
      y_true,
      y_pred,
      ax=ax,
      cmap=self.cmap,
      normalize=self.normalize,
    )
    ax.set_title("Confusion Matrix")
    fig.tight_layout()
    return ImageResult("confusion_matrix.png", fig, label="Confusion Matrix")

class MseAnalysis(SupervisedAnalyzer):
  def __init__(self, squared: bool = True, **params: t.Any) -> None:
    self.squared = bool(squared)

  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    value = float(mean_squared_error(y_true, y_pred))

    if not self.squared:
      value = float(np.sqrt(value))

    label = "Mean Squared Error" if self.squared else "Root Mean Squared Error"
    return ScalarResult("mse.json", value, label=label)

class R2Analysis(SupervisedAnalyzer):
  def __init__(self, **params: t.Any) -> None:
    pass

  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    return ScalarResult("r2.json", float(r2_score(y_true, y_pred)), label="R2 Score")

class ActualVsPredictedAnalysis(SupervisedAnalyzer):
  def __init__(self, alpha: float = 0.7, **params: t.Any) -> None:
    self.alpha = float(alpha)

  def analyze(self, y_true: t.Any, y_pred: t.Any) -> ExportResult:
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.scatter(y_true, y_pred, alpha=self.alpha, edgecolors="k", color="#0984e3")
    ax.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], "r--", lw=2)
    ax.set_xlabel("Actual Values")
    ax.set_ylabel("Predicted Values")
    ax.set_title("Actual vs Predicted")
    fig.tight_layout()
    return ImageResult("actual_vs_predicted.png", fig, label="Actual vs Predicted")

# --- Clustering ---

class SilhouetteScoreAnalysis(ClusteringAnalyzer):
  def __init__(self, metric: str = "euclidean", **params: t.Any) -> None:
    self.metric = metric

  def analyze(self, X: t.Any, labels: t.Any) -> ExportResult:
    unique = np.unique(labels)

    if len(unique) < 2:
      raise ValueError("Silhouette score requires at least 2 clusters.")

    return ScalarResult(
      "silhouette_score.json",
      float(silhouette_score(X, labels, metric=self.metric)),
      label="Silhouette Score",
    )

class DaviesBouldinAnalysis(ClusteringAnalyzer):
  def __init__(self, **params: t.Any) -> None:
    pass

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
  def __init__(self, **params: t.Any) -> None:
    pass

  def analyze(self, X: t.Any, labels: t.Any) -> ExportResult:
    unique, counts = np.unique(labels, return_counts=True)
    lines = [f"Cluster {label}: {count} samples" for label, count in zip(unique, counts)]
    content = f"Total samples: {len(labels)}\nClusters: {len(unique)}\n\n" + "\n".join(lines)
    return TextResult("cluster_sizes.txt", content, label="Cluster Sizes")

class Clusters2DScatterAnalysis(ClusteringAnalyzer):
  def __init__(self, random_state: int = 42, **params: t.Any) -> None:
    self.random_state = int(random_state)

  def analyze(self, X: t.Any, labels: t.Any) -> ExportResult:
    X_arr = np.asarray(X)

    if X_arr.ndim != 2:
      raise ValueError("X must be a 2D feature matrix.")

    if X_arr.shape[1] > 2:
      coords = PCA(n_components=2, random_state=self.random_state).fit_transform(X_arr)
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
    return ImageResult("clusters_2d.png", fig, label="Clusters 2D Scatter")

# --- Dimensionality Reduction ---

class ExplainedVarianceRatioAnalysis(DimensionalityReductionAnalyzer):
  def __init__(self, **params: t.Any) -> None:
    pass

  def analyze(self, X: t.Any, embedding: t.Any, model: t.Any = None) -> ExportResult:
    if model is None or not hasattr(model, "explained_variance_ratio_"):
      raise ValueError("Explained variance requires a fitted model with explained_variance_ratio_.")

    total = float(np.sum(model.explained_variance_ratio_))
    return ScalarResult("explained_variance_ratio.json", total, label="Explained Variance Ratio (sum)")

class EmbeddingScatterAnalysis(DimensionalityReductionAnalyzer):
  def __init__(self, x_component: int = 0, y_component: int = 1, **params: t.Any) -> None:
    self.x_component = int(x_component)
    self.y_component = int(y_component)

  def analyze(self, X: t.Any, embedding: t.Any, model: t.Any = None) -> ExportResult:
    emb = np.asarray(embedding)

    if emb.ndim != 2 or emb.shape[1] < 1:
      raise ValueError("Embedding must be a 2D matrix with at least one component.")

    if self.x_component < 0 or self.x_component >= emb.shape[1]:
      raise ValueError(f"x_component {self.x_component} is out of range for {emb.shape[1]} components.")

    x = emb[:, self.x_component]

    if self.y_component < 0 or self.y_component >= emb.shape[1]:
      y = np.zeros(len(emb))
      ylabel = "(padded)"
    else:
      y = emb[:, self.y_component]
      ylabel = f"Component {self.y_component + 1}"

    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.scatter(x, y, alpha=0.7, edgecolors="k", color="#0984e3")
    ax.set_xlabel(f"Component {self.x_component + 1}")
    ax.set_ylabel(ylabel)
    ax.set_title("Embedding Scatter")
    fig.tight_layout()
    return ImageResult("embedding_scatter.png", fig, label="Embedding Scatter")

class ComponentSummaryAnalysis(DimensionalityReductionAnalyzer):
  def __init__(self, **params: t.Any) -> None:
    pass

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

    return TextResult("component_summary.txt", "\n".join(lines), label="Component Summary")

# --- Association Rules ---

def _format_itemset(value: t.Any) -> str:
  if value is None:
    return ""

  if isinstance(value, (set, frozenset, list, tuple)):
    return "{" + ", ".join(sorted(str(item) for item in value)) + "}"

  return str(value)

class RuleCountAnalysis(AssociationRulesAnalyzer):
  def __init__(self, **params: t.Any) -> None:
    pass

  def analyze(self, model: t.Any, X: t.Any = None) -> ExportResult:
    if not hasattr(model, "get_rules"):
      raise ValueError("Rule count requires a fitted association-rules model with get_rules().")

    rules = model.get_rules()
    count = int(len(rules))
    return ScalarResult("rule_count.json", count, label="Rule Count")

class FrequentItemsetsAnalysis(AssociationRulesAnalyzer):
  def __init__(self, **params: t.Any) -> None:
    pass

  def analyze(self, model: t.Any, X: t.Any = None) -> ExportResult:
    if not hasattr(model, "get_frequent_itemsets"):
      raise ValueError("Frequent itemsets require a fitted model with get_frequent_itemsets().")

    itemsets = model.get_frequent_itemsets()

    if hasattr(itemsets, "empty") and itemsets.empty:
      content = "No frequent itemsets found."
    elif hasattr(itemsets, "iterrows"):
      lines = ["itemset\tsupport"]
      for _, row in itemsets.iterrows():
        itemset = row["itemsets"] if "itemsets" in row.index else row.iloc[0]
        support = row["support"] if "support" in row.index else row.iloc[1]
        lines.append(f"{_format_itemset(itemset)}\t{float(support):.4f}")
      content = "\n".join(lines)
    else:
      content = str(itemsets)

    return TextResult("frequent_itemsets.txt", content, label="Frequent Itemsets")

class AssociationRulesTableAnalysis(AssociationRulesAnalyzer):
  def __init__(self, sort_by: str = "lift", **params: t.Any) -> None:
    self.sort_by = sort_by

  def analyze(self, model: t.Any, X: t.Any = None) -> ExportResult:
    if not hasattr(model, "get_rules"):
      raise ValueError("Association rules require a fitted model with get_rules().")

    rules = model.get_rules()

    if hasattr(rules, "empty") and rules.empty:
      content = "No association rules found."
    elif hasattr(rules, "iterrows"):
      ordered = rules
      if self.sort_by in getattr(rules, "columns", []):
        ordered = rules.sort_values(self.sort_by, ascending=False)

      lines = ["antecedents\tconsequents\tsupport\tconfidence\tlift"]
      for _, row in ordered.iterrows():
        antecedents = row["antecedents"] if "antecedents" in row.index else ""
        consequents = row["consequents"] if "consequents" in row.index else ""
        support = float(row["support"]) if "support" in row.index else float("nan")
        confidence = float(row["confidence"]) if "confidence" in row.index else float("nan")
        lift = float(row["lift"]) if "lift" in row.index else float("nan")
        lines.append(
          f"{_format_itemset(antecedents)}\t{_format_itemset(consequents)}\t"
          f"{support:.4f}\t{confidence:.4f}\t{lift:.4f}"
        )
      content = "\n".join(lines)
    else:
      content = str(rules)

    return TextResult("association_rules.txt", content, label="Association Rules")


# --- Reinforcement Learning ---

class MeanReturnAnalysis(ReinforcementLearningAnalyzer):
  def __init__(self, **params: t.Any) -> None:
    pass

  def analyze(self, agent: t.Any, train_result: t.Any) -> ExportResult:
    returns = list(getattr(train_result, "episode_returns", []) or [])
    if not returns:
      raise ValueError("Mean return requires non-empty episode_returns.")
    mean_val = float(np.mean(returns))
    return ScalarResult("mean_return.json", mean_val, label="Mean Return")


class ReturnCurveAnalysis(ReinforcementLearningAnalyzer):
  def __init__(self, **params: t.Any) -> None:
    pass

  def analyze(self, agent: t.Any, train_result: t.Any) -> ExportResult:
    returns = list(getattr(train_result, "episode_returns", []) or [])
    if not returns:
      raise ValueError("Return curve requires non-empty episode_returns.")

    fig = Figure(figsize=(6, 4), dpi=120)
    ax = fig.add_subplot(111)
    ax.plot(range(1, len(returns) + 1), returns, linewidth=1.2)
    ax.set_xlabel("Episode")
    ax.set_ylabel("Return")
    ax.set_title("Episode Return Curve")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return ImageResult("return_curve.png", fig, label="Return Curve")


class QTableSummaryAnalysis(ReinforcementLearningAnalyzer):
  def __init__(self, max_states: int = 20, **params: t.Any) -> None:
    self.max_states = int(max_states)

  def analyze(self, agent: t.Any, train_result: t.Any) -> ExportResult:
    if not hasattr(agent, "get_q_table"):
      raise ValueError("Q-table summary requires an agent with get_q_table().")

    q_table = agent.get_q_table()
    lines = [f"Q-table states: {len(q_table)}", ""]
    for i, (state, actions) in enumerate(q_table.items()):
      if i >= self.max_states:
        lines.append(f"... ({len(q_table) - self.max_states} more states)")
        break
      best_action = max(actions, key=actions.get) if actions else None
      best_value = actions.get(best_action, 0.0) if best_action is not None else 0.0
      lines.append(f"state={state!r} best_action={best_action!r} Q={best_value:.4f} (|A|={len(actions)})")

    return TextResult("q_table_summary.txt", "\n".join(lines), label="Q-Table Summary")


# --- Registry ---

_P = ParamType

NATIVE_ANALYSIS_REGISTRY: dict[ProblemType, dict[str, dict[str, t.Any]]] = {
  ProblemType.CLASSIFICATION: {
    "Accuracy": {
      "type": ProblemType.CLASSIFICATION,
      "class": "AccuracyAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "title": {"en_US": "Accuracy", "pt_BR": "Acurácia"},
      "description": {
        "en_US": "Overall classification accuracy (fraction of correct predictions).",
        "pt_BR": "Acurácia geral da classificação (fração de previsões corretas).",
      },
      "params": [],
    },
    "Classification Report": {
      "type": ProblemType.CLASSIFICATION,
      "class": "ClassificationReportAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.TEXT,
      "title": {"en_US": "Classification Report", "pt_BR": "Relatório de Classificação"},
      "description": {
        "en_US": "Precision, recall, F1 and support per class.",
        "pt_BR": "Precisão, recall, F1 e suporte por classe.",
      },
      "params": [
        {
          "name": "digits",
          "type": _P.INT,
          "default": 2,
          "label": {"en_US": "Decimal digits", "pt_BR": "Casas decimais"},
          "description": {
            "en_US": "Number of decimal digits for floating-point values in the report.",
            "pt_BR": "Número de casas decimais nos valores do relatório.",
          },
        },
        {
          "name": "zero_division",
          "type": _P.CATEGORICAL,
          "options": ["0", "1"],
          "default": "0",
          "label": {"en_US": "Zero division", "pt_BR": "Divisão por zero"},
          "description": {
            "en_US": "Value to return when there is a zero division (e.g. no predicted samples).",
            "pt_BR": "Valor retornado quando há divisão por zero (ex.: nenhuma previsão da classe).",
          },
        },
      ],
    },
    "Confusion Matrix": {
      "type": ProblemType.CLASSIFICATION,
      "class": "ConfusionMatrixAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.IMAGE,
      "title": {"en_US": "Confusion Matrix", "pt_BR": "Matriz de Confusão"},
      "description": {
        "en_US": "Confusion matrix heatmap of true vs predicted labels.",
        "pt_BR": "Mapa de calor da matriz de confusão entre rótulos reais e previstos.",
      },
      "params": [
        {
          "name": "cmap",
          "type": _P.CATEGORICAL,
          "options": ["Blues", "Viridis", "Oranges", "Greens", "Purples"],
          "default": "Blues",
          "label": {"en_US": "Colormap", "pt_BR": "Mapa de cores"},
          "description": {
            "en_US": "Matplotlib colormap used for the heatmap.",
            "pt_BR": "Mapa de cores do Matplotlib usado no heatmap.",
          },
        },
        {
          "name": "normalize",
          "type": _P.CATEGORICAL,
          "options": ["none", "true", "pred", "all"],
          "default": "none",
          "label": {"en_US": "Normalize", "pt_BR": "Normalizar"},
          "description": {
            "en_US": "Normalize matrix by true labels, predictions, all, or leave as counts.",
            "pt_BR": "Normalizar pela verdade, previsões, tudo, ou manter contagens.",
          },
        },
      ],
    },
  },
  ProblemType.REGRESSION: {
    "MSE": {
      "type": ProblemType.REGRESSION,
      "class": "MseAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "title": {"en_US": "MSE", "pt_BR": "MSE"},
      "description": {
        "en_US": "Mean squared error between actual and predicted values.",
        "pt_BR": "Erro quadrático médio entre valores reais e previstos.",
      },
      "params": [
        {
          "name": "squared",
          "type": _P.BOOL,
          "default": True,
          "label": {"en_US": "Squared (MSE)", "pt_BR": "Ao quadrado (MSE)"},
          "description": {
            "en_US": "If True, report MSE; if False, report RMSE.",
            "pt_BR": "Se verdadeiro, reporta MSE; se falso, reporta RMSE.",
          },
        },
      ],
    },
    "R2 Score": {
      "type": ProblemType.REGRESSION,
      "class": "R2Analysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "title": {"en_US": "R2 Score", "pt_BR": "Coeficiente R²"},
      "description": {
        "en_US": "Coefficient of determination (R²).",
        "pt_BR": "Coeficiente de determinação (R²).",
      },
      "params": [],
    },
    "Actual vs Predicted": {
      "type": ProblemType.REGRESSION,
      "class": "ActualVsPredictedAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.IMAGE,
      "title": {"en_US": "Actual vs Predicted", "pt_BR": "Real vs Previsto"},
      "description": {
        "en_US": "Scatter plot of actual versus predicted values.",
        "pt_BR": "Gráfico de dispersão entre valores reais e previstos.",
      },
      "params": [
        {
          "name": "alpha",
          "type": _P.FLOAT,
          "default": 0.7,
          "label": {"en_US": "Point opacity", "pt_BR": "Opacidade dos pontos"},
          "description": {
            "en_US": "Alpha transparency of scatter points (0–1).",
            "pt_BR": "Transparência alfa dos pontos (0–1).",
          },
        },
      ],
    },
  },
  ProblemType.CLUSTERING: {
    "Silhouette Score": {
      "type": ProblemType.CLUSTERING,
      "class": "SilhouetteScoreAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "title": {"en_US": "Silhouette Score", "pt_BR": "Coeficiente de Silhueta"},
      "description": {
        "en_US": "Mean silhouette coefficient of all samples (higher is better).",
        "pt_BR": "Coeficiente médio de silhueta de todas as amostras (quanto maior, melhor).",
      },
      "params": [
        {
          "name": "metric",
          "type": _P.CATEGORICAL,
          "options": ["euclidean", "cosine", "manhattan"],
          "default": "euclidean",
          "label": {"en_US": "Distance metric", "pt_BR": "Métrica de distância"},
          "description": {
            "en_US": "Distance metric passed to silhouette_score.",
            "pt_BR": "Métrica de distância passada ao silhouette_score.",
          },
        },
      ],
    },
    "Davies-Bouldin Index": {
      "type": ProblemType.CLUSTERING,
      "class": "DaviesBouldinAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "title": {"en_US": "Davies-Bouldin Index", "pt_BR": "Índice de Davies-Bouldin"},
      "description": {
        "en_US": "Average similarity between clusters (lower is better).",
        "pt_BR": "Similaridade média entre clusters (quanto menor, melhor).",
      },
      "params": [],
    },
    "Cluster Sizes": {
      "type": ProblemType.CLUSTERING,
      "class": "ClusterSizesAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.TEXT,
      "title": {"en_US": "Cluster Sizes", "pt_BR": "Tamanhos dos Clusters"},
      "description": {
        "en_US": "Number of samples assigned to each cluster.",
        "pt_BR": "Número de amostras atribuídas a cada cluster.",
      },
      "params": [],
    },
    "Clusters 2D Scatter": {
      "type": ProblemType.CLUSTERING,
      "class": "Clusters2DScatterAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.IMAGE,
      "title": {"en_US": "Clusters 2D Scatter", "pt_BR": "Dispersão 2D dos Clusters"},
      "description": {
        "en_US": "2D scatter of clusters (PCA projection when needed).",
        "pt_BR": "Dispersão 2D dos clusters (projeção PCA quando necessário).",
      },
      "params": [
        {
          "name": "random_state",
          "type": _P.INT,
          "default": 42,
          "label": {"en_US": "PCA random state", "pt_BR": "Semente aleatória do PCA"},
          "description": {
            "en_US": "Random seed used when projecting with PCA.",
            "pt_BR": "Semente aleatória usada na projeção com PCA.",
          },
        },
      ],
    },
  },
  ProblemType.DIMENSIONALITY_REDUCTION: {
    "Explained Variance Ratio": {
      "type": ProblemType.DIMENSIONALITY_REDUCTION,
      "class": "ExplainedVarianceRatioAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "title": {"en_US": "Explained Variance Ratio", "pt_BR": "Razão de Variância Explicada"},
      "description": {
        "en_US": "Sum of explained variance ratios of retained components.",
        "pt_BR": "Soma das razões de variância explicada dos componentes retidos.",
      },
      "params": [],
    },
    "Embedding Scatter": {
      "type": ProblemType.DIMENSIONALITY_REDUCTION,
      "class": "EmbeddingScatterAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.IMAGE,
      "title": {"en_US": "Embedding Scatter", "pt_BR": "Dispersão do Embedding"},
      "description": {
        "en_US": "Scatter of selected embedding components.",
        "pt_BR": "Dispersão dos componentes selecionados do embedding.",
      },
      "params": [
        {
          "name": "x_component",
          "type": _P.INT,
          "default": 0,
          "label": {"en_US": "X component index", "pt_BR": "Índice do componente X"},
          "description": {
            "en_US": "Zero-based index of the component used on the X axis.",
            "pt_BR": "Índice (base 0) do componente usado no eixo X.",
          },
        },
        {
          "name": "y_component",
          "type": _P.INT,
          "default": 1,
          "label": {"en_US": "Y component index", "pt_BR": "Índice do componente Y"},
          "description": {
            "en_US": "Zero-based index of the component used on the Y axis.",
            "pt_BR": "Índice (base 0) do componente usado no eixo Y.",
          },
        },
      ],
    },
    "Component Summary": {
      "type": ProblemType.DIMENSIONALITY_REDUCTION,
      "class": "ComponentSummaryAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.TEXT,
      "title": {"en_US": "Component Summary", "pt_BR": "Resumo dos Componentes"},
      "description": {
        "en_US": "Embedding shape and per-component explained variance when available.",
        "pt_BR": "Formato do embedding e variância explicada por componente, quando disponível.",
      },
      "params": [],
    },
  },
  ProblemType.ASSOCIATION_RULES: {
    "Rule Count": {
      "type": ProblemType.ASSOCIATION_RULES,
      "class": "RuleCountAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "title": {"en_US": "Rule Count", "pt_BR": "Contagem de Regras"},
      "description": {
        "en_US": "Number of association rules produced by the fitted model.",
        "pt_BR": "Número de regras de associação produzidas pelo modelo ajustado.",
      },
      "params": [],
    },
    "Frequent Itemsets": {
      "type": ProblemType.ASSOCIATION_RULES,
      "class": "FrequentItemsetsAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.TEXT,
      "title": {"en_US": "Frequent Itemsets", "pt_BR": "Itemsets Frequentes"},
      "description": {
        "en_US": "Frequent itemsets with support values.",
        "pt_BR": "Itemsets frequentes com valores de suporte.",
      },
      "params": [],
    },
    "Association Rules": {
      "type": ProblemType.ASSOCIATION_RULES,
      "class": "AssociationRulesTableAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.TEXT,
      "title": {"en_US": "Association Rules", "pt_BR": "Regras de Associação"},
      "description": {
        "en_US": "Association rules with support, confidence and lift.",
        "pt_BR": "Regras de associação com suporte, confiança e lift.",
      },
      "params": [
        {
          "name": "sort_by",
          "type": _P.CATEGORICAL,
          "options": ["lift", "confidence", "support"],
          "default": "lift",
          "label": {"en_US": "Sort by", "pt_BR": "Ordenar por"},
          "description": {
            "en_US": "Metric used to sort rules in the report.",
            "pt_BR": "Métrica usada para ordenar as regras no relatório.",
          },
        },
      ],
    },
  },
  ProblemType.REINFORCEMENT_LEARNING: {
    "Mean Return": {
      "type": ProblemType.REINFORCEMENT_LEARNING,
      "class": "MeanReturnAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.SCALAR,
      "title": {"en_US": "Mean Return", "pt_BR": "Retorno Médio"},
      "description": {
        "en_US": "Average episode return over training.",
        "pt_BR": "Retorno médio por episódio ao longo do treino.",
      },
      "params": [],
    },
    "Return Curve": {
      "type": ProblemType.REINFORCEMENT_LEARNING,
      "class": "ReturnCurveAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.IMAGE,
      "title": {"en_US": "Return Curve", "pt_BR": "Curva de Retorno"},
      "description": {
        "en_US": "Plot of episode return versus episode index.",
        "pt_BR": "Gráfico do retorno por episódio.",
      },
      "params": [],
    },
    "Q-Table Summary": {
      "type": ProblemType.REINFORCEMENT_LEARNING,
      "class": "QTableSummaryAnalysis",
      "module": "application.managers.analysis.natives",
      "output_kind": AnalysisOutputKind.TEXT,
      "title": {"en_US": "Q-Table Summary", "pt_BR": "Resumo da Q-Table"},
      "description": {
        "en_US": "Summary of learned Q-values (requires Q-Learning).",
        "pt_BR": "Resumo dos valores Q aprendidos (requer Q-Learning).",
      },
      "params": [
        {
          "name": "max_states",
          "type": _P.INT,
          "default": 20,
          "label": {"en_US": "Max States", "pt_BR": "Máx. estados"},
          "description": {
            "en_US": "Maximum number of states to list in the summary.",
            "pt_BR": "Número máximo de estados a listar no resumo.",
          },
        },
      ],
    },
  },
}
