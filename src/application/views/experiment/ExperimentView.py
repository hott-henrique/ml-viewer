import typing as t
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from sklearn.model_selection import train_test_split

from application.components import HyperParamForm
from application.enums import ExperimentStatus, ProblemType
from application.managers.DatasetManager import DatasetMetadata
from application.managers.results import (
  ClassificationAnalyzer,
  ExportResult,
  ImageResult,
  RegressionAnalyzer,
  ResultAnalyzer,
  StoredImageResult,
  TextResult,
)
from application.views.experiment import ExperimentFormModal, ExperimentExportModal
from application.views.experiment.ExperimentExportModal import ExperimentExportData
from application.managers import ExperimentManager, ModelManager
from application.managers.model.ModelManager import ModelAPI

class ExperimentView(ttk.Frame):

  def __init__(self, parent: tk.Misc) -> None:
    super().__init__(parent)
    
    header_frame = ttk.Frame(self)
    header_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(header_frame, text="🧪 Experiments", font=("", 16, "bold")).pack(side=tk.LEFT)
    
    ttk.Button(header_frame, text="🗑️ Delete", command=self.delete_experiment).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text="💾 Export", command=self.export_selected).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text="📊 View Results", command=self.view_results).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text="📑 Duplicate", command=self.duplicate_experiment).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text="➕ Run", command=self.open_create_modal).pack(side=tk.RIGHT)

    table_frame = ttk.Frame(self)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("id", "name", "dataset", "model", "status", "date")
    self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
    
    self.tree.heading("id", text="ID")
    self.tree.column("id", width=0, stretch=tk.NO) 

    self.tree.heading("name", text="Experiment Name")
    self.tree.heading("dataset", text="Dataset")
    self.tree.heading("model", text="Model")
    self.tree.heading("status", text="Status")
    self.tree.heading("date", text="Created On")

    self.tree.column("name", width=150)
    self.tree.column("dataset", width=120)
    self.tree.column("model", width=120)
    self.tree.column("status", width=80)
    self.tree.column("date", width=130)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.tree.bind("<<TreeviewSelect>>", self.on_experiment_selected)

    details_frame = ttk.Frame(self)
    details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    details_frame.columnconfigure(0, weight=1)
    details_frame.columnconfigure(1, weight=2)
    details_frame.rowconfigure(0, weight=1)

    param_frame = ttk.LabelFrame(details_frame, text="Hyperparameters (Read-Only)")
    param_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
    
    self.hyperparam_form = HyperParamForm(param_frame, is_readonly=True)
    self.hyperparam_form.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    logs_frame = ttk.LabelFrame(details_frame, text="Execution Logs")
    logs_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
    
    self.logs_text = tk.Text(logs_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#f5f5f5", height=10)
    self.logs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    self.load_table_data()

  def _get_selected_experiment(self):
    selected = self.tree.selection()

    if not selected:
      return None

    exp_id = str(self.tree.item(selected[0])["values"][0])

    return next((e for e in ExperimentManager.get_all() if str(e.id) == exp_id), None)

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
      status_icon = "⏳ Pending" if status == "Pending" else ("✅ OK" if status == "OK" else "❌ NOK")

      self.tree.insert("", tk.END, values=(
        exp.id, exp.name, exp.dataset_name, 
        exp.model_name, status_icon, exp.date
      ))

  def on_experiment_selected(self, event: t.Optional[tk.Event]) -> None:
    experiment = self._get_selected_experiment()

    if experiment is None:
      return

    prob_type = experiment.problem_type
    model_name = experiment.model_name
    saved_hyperparams = experiment.hyperparameters

    model_config = ModelManager.registry(prob_type).get(model_name)

    if model_config:
      self.hyperparam_form.render_form(model_config.params)
      
      for param_name, param_value in saved_hyperparams.items():
          if param_name in self.hyperparam_form.param_vars:
              self.hyperparam_form.param_vars[param_name].set(str(param_value))
    else:
      print('Failed to find model to show!')

    try:
      logs = ExperimentManager.load_logs(experiment.id)
    except Exception as e:
      logs = f"(Failed to load logs: {e})"

    self._set_logs_panel(logs)

  def open_create_modal(self) -> None:
    ExperimentFormModal(self, on_save=self._on_experiment_saved)

  def _get_analyzer(self, prob_type: ProblemType, target_col: str) -> ResultAnalyzer:
    if prob_type == ProblemType.CLASSIFICATION:
      return ClassificationAnalyzer(target_col)

    return RegressionAnalyzer(target_col)

  def _on_experiment_saved(self, payload: dict[str, t.Any]) -> None:
    self.config(cursor="watch")
    self.update()

    dataset_info: DatasetMetadata = payload["dataset"]
    prob_type = dataset_info.type
    target_col = dataset_info.target
    filepath = dataset_info.path
    
    status = ExperimentStatus.PENDING
    results: list[ExportResult] = []
    logs = ""
    trained_model: t.Optional[ModelAPI] = None

    try:
      df = pd.read_csv(filepath)

      if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataset.")

      df = df.dropna()
      X = df.drop(columns=[target_col])
      y = df[target_col]
      X = pd.get_dummies(X)

      X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

      model = ModelManager.instantiate(prob_type, payload["model_name"], payload["hyperparams"])

      model.fit(X_train, y_train)
      trained_model = model

      preds = model.predict(X_test)

      analyzer = self._get_analyzer(prob_type, target_col)
      results = analyzer.analyze(y_test, preds)

      status = ExperimentStatus.OK
      logs = "Experiment completed successfully."

    except Exception as e:
      status = ExperimentStatus.NOK
      logs = f"Error executing pipeline:\n\n{str(e)}\n\nTry checking if your hyperparameters are valid."
    finally:
      self.config(cursor="")

    new_experiment = ExperimentManager.add_experiment(
      name=payload["name"],
      dataset=payload["dataset"],
      model_name=payload["model_name"],
      hyperparams=payload["hyperparams"],
      status=status,
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
    experiment = self._get_selected_experiment()

    if experiment is None:
      messagebox.showwarning("Warning", "Select an experiment to view results.")
      return

    results = ExperimentManager.load_results(experiment.id)

    if not results and experiment.status != ExperimentStatus.OK:
      messagebox.showinfo("No Results", "This experiment has no persisted analysis results.")
      return

    if not results:
      messagebox.showinfo("No Results", "No analysis results were found for this experiment.")
      return

    experiment_data = ExperimentExportData.from_experiment_metadata(experiment)
    self._show_results_popup(experiment_data, experiment.status, results)

  def export_selected(self) -> None:
    experiment = self._get_selected_experiment()

    if experiment is None:
      messagebox.showwarning("Warning", "Select an experiment to export.")
      return

    experiment_data = ExperimentExportData.from_experiment_metadata(experiment)
    results = ExperimentManager.load_results(experiment.id)
    logs = ExperimentManager.load_logs(experiment.id)

    if logs:
      results = [TextResult("logs.txt", logs), *results]

    ExperimentExportModal(self, experiment_data, results)

  def duplicate_experiment(self) -> None:
    experiment = self._get_selected_experiment()

    if experiment is None:
      messagebox.showwarning("Warning", "Select an experiment to duplicate.")
      return

    ExperimentFormModal(self, on_save=self._on_experiment_saved, initial_data=experiment)

  def delete_experiment(self) -> None:
    experiment = self._get_selected_experiment()

    if experiment is None:
      return

    if messagebox.askyesno("Confirm", "Delete this experiment permanently?"):
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
  ) -> None:
    popup = tk.Toplevel(self)
    popup.title(f"Results: {experiment_data.name}")
    popup.geometry("600x650")
    popup.resizable(False, False)
    popup.grab_set()

    main_frame = ttk.Frame(popup, padding=(20, 20))
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_text = "✅ Execution Successful!" if status == ExperimentStatus.OK else "🚨 Execution Failed!"
    fg_color = "#27ae60" if status == ExperimentStatus.OK else "#c0392b"

    ttk.Label(main_frame, text=header_text, font=("", 14, "bold"), foreground=fg_color).pack(anchor=tk.W, pady=(0, 10))

    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

    text_results = [r for r in results if isinstance(r, TextResult)]
    report_text = "\n\n".join(r.content for r in text_results)

    if status != ExperimentStatus.OK and not report_text and logs:
      report_text = logs

    tab_text = ttk.Frame(notebook)
    notebook.add(tab_text, text="📝 Report")

    scrollbar = ttk.Scrollbar(tab_text, orient="vertical")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_widget = tk.Text(
      tab_text,
      wrap=tk.WORD,
      bg="#1e1e1e",
      fg="#d4d4d4",
      font=("Consolas", 10),
      relief="flat",
      yscrollcommand=scrollbar.set
    )
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_widget.yview)

    text_widget.insert(tk.END, report_text)
    text_widget.config(state=tk.DISABLED)

    if status == ExperimentStatus.OK:
      for image_result in (r for r in results if isinstance(r, (ImageResult, StoredImageResult))):
        tab_chart = ttk.Frame(notebook)
        notebook.add(tab_chart, text=f"📊 {image_result.name}")

        canvas = FigureCanvasTkAgg(image_result.figure, master=tab_chart)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def open_export() -> None:
      from application.views.experiment import ExperimentExportModal
      ExperimentExportModal(popup, experiment_data, results, trained_model)

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X)

    ttk.Button(btn_frame, text="Close", command=popup.destroy).pack(side=tk.RIGHT, ipady=6, ipadx=10)
    
    if status == ExperimentStatus.OK:
        ttk.Button(btn_frame, text="💾 Export", command=open_export).pack(side=tk.RIGHT, padx=(0, 10), ipady=6, ipadx=10)
