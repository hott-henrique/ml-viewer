import tkinter as tk
from tkinter import ttk, messagebox

from application.managers import DatasetManager, ModelManager

from application.components import HyperParamForm

class ExperimentFormModal(tk.Toplevel):

  def __init__(self, parent, on_save, initial_data=None):
    super().__init__(parent)

    self.title("New Experiment")
    self.geometry("500x600")
    self.resizable(False, False)
    self.grab_set()

    self.on_save = on_save
    self.initial_data = initial_data or {}
    self.datasets = DatasetManager.get_all()
    
    init_name = self.initial_data.get("name", "")

    if init_name:
        init_name += " (Copy)"

    self.name_var = tk.StringVar(value=init_name)
    self.selected_dataset = None
    self.dataset_var = tk.StringVar()
    self.model_var = tk.StringVar()

    self._build_ui()
    
    self._apply_autofill()

  def _build_ui(self):
    main_frame = ttk.Frame(self, padding=(25, 20))
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Experiment Name:", foreground="#333333").pack(anchor=tk.W)
    ttk.Entry(main_frame, textvariable=self.name_var).pack(fill=tk.X, pady=(0, 15))

    ttk.Label(main_frame, text="Select Dataset:", foreground="#333333").pack(anchor=tk.W)
    dataset_names = [f"{ds.name} ({ds.type})" for ds in self.datasets]
    
    self.ds_combo = ttk.Combobox(main_frame, textvariable=self.dataset_var, values=dataset_names, state="readonly")
    self.ds_combo.pack(fill=tk.X, pady=(0, 15))
    self.ds_combo.bind("<<ComboboxSelected>>", self._on_dataset_selected)

    ttk.Label(main_frame, text="Select Model:", foreground="#333333").pack(anchor=tk.W)
    self.model_combo = ttk.Combobox(main_frame, textvariable=self.model_var, state="readonly")
    self.model_combo.pack(fill=tk.X, pady=(0, 15))
    self.model_combo.bind("<<ComboboxSelected>>", self._on_model_selected)

    self.param_frame = ttk.LabelFrame(main_frame, text="Hyperparameters Config")
    self.param_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
    
    self.hyperparam_form = HyperParamForm(self.param_frame, is_readonly=False)
    self.hyperparam_form.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    ttk.Button(main_frame, text="Run Experiment", command=self._handle_save).pack(fill=tk.X, ipady=6)

  def _apply_autofill(self):
    if not self.initial_data:
      return

    saved_ds = self.initial_data.get("dataset", {})

    ds_str_to_find = f"{saved_ds.get('name')} ({saved_ds.get('type')})"

    if ds_str_to_find in self.ds_combo['values']:
      self.dataset_var.set(ds_str_to_find)
      self._on_dataset_selected(None) 

    saved_model = self.initial_data.get("model_name")

    if saved_model in self.model_combo['values']:
      self.model_var.set(saved_model)
      self._on_model_selected(None)

    saved_hyperparams = self.initial_data.get("hyperparameters", {})

    for param_name, param_value in saved_hyperparams.items():
      if param_name in self.hyperparam_form.param_vars:
        self.hyperparam_form.param_vars[param_name].set(str(param_value))

  def _on_dataset_selected(self, event):
    selected_text = self.dataset_var.get()

    self.selected_dataset = next((ds for ds in self.datasets if f"{ds.name} ({ds.type})" == selected_text), None)

    if not self.selected_dataset:
      return

    prob_type = self.selected_dataset.type

    valid_models = ModelManager.options(prob_type)
    self.model_combo['values'] = valid_models
    self.model_combo.set("")
    self.hyperparam_form.render_form([])

  def _on_model_selected(self, event):
    if not self.selected_dataset:
      return

    prob_type = self.selected_dataset.type

    model_name = self.model_var.get()

    registry = ModelManager.registry(prob_type)
    model_config = registry.get(model_name)

    if model_config:
      self.hyperparam_form.render_form(model_config.params)

  def _handle_save(self):
    if not self.name_var.get() or not self.selected_dataset or not self.model_var.get():
      messagebox.showerror("Error", "Name, Dataset, and Model are required.", parent=self)
      return

    try:
      params = self.hyperparam_form.get_parsed_values()
    except ValueError as e:
      messagebox.showerror("Validation Error", str(e), parent=self)
      return

    payload = {
      "name": self.name_var.get(),
      "dataset": self.selected_dataset,
      "model_name": self.model_var.get(),
      "hyperparams": params
    }

    self.on_save(payload)

    self.destroy()