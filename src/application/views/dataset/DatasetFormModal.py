import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd

from application.components import ProblemTypeSelector
from application.enums import ProblemType
from application.i18n import _
from application.managers.DatasetManager import SUPERVISED_TYPES, UNSUPERVISED_TYPES

class DatasetFormModal(tk.Toplevel):

  def __init__(self, parent, on_save, dataset_data=None):
    super().__init__(parent)

    self.is_editing = dataset_data is not None
    self.title(_("dataset.form.edit_title") if self.is_editing else _("dataset.form.add_title"))

    self.geometry("400x420")
    self.resizable(False, False)
    self.grab_set()

    self.on_save = on_save

    data = dataset_data or {}
    self.dataset_id = data.get("id")

    self.name_var = tk.StringVar(value=data.get("name", ""))
    self.type_var = tk.StringVar(value=data.get("type", "Classification"))
    self.path_var = tk.StringVar(value=data.get("path", ""))
    initial_target = data.get("target")
    self.target_var = tk.StringVar(value=initial_target if initial_target else "")

    self._build_ui()

    self.path_var.trace_add("write", self._load_csv_columns)
    self.type_var.trace_add("write", self._on_type_changed)

    if self.path_var.get():
      self._load_csv_columns()

    self._on_type_changed()

  def _build_ui(self):
    main_frame = ttk.Frame(self, padding=(25, 20))
    main_frame.pack(fill=tk.BOTH, expand=True)

    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.BOTH, expand=True)
    form_frame.columnconfigure(0, weight=1)

    ttk.Label(form_frame, text=_("dataset.form.name"), foreground="#333333").grid(row=0, column=0, sticky="w", pady=(0, 2))
    ttk.Entry(form_frame, textvariable=self.name_var).grid(row=1, column=0, sticky="ew", pady=(0, 15))

    ttk.Label(form_frame, text=_("dataset.form.paradigm_type"), foreground="#333333").grid(row=2, column=0, sticky="w", pady=(0, 2))

    selector = ProblemTypeSelector(form_frame, type_var=self.type_var, initial_value=self.type_var.get())
    selector.grid(row=3, column=0, sticky="ew", pady=(0, 15))

    ttk.Label(form_frame, text=_("dataset.form.file"), foreground="#333333").grid(row=4, column=0, sticky="w", pady=(0, 2))

    file_frame = ttk.Frame(form_frame)
    file_frame.grid(row=5, column=0, sticky="ew", pady=(0, 15))

    ttk.Entry(file_frame, textvariable=self.path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Button(file_frame, text=_("common.browse"), command=self._browse_file, width=8).pack(side=tk.RIGHT, padx=(5, 0))

    self.target_label = ttk.Label(form_frame, text=_("dataset.form.target"), foreground="#333333")
    self.target_label.grid(row=6, column=0, sticky="w", pady=(0, 2))
    self.target_selector = ttk.Combobox(form_frame, textvariable=self.target_var, state="readonly")
    self.target_selector.grid(row=7, column=0, sticky="ew", pady=(0, 20))

    btn_text = _("dataset.form.update") if self.is_editing else _("dataset.form.save")

    save_btn = ttk.Button(main_frame, text=btn_text, command=self._handle_save)
    save_btn.pack(fill=tk.X, ipady=6)

  def _current_problem_type(self) -> ProblemType:
    return ProblemType(self.type_var.get())

  def _is_supervised(self) -> bool:
    return self._current_problem_type() in SUPERVISED_TYPES

  def _on_type_changed(self, *args) -> None:
    if self._is_supervised():
      self.target_label.config(text=_("dataset.form.target"))
      self.target_selector.config(state="readonly")

      if self.path_var.get() and not self.target_var.get():
        self._load_csv_columns()
    else:
      self.target_label.config(text=_("dataset.form.target_unused"))
      self.target_var.set("")
      self.target_selector.config(state="disabled")

  def _browse_file(self):
    filepath = filedialog.askopenfilename(
      parent=self,
      filetypes=[(_("common.filetypes.csv"), "*.csv")]
    )

    if filepath:
      self.path_var.set(filepath)

    self.lift()
    self.focus_force()

  def _load_csv_columns(self, *args):
    filepath = self.path_var.get()

    if not filepath:
      return

    try:
      df = pd.read_csv(filepath, nrows=0)
      columns = df.columns.tolist()

      self.target_selector["values"] = columns

      if self._is_supervised() and columns and not self.target_var.get():
        self.target_var.set(columns[-1])

    except Exception as e:
      self.target_selector["values"] = []
      self.target_var.set("")
      print(f"Error reading CSV inside modal: {e}")

  def _handle_save(self):
    if not self.name_var.get() or not self.path_var.get():
      messagebox.showerror(_("common.error"), _("dataset.form.err_name_file"), parent=self)
      return

    problem_type = self._current_problem_type()
    target_value = self.target_var.get().strip() or None

    if problem_type in SUPERVISED_TYPES and target_value is None:
      messagebox.showerror(_("common.error"), _("dataset.form.err_target_required"), parent=self)
      return

    if problem_type in UNSUPERVISED_TYPES:
      target_value = None

    dataset_payload = {
      "id": self.dataset_id,
      "name": self.name_var.get(),
      "type": self.type_var.get(),
      "path": self.path_var.get(),
      "target": target_value,
    }

    try:
      self.on_save(dataset_payload)
    except Exception as e:
      messagebox.showerror(_("common.error"), str(e), parent=self)
      return

    self.destroy()
