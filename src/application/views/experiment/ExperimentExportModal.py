import os
import json
import zipfile
import pickle
import typing as t
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from pydantic import BaseModel

from application.enums import ProblemType
from application.i18n import _
from application.managers import ModelManager
from application.managers.DatasetManager import DatasetMetadata
from application.managers.ExperimentManager import ExperimentMetadata
from application.managers.model.base import ModelAPI
from application.managers.results import ExportResult

HyperParamValue = int | float | bool | str

class ExperimentExportData(BaseModel):
  name: str
  dataset: DatasetMetadata
  problem_type: ProblemType
  model_name: str
  hyperparameters: dict[str, HyperParamValue]
  pickle_path: t.Optional[str] = None

  @classmethod
  def from_experiment_metadata(cls, experiment: ExperimentMetadata) -> "ExperimentExportData":
    return cls(
      name=experiment.name,
      dataset=experiment.dataset,
      problem_type=experiment.problem_type,
      model_name=experiment.model_name,
      hyperparameters=experiment.hyperparameters,
      pickle_path=experiment.pickle_path,
    )

class ExperimentExportModal(tk.Toplevel):

  def __init__(
    self,
    parent: tk.Misc,
    experiment_data: ExperimentExportData,
    results: list[ExportResult],
    trained_model: t.Optional[ModelAPI] = None,
  ) -> None:
    super().__init__(parent)
    self.title(_("experiment.export.title").format(name=experiment_data.name))
    self.geometry("420x300")
    self.resizable(False, False)
    self.grab_set()

    self.experiment_data = experiment_data
    self.results = results
    self.trained_model = trained_model

    self._build_ui()

  def _build_ui(self) -> None:
    main_frame = ttk.Frame(self, padding=(20, 20))
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text=_("experiment.export.select_items"), font=("", 12, "bold")).pack(anchor=tk.W, pady=(0, 15))

    self.inc_dataset_var = tk.BooleanVar(value=True)
    self.inc_model_var = tk.BooleanVar(value=True)
    self.inc_script_var = tk.BooleanVar(value=True)

    ttk.Checkbutton(main_frame, text=_("experiment.export.include_dataset"), variable=self.inc_dataset_var).pack(anchor=tk.W, pady=5)

    self.chk_model = ttk.Checkbutton(main_frame, text=_("experiment.export.include_model"), variable=self.inc_model_var)
    self.chk_model.pack(anchor=tk.W, pady=5)

    if self.trained_model is None and not self.experiment_data.pickle_path:
      self.chk_model.config(text=_("experiment.export.include_model_unavailable"))
      self.chk_model.state(['disabled'])
      self.inc_model_var.set(False)

    self.chk_script = ttk.Checkbutton(main_frame, text=_("experiment.export.include_script"), variable=self.inc_script_var)
    self.chk_script.pack(anchor=tk.W, pady=5)

    prob_type = self.experiment_data.problem_type
    model_name = self.experiment_data.model_name

    registry = ModelManager.registry(prob_type)

    model_config = registry.get(model_name)

    self.plugin_path = model_config.plugin_path if model_config else None

    if not self.plugin_path or not os.path.exists(self.plugin_path):
      self.chk_script.config(text=_("experiment.export.include_script_native"))
      self.chk_script.state(['disabled'])
      self.inc_script_var.set(False)

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X, pady=(25, 0))

    ttk.Button(btn_frame, text=_("common.cancel"), command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0), ipady=4, ipadx=10)
    ttk.Button(btn_frame, text=_("experiment.export.as_zip"), command=self._handle_export).pack(side=tk.RIGHT, ipady=4, ipadx=10)

  def _handle_export(self) -> None:
    exp_name = self.experiment_data.name.replace(' ', '_')

    filepath = filedialog.asksaveasfilename(
      parent=self,
      defaultextension=".zip",
      filetypes=[(_("common.filetypes.zip"), "*.zip")],
      title=_("experiment.export.dialog_title"),
      initialfile=f"experiment_{exp_name}.zip"
    )

    if not filepath:
      return

    try:
      with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("experiment_config.json", json.dumps(self.experiment_data.model_dump(mode="json"), indent=4))

        for result in self.results:
          result.include_in_zip(zf)

        if self.inc_dataset_var.get():
          ds_path = self.experiment_data.dataset.path

          if ds_path and os.path.exists(ds_path):
            zf.write(ds_path, os.path.basename(ds_path))

        if self.inc_model_var.get():
          model_filename = f"model_{self.experiment_data.model_name.replace(' ', '_')}.pkl"

          if self.trained_model is not None:
            zf.writestr(model_filename, pickle.dumps(self.trained_model))
          elif self.experiment_data.pickle_path and os.path.exists(self.experiment_data.pickle_path):
            zf.write(self.experiment_data.pickle_path, model_filename)

        if self.inc_script_var.get() and self.plugin_path:
            zf.write(self.plugin_path, os.path.basename(self.plugin_path))

      messagebox.showinfo(_("common.success"), _("experiment.export.success").format(path=filepath), parent=self)

      self.destroy()
    except Exception as e:
        messagebox.showerror(_("common.export_error"), _("experiment.export.failed").format(error=str(e)), parent=self)
