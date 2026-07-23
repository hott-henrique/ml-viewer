import os
import json
import zipfile
import pickle
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from application.managers import ModelManager

class ExperimentExportModal(tk.Toplevel):

  def __init__(self, parent, experiment_data, results_str, trained_model=None):
    super().__init__(parent)
    self.title(f"Export: {experiment_data.get('name', 'Experiment')}")
    self.geometry("420x300")
    self.resizable(False, False)
    self.grab_set()

    self.experiment_data = experiment_data
    self.results_str = results_str
    self.trained_model = trained_model

    self._build_ui()

  def _build_ui(self):
    main_frame = ttk.Frame(self, padding=(20, 20))
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Select items to include in the ZIP:", font=("", 12, "bold")).pack(anchor=tk.W, pady=(0, 15))

    self.inc_dataset_var = tk.BooleanVar(value=True)
    self.inc_model_var = tk.BooleanVar(value=True)
    self.inc_script_var = tk.BooleanVar(value=True)

    ttk.Checkbutton(main_frame, text="Include Dataset (.csv)", variable=self.inc_dataset_var).pack(anchor=tk.W, pady=5)

    self.chk_model = ttk.Checkbutton(main_frame, text="Include Trained Model (.pkl)", variable=self.inc_model_var)
    self.chk_model.pack(anchor=tk.W, pady=5)

    if self.trained_model is None:
      self.chk_model.config(text="Include Trained Model (.pkl)  [Not in memory]")
      self.chk_model.state(['disabled'])
      self.inc_model_var.set(False)

    self.chk_script = ttk.Checkbutton(main_frame, text="Include Model Script (.py)", variable=self.inc_script_var)
    self.chk_script.pack(anchor=tk.W, pady=5)

    prob_type = self.experiment_data.get("problem_type") or self.experiment_data.get("dataset", {}).get("type")
    model_name = self.experiment_data.get("model_name")
    registry = ModelManager.registry(prob_type)
    model_data = registry.get(model_name, {})
    self.plugin_path = model_data.get("plugin_path")

    if not self.plugin_path or not os.path.exists(self.plugin_path):
      self.chk_script.config(text="Include Model Script (.py)  [Native model]")
      self.chk_script.state(['disabled'])
      self.inc_script_var.set(False)

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X, pady=(25, 0))

    ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0), ipady=4, ipadx=10)
    ttk.Button(btn_frame, text="💾 Export as ZIP", command=self._handle_export).pack(side=tk.RIGHT, ipady=4, ipadx=10)

  def _handle_export(self):
    exp_name = self.experiment_data.get("name", "experiment").replace(' ', '_')

    filepath = filedialog.asksaveasfilename(
      parent=self,
      defaultextension=".zip",
      filetypes=[("ZIP Archive", "*.zip")],
      title="Export Experiment as ZIP",
      initialfile=f"experiment_{exp_name}.zip"
    )

    if not filepath:
      return

    try:
      with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("metrics_and_logs.txt", self.results_str)
        zf.writestr("experiment_config.json", json.dumps(self.experiment_data, indent=4))

        if self.inc_dataset_var.get():
          ds_path = self.experiment_data.get("dataset", {}).get("path")

          if ds_path and os.path.exists(ds_path):
            zf.write(ds_path, os.path.basename(ds_path))

        if self.inc_model_var.get() and self.trained_model is not None:
          model_bytes = pickle.dumps(self.trained_model)
          model_filename = f"model_{self.experiment_data.get('model_name', 'model').replace(' ', '_')}.pkl"
          zf.writestr(model_filename, model_bytes)

        if self.inc_script_var.get() and self.plugin_path:
            zf.write(self.plugin_path, os.path.basename(self.plugin_path))

      messagebox.showinfo("Success", f"Experiment exported successfully to:\n{filepath}", parent=self)

      self.destroy()
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export experiment:\n{str(e)}", parent=self)