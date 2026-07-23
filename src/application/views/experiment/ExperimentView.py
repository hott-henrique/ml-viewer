import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score

from application.components import HyperParamForm
from application.views.experiment import ExperimentFormModal, ExperimentExportModal
from application.managers import ExperimentManager, ModelManager

class ExperimentView(ttk.Frame):

  def __init__(self, parent):
    super().__init__(parent)
    
    header_frame = ttk.Frame(self)
    header_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(header_frame, text="🧪 Experiments", font=("", 16, "bold")).pack(side=tk.LEFT)
    
    ttk.Button(header_frame, text="🗑️ Delete", command=self.delete_experiment).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text="💾 Export", command=self.export_selected).pack(side=tk.RIGHT, padx=(5, 0))
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

    result_frame = ttk.LabelFrame(details_frame, text="Execution Results")
    result_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
    
    self.result_text = tk.Text(result_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#f5f5f5", height=10)
    self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    self.load_table_data()

  def load_table_data(self):
    for item in self.tree.get_children():
      self.tree.delete(item)

    experiments = ExperimentManager.get_all()

    for exp in experiments:
      status = exp["status"]
      status_icon = "⏳ Pending" if status == "Pending" else ("✅ OK" if status == "OK" else "❌ NOK")

      self.tree.insert("", tk.END, values=(
        exp["id"], exp["name"], exp["dataset_name"], 
        exp["model_name"], status_icon, exp["date"]
      ))

  def on_experiment_selected(self, event):
    selected = self.tree.selection()
    if not selected:
      return

    exp_id = str(self.tree.item(selected[0])["values"][0])
    experiment = next((e for e in ExperimentManager.get_all() if str(e["id"]) == exp_id), None)

    if experiment:
      prob_type = experiment.get("problem_type")
      model_name = experiment.get("model_name")
      saved_hyperparams = experiment.get("hyperparameters", {})

      registry = ModelManager.registry(prob_type)
      model_data = registry.get(model_name, {})
      
      self.hyperparam_form.render_form(model_data.get("params", []))
      
      for param_name, param_value in saved_hyperparams.items():
          if param_name in self.hyperparam_form.param_vars:
              self.hyperparam_form.param_vars[param_name].set(str(param_value))
              
      self.result_text.config(state=tk.NORMAL)
      self.result_text.delete(1.0, tk.END)
      self.result_text.insert(tk.END, experiment.get("results", "No results to display."))
      self.result_text.config(state=tk.DISABLED)

  def open_create_modal(self):
    ExperimentFormModal(self, on_save=self._on_experiment_saved)

  def _on_experiment_saved(self, payload):
    self.config(cursor="watch")
    self.update()

    dataset_info = payload["dataset"]
    prob_type = dataset_info.get("type")
    target_col = dataset_info.get("target")
    filepath = dataset_info.get("path")
    
    status = "Pending"
    results_str = ""
    trained_model = None

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

      if prob_type == "Classification":
        acc = accuracy_score(y_test, preds)
        report = classification_report(y_test, preds)
        results_str = f"Target Column: {target_col}\nTest Size: 20%\n\nAccuracy: {acc:.4f}\n\nClassification Report:\n{report}"
      else:
        mse = mean_squared_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        results_str = f"Target Column: {target_col}\nTest Size: 20%\n\nMean Squared Error (MSE): {mse:.4f}\nR2 Score: {r2:.4f}"
          
      status = "OK"

    except Exception as e:
      status = "NOK"
      results_str = f"Error executing pipeline:\n\n{str(e)}\n\nTry checking if your hyperparameters are valid or if the dataset requires specific preprocessing."
    finally:
      self.config(cursor="")

    ExperimentManager.add_experiment(
      name=payload["name"],
      dataset=payload["dataset"],
      model_name=payload["model_name"],
      hyperparams=payload["hyperparams"],
      status=status,
      results=results_str
    )

    self.load_table_data()
    
    # Remonta o dicionario como o Manager salva para passar para o Popup
    experiment_data = {
        "name": payload["name"],
        "dataset": payload["dataset"],
        "problem_type": prob_type,
        "model_name": payload["model_name"],
        "hyperparameters": payload["hyperparams"]
    }
    self._show_results_popup(experiment_data, status, results_str, trained_model)

  # --- NOVA FUNÇÃO: Acionada pelo botão no topo da tabela ---
  def export_selected(self):
    selected = self.tree.selection()
    if not selected:
      messagebox.showwarning("Warning", "Select an experiment to export.")
      return

    exp_id = str(self.tree.item(selected[0])["values"][0])
    target_exp = next((e for e in ExperimentManager.get_all() if str(e["id"]) == exp_id), None)

    if target_exp:
      ExperimentExportModal(self, target_exp, target_exp.get("results", ""))

  def duplicate_experiment(self):
    selected = self.tree.selection()
    if not selected:
      messagebox.showwarning("Warning", "Select an experiment to duplicate.")
      return

    exp_id = str(self.tree.item(selected[0])["values"][0])
    target_exp = next((e for e in ExperimentManager.get_all() if str(e["id"]) == exp_id), None)

    if target_exp:
      ExperimentFormModal(self, on_save=self._on_experiment_saved, initial_data=target_exp)

  def delete_experiment(self):
    selected = self.tree.selection()
    if not selected:
      return

    exp_id = str(self.tree.item(selected[0])["values"][0])

    if messagebox.askyesno("Confirm", "Delete this experiment permanently?"):
      ExperimentManager.delete_experiment(exp_id)
      self.load_table_data()
      self.result_text.config(state=tk.NORMAL)
      self.result_text.delete(1.0, tk.END)
      self.result_text.config(state=tk.DISABLED)

  def _show_results_popup(self, experiment_data, status, results, trained_model=None):
    popup = tk.Toplevel(self)
    popup.title(f"Results: {experiment_data['name']}")
    popup.geometry("600x480") # Voltei pro tamanho limpo
    popup.resizable(False, False)
    popup.grab_set()

    main_frame = ttk.Frame(popup, padding=(20, 20))
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_text = "✅ Execution Successful!" if status == "OK" else "🚨 Execution Failed!"
    fg_color = "#27ae60" if status == "OK" else "#c0392b"

    ttk.Label(main_frame, text=header_text, font=("", 14, "bold"), foreground=fg_color).pack(anchor=tk.W, pady=(0, 10))

    text_frame = ttk.Frame(main_frame)
    text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

    scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_widget = tk.Text(
      text_frame,
      wrap=tk.WORD,
      bg="#1e1e1e",
      fg="#d4d4d4",
      font=("Consolas", 10),
      relief="flat",
      yscrollcommand=scrollbar.set
    )
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_widget.yview)

    text_widget.insert(tk.END, results)
    text_widget.config(state=tk.DISABLED)

    def open_export():
      ExperimentExportModal(popup, experiment_data, results, trained_model)

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X)

    ttk.Button(btn_frame, text="Close", command=popup.destroy).pack(side=tk.RIGHT, ipady=6, ipadx=10)
    
    if status == "OK":
        ttk.Button(btn_frame, text="💾 Export", command=open_export).pack(side=tk.RIGHT, padx=(0, 10), ipady=6, ipadx=10)