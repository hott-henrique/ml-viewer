import typing as t
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from sklearn.model_selection import train_test_split

from application.components import HyperParamForm, SortableTreeview
from application.db.paths import get_experiments_dir
from application.db.storage_usage import dir_size_bytes, format_bytes
from application.enums import DatasetLayout, ExperimentStatus, ProblemType
from application.i18n import _, display_title, localize_enum
from application.managers.DatasetManager import DatasetMetadata, read_dataset_frame
from application.managers.model.base import ModelAPI
from application.managers.results import (
  ClusteringAnalyzer,
  DimensionalityReductionAnalyzer,
  ExportResult,
  ImageResult,
  ScalarResult,
  StoredImageResult,
  SupervisedAnalyzer,
  TextResult,
)
from application.views.experiment import ExperimentFormModal, ExperimentExportModal
from application.views.experiment.ExperimentExportModal import ExperimentExportData
from application.managers import AnalysisManager, ExperimentManager, ModelManager
from application.managers.DatasetManager import SUPERVISED_TYPES
from application.managers.ExperimentManager import ExperimentSplitConfig

class ExperimentView(ttk.Frame):

  def __init__(self, parent: tk.Misc) -> None:
    super().__init__(parent)

    header_frame = ttk.Frame(self)
    header_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(header_frame, text=_("experiment.view.title"), font=("", 16, "bold")).pack(side=tk.LEFT)

    ttk.Button(header_frame, text=_("action.delete"), command=self.delete_experiment).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text=_("action.export"), command=self.export_selected).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text=_("action.view_results"), command=self.view_results).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text=_("action.duplicate"), command=self.duplicate_experiment).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text=_("action.run"), command=self.open_create_modal).pack(side=tk.RIGHT)

    table_frame = ttk.Frame(self)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("id", "name", "dataset", "model", "status", "date", "disk", "disk_bytes")
    self.tree = SortableTreeview(
      table_frame,
      columns=columns,
      display_columns=("name", "dataset", "model", "status", "date", "disk"),
      sort_keys={"disk": "disk_bytes"},
      height=6,
    )

    self.tree.set_heading("id", _("common.id"), sortable=False)
    self.tree.column("id", width=0, stretch=tk.NO)
    self.tree.column("disk_bytes", width=0, stretch=tk.NO)

    self.tree.set_heading("name", _("experiment.col.name"))
    self.tree.set_heading("dataset", _("experiment.col.dataset"))
    self.tree.set_heading("model", _("experiment.col.model"))
    self.tree.set_heading("status", _("common.status"))
    self.tree.set_heading("date", _("experiment.col.created_on"))
    self.tree.set_heading("disk", _("experiment.col.disk"))

    self.tree.column("name", width=140)
    self.tree.column("dataset", width=110)
    self.tree.column("model", width=110)
    self.tree.column("status", width=80)
    self.tree.column("date", width=120)
    self.tree.column("disk", width=80)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.tree.bind("<<TreeviewSelect>>", self.on_experiment_selected)
    self.tree.bind("<Double-1>", self._on_double_click)
    self.tree.bind_context_menu(self._build_context_menu)

    details_frame = ttk.Frame(self)
    details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    details_frame.columnconfigure(0, weight=1)
    details_frame.columnconfigure(1, weight=2)
    details_frame.rowconfigure(0, weight=1)

    param_frame = ttk.LabelFrame(details_frame, text=_("model.hyperparams.readonly"))
    param_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

    self.hyperparam_form = HyperParamForm(param_frame, is_readonly=True)
    self.hyperparam_form.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    logs_frame = ttk.LabelFrame(details_frame, text=_("experiment.logs.title"))
    logs_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

    self.logs_text = tk.Text(logs_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#f5f5f5", height=10)
    self.logs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    self.load_table_data()

  def _get_selected_experiments(self):
    selected_ids = {str(self.tree.item(iid)["values"][0]) for iid in self.tree.selection()}

    if not selected_ids:
      return []

    return [e for e in ExperimentManager.get_all() if str(e.id) in selected_ids]

  def _get_selected_experiment(self):
    experiments = self._get_selected_experiments()

    if len(experiments) != 1:
      return None

    return experiments[0]

  def _build_context_menu(self, event: tk.Event) -> tk.Menu | None:
    if not self.tree.selection():
      return None

    menu = tk.Menu(self, tearoff=0)
    menu.add_command(label=_("experiment.menu.view_results"), command=self.view_results)
    menu.add_command(label=_("common.export"), command=self.export_selected)
    menu.add_command(label=_("experiment.menu.duplicate"), command=self.duplicate_experiment)
    menu.add_separator()
    menu.add_command(label=_("common.delete"), command=self.delete_experiment)
    return menu

  def _on_double_click(self, event: tk.Event) -> None:
    if self.tree.identify_row(event.y):
      self.view_results()

  def _set_logs_panel(self, content: str) -> None:
    self.logs_text.config(state=tk.NORMAL)
    self.logs_text.delete(1.0, tk.END)
    self.logs_text.insert(tk.END, content)
    self.logs_text.config(state=tk.DISABLED)

  def load_table_data(self) -> None:
    for item in self.tree.get_children():
      self.tree.delete(item)

    experiments = ExperimentManager.get_all()

    for exp in experiments:
      status = exp.status
      status_code = {
        ExperimentStatus.PENDING: "experiment.status.pending",
        ExperimentStatus.OK: "experiment.status.ok",
        ExperimentStatus.NOK: "experiment.status.nok",
      }.get(ExperimentStatus(status), "experiment.status.pending")
      status_icon = _(status_code)
      disk_bytes = dir_size_bytes(get_experiments_dir() / str(exp.id))

      model_config = ModelManager.registry(exp.problem_type).get(exp.model_name)
      model_display = display_title(model_config.title, exp.model_name) if model_config else exp.model_name

      self.tree.insert("", tk.END, values=(
        exp.id, exp.name, exp.dataset_name,
        model_display, status_icon, exp.date,
        format_bytes(disk_bytes), disk_bytes,
      ))

  def on_experiment_selected(self, event: t.Optional[tk.Event]) -> None:
    experiment = self._get_selected_experiment()

    if experiment is None:
      return

    model_config = ModelManager.registry(experiment.problem_type).get(experiment.model_name)

    if model_config:
      self.hyperparam_form.render_form(model_config.params)

      for param_name, param_value in experiment.hyperparameters.items():
        if param_name in self.hyperparam_form.param_vars:
          self.hyperparam_form.param_vars[param_name].set(str(param_value))
    else:
      print("Failed to find model to show!")

    try:
      logs = ExperimentManager.load_logs(experiment.id)
    except Exception as e:
      logs = _("experiment.logs.load_failed").format(error=e)

    self._set_logs_panel(logs)

  def open_create_modal(self) -> None:
    ExperimentFormModal(self, on_save=self._on_experiment_saved)

  def _run_analyses(
    self,
    problem_type: ProblemType,
    analysis_names: list[str],
    *,
    analysis_params: t.Optional[dict[str, dict[str, t.Any]]] = None,
    y_true: t.Any = None,
    y_pred: t.Any = None,
    X: t.Any = None,
    labels: t.Any = None,
    embedding: t.Any = None,
    model: t.Any = None,
  ) -> list[ExportResult]:
    results: list[ExportResult] = []
    registry = AnalysisManager.registry(problem_type)
    params_by_name = analysis_params or {}

    for name in analysis_names:
      analyzer = AnalysisManager.instantiate(problem_type, name, params_by_name.get(name))

      if isinstance(analyzer, SupervisedAnalyzer):
        result = analyzer.analyze(y_true, y_pred)
      elif isinstance(analyzer, ClusteringAnalyzer):
        result = analyzer.analyze(X, labels)
      elif isinstance(analyzer, DimensionalityReductionAnalyzer):
        result = analyzer.analyze(X, embedding, model)
      else:
        raise TypeError(f"Unsupported analyzer type: {type(analyzer)!r}")

      config = registry.get(name)
      result.label = display_title(config.title if config else None, name)
      results.append(result)

    return results

  def _features_and_target(self, df: pd.DataFrame, target_idx: int) -> tuple[pd.DataFrame, pd.Series]:
    if target_idx < 0 or target_idx >= df.shape[1]:
      raise ValueError(_("experiment.err.target_index_missing").format(index=target_idx))

    y = df.iloc[:, target_idx]
    X = pd.get_dummies(df.drop(df.columns[target_idx], axis=1))
    return X, y

  def _on_experiment_saved(self, payload: dict[str, t.Any]) -> None:
    self.config(cursor="watch")
    self.update()

    dataset_info: DatasetMetadata = payload["dataset"]
    prob_type = dataset_info.type
    target_idx = dataset_info.target
    selected_analyses: list[str] = list(payload.get("analyses") or [])
    analysis_params: dict[str, dict[str, t.Any]] = dict(payload.get("analysis_params") or {})
    split_config: t.Optional[ExperimentSplitConfig] = payload.get("split_config")

    status = ExperimentStatus.PENDING
    results: list[ExportResult] = []
    logs = ""
    trained_model: t.Optional[ModelAPI] = None

    try:
      model = ModelManager.instantiate(prob_type, payload["model_name"], payload["hyperparams"])

      if prob_type in SUPERVISED_TYPES:
        if target_idx is None:
          raise ValueError(_("experiment.err.supervised_requires_target"))

        if dataset_info.layout == DatasetLayout.TRAIN_TEST_SPLIT:
          train_df = read_dataset_frame(dataset_info.train_path, dataset_info.has_header).dropna()
          test_df = read_dataset_frame(dataset_info.test_path, dataset_info.has_header).dropna()
          X_train, y_train = self._features_and_target(train_df, target_idx)
          X_test, y_test = self._features_and_target(test_df, target_idx)
        else:
          df = read_dataset_frame(dataset_info.full_path, dataset_info.has_header).dropna()
          X, y = self._features_and_target(df, target_idx)
          cfg = split_config or ExperimentSplitConfig()
          X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=cfg.test_size,
            random_state=42,
          )

        model.fit(X_train, y_train)
        trained_model = model
        preds = model.predict(X_test)
        results = self._run_analyses(
          prob_type,
          selected_analyses,
          analysis_params=analysis_params,
          y_true=y_test,
          y_pred=preds,
        )

      elif prob_type == ProblemType.CLUSTERING:
        df = read_dataset_frame(dataset_info.full_path, dataset_info.has_header).dropna()
        X = pd.get_dummies(df)
        model.fit(X)
        trained_model = model
        labels = model.predict(X)
        results = self._run_analyses(
          prob_type,
          selected_analyses,
          analysis_params=analysis_params,
          X=X,
          labels=labels,
        )

      elif prob_type == ProblemType.DIMENSIONALITY_REDUCTION:
        df = read_dataset_frame(dataset_info.full_path, dataset_info.has_header).dropna()
        X = pd.get_dummies(df)
        model.fit(X)
        trained_model = model
        embedding = model.transform(X)
        results = self._run_analyses(
          prob_type,
          selected_analyses,
          analysis_params=analysis_params,
          X=X,
          embedding=embedding,
          model=model,
        )

      else:
        raise ValueError(_("dataset.err.unsupported_problem_type").format(problem_type=prob_type))

      status = ExperimentStatus.OK
      logs = _("experiment.msg.completed")

    except Exception as e:
      status = ExperimentStatus.NOK
      logs = _("experiment.msg.pipeline_error").format(error=str(e))
    finally:
      self.config(cursor="")

    new_experiment = ExperimentManager.add_experiment(
      name=payload["name"],
      dataset=payload["dataset"],
      model_name=payload["model_name"],
      hyperparams=payload["hyperparams"],
      status=status,
      selected_analyses=selected_analyses,
      analysis_params=analysis_params,
      split_config=split_config,
    )

    ExperimentManager.save_logs(new_experiment.id, logs)

    if status == ExperimentStatus.OK:
      if results:
        ExperimentManager.save_results(new_experiment.id, results)

      if trained_model is not None:
        ExperimentManager.save_trained_model(new_experiment.id, trained_model)

    self.load_table_data()

    experiment_data = ExperimentExportData(
      name=payload["name"],
      dataset=payload["dataset"],
      problem_type=prob_type,
      model_name=payload["model_name"],
      hyperparameters=payload["hyperparams"],
      pickle_path=None,
    )

    if status == ExperimentStatus.OK:
      reloaded = next(e for e in ExperimentManager.get_all() if e.id == new_experiment.id)
      experiment_data = ExperimentExportData.from_experiment_metadata(reloaded)

    self._show_results_popup(experiment_data, status, results, trained_model, logs=logs)

  def view_results(self) -> None:
    experiments = self._get_selected_experiments()

    if not experiments:
      messagebox.showwarning(_("common.warning"), _("experiment.msg.select_at_least_one_results"))
      return

    to_open: list[tuple] = []

    for experiment in experiments:
      results = ExperimentManager.load_results(experiment.id)
      logs = ExperimentManager.load_logs(experiment.id)

      if not results and not logs:
        continue

      to_open.append((experiment, results, logs))

    if not to_open:
      messagebox.showinfo(_("experiment.msg.no_results_title"), _("experiment.msg.no_results_body"))
      return

    modal = len(to_open) == 1

    for index, (experiment, results, logs) in enumerate(to_open):
      experiment_data = ExperimentExportData.from_experiment_metadata(experiment)
      self._show_results_popup(
        experiment_data,
        experiment.status,
        results,
        logs=logs,
        modal=modal,
        geometry_offset=index,
      )

  def export_selected(self) -> None:
    experiment = self._get_selected_experiment()

    if experiment is None:
      messagebox.showwarning(_("common.warning"), _("experiment.msg.select_one_export"))
      return

    experiment_data = ExperimentExportData.from_experiment_metadata(experiment)
    results = ExperimentManager.load_results(experiment.id)
    logs = ExperimentManager.load_logs(experiment.id)

    if logs:
      results = [TextResult("logs.txt", logs, label=_("common.logs")), *results]

    ExperimentExportModal(self, experiment_data, results)

  def duplicate_experiment(self) -> None:
    experiment = self._get_selected_experiment()

    if experiment is None:
      messagebox.showwarning(_("common.warning"), _("experiment.msg.select_one_duplicate"))
      return

    ExperimentFormModal(self, on_save=self._on_experiment_saved, initial_data=experiment)

  def delete_experiment(self) -> None:
    experiments = self._get_selected_experiments()

    if not experiments:
      messagebox.showwarning(_("common.warning"), _("experiment.msg.select_delete"))
      return

    label = experiments[0].name if len(experiments) == 1 else _("experiment.msg.n_experiments").format(n=len(experiments))

    if not messagebox.askyesno(_("common.confirm_delete"), _("experiment.msg.delete_confirm").format(label=label)):
      return

    for experiment in experiments:
      ExperimentManager.delete_experiment(experiment.id)

    self.load_table_data()
    self._set_logs_panel("")

  def _show_results_popup(
    self,
    experiment_data: ExperimentExportData,
    status: ExperimentStatus,
    results: list[ExportResult],
    trained_model: t.Optional[ModelAPI] = None,
    logs: str = "",
    *,
    modal: bool = True,
    geometry_offset: int = 0,
  ) -> None:
    popup = tk.Toplevel(self)
    popup.title(_("experiment.results.title").format(name=experiment_data.name))
    x = 40 + geometry_offset * 30
    y = 40 + geometry_offset * 30
    popup.geometry(f"640x680+{x}+{y}")
    popup.resizable(False, False)

    if modal:
      popup.grab_set()

    main_frame = ttk.Frame(popup, padding=(20, 20))
    main_frame.pack(fill=tk.BOTH, expand=True)

    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

    scalars = [r for r in results if isinstance(r, ScalarResult)]
    texts = [r for r in results if isinstance(r, TextResult)]
    images = [r for r in results if isinstance(r, (ImageResult, StoredImageResult))]

    def add_text_tab(title: str, content: str) -> None:
      tab = ttk.Frame(notebook)
      notebook.add(tab, text=title)

      scrollbar = ttk.Scrollbar(tab, orient="vertical")
      scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

      text_widget = tk.Text(
        tab,
        wrap=tk.WORD,
        bg="#1e1e1e",
        fg="#d4d4d4",
        font=("Consolas", 10),
        relief="flat",
        yscrollcommand=scrollbar.set,
      )
      text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
      scrollbar.config(command=text_widget.yview)
      text_widget.insert(tk.END, content)
      text_widget.config(state=tk.DISABLED)

    add_text_tab(_("common.logs"), logs)

    if scalars:
      tab_metrics = ttk.Frame(notebook)
      notebook.add(tab_metrics, text=_("common.metrics"))

      tree = ttk.Treeview(tab_metrics, columns=("metric", "value"), show="headings", height=8)
      tree.heading("metric", text=_("common.metric"))
      tree.heading("value", text=_("common.value"))
      tree.column("metric", width=220)
      tree.column("value", width=160)
      tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

      for scalar in scalars:
        tree.insert("", tk.END, values=(scalar.label, scalar.value))

    for text_result in texts:
      add_text_tab(text_result.label, text_result.content)

    for image_result in images:
      tab_chart = ttk.Frame(notebook)
      notebook.add(tab_chart, text=image_result.label)

      canvas = FigureCanvasTkAgg(image_result.figure, master=tab_chart)
      canvas.draw()
      canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def open_export() -> None:
      from application.views.experiment import ExperimentExportModal
      ExperimentExportModal(popup, experiment_data, results, trained_model)

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X)

    ttk.Button(btn_frame, text=_("common.close"), command=popup.destroy).pack(side=tk.RIGHT, ipady=6, ipadx=10)

    if status == ExperimentStatus.OK:
      ttk.Button(btn_frame, text=_("common.export"), command=open_export).pack(side=tk.RIGHT, padx=(0, 10), ipady=6, ipadx=10)
