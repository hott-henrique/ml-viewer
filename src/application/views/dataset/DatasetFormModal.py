import typing as t
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from application.components import ProblemTypeSelector
from application.enums import DatasetFileRole, DatasetLayout, ProblemType
from application.i18n import _, localize_enum
from application.managers.DatasetManager import (
  SUPERVISED_TYPES,
  UNSUPERVISED_TYPES,
  format_target_display,
  parse_target_display,
  peek_column_names,
)

class DatasetFormModal(tk.Toplevel):

  def __init__(self, parent, on_save, dataset_data=None):
    super().__init__(parent)

    self.is_editing = dataset_data is not None
    self.title(_("dataset.form.edit_title") if self.is_editing else _("dataset.form.add_title"))

    self.geometry("440x560")
    self.resizable(False, False)
    self.grab_set()

    self.on_save = on_save

    data = dataset_data or {}
    self.dataset_id = data.get("id")

    self.name_var = tk.StringVar(value=data.get("name", ""))
    self.type_var = tk.StringVar(value=data.get("type", ProblemType.CLASSIFICATION.value))
    self.has_header_var = tk.BooleanVar(value=bool(data.get("has_header", True)))
    self.layout_var = tk.StringVar(value=data.get("layout", DatasetLayout.NO_SPLIT.value))
    self.full_path_var = tk.StringVar(value=data.get("full_path", data.get("path", "")))
    self.train_path_var = tk.StringVar(value=data.get("train_path", ""))
    self.test_path_var = tk.StringVar(value=data.get("test_path", ""))
    initial_target = data.get("target")
    self.target_var = tk.StringVar(value="" if initial_target is None else str(initial_target))

    self._layout_display_to_value = {
      localize_enum(DatasetLayout.NO_SPLIT): DatasetLayout.NO_SPLIT.value,
      localize_enum(DatasetLayout.TRAIN_TEST_SPLIT): DatasetLayout.TRAIN_TEST_SPLIT.value,
    }
    self._layout_value_to_display = {v: k for k, v in self._layout_display_to_value.items()}
    self._layout_display_var = tk.StringVar(
      value=self._layout_value_to_display.get(self.layout_var.get(), localize_enum(DatasetLayout.NO_SPLIT))
    )

    self._build_ui()

    self.type_var.trace_add("write", self._on_type_changed)
    self.has_header_var.trace_add("write", self._on_header_or_path_changed)
    self.full_path_var.trace_add("write", self._on_header_or_path_changed)
    self.train_path_var.trace_add("write", self._on_header_or_path_changed)
    self._layout_display_var.trace_add("write", self._on_layout_display_changed)

    self._on_type_changed()
    self._sync_file_widgets()
    self._load_csv_columns()

  def _build_ui(self):
    main_frame = ttk.Frame(self, padding=(25, 20))
    main_frame.pack(fill=tk.BOTH, expand=True)

    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.BOTH, expand=True)
    form_frame.columnconfigure(0, weight=1)

    row = 0

    ttk.Label(form_frame, text=_("dataset.form.name"), foreground="#333333").grid(row=row, column=0, sticky="w", pady=(0, 2))
    row += 1
    ttk.Entry(form_frame, textvariable=self.name_var).grid(row=row, column=0, sticky="ew", pady=(0, 12))
    row += 1

    ttk.Label(form_frame, text=_("dataset.form.paradigm_type"), foreground="#333333").grid(row=row, column=0, sticky="w", pady=(0, 2))
    row += 1
    selector = ProblemTypeSelector(form_frame, type_var=self.type_var, initial_value=self.type_var.get())
    selector.grid(row=row, column=0, sticky="ew", pady=(0, 12))
    row += 1

    ttk.Label(form_frame, text=_("dataset.form.layout"), foreground="#333333").grid(row=row, column=0, sticky="w", pady=(0, 2))
    row += 1
    self.layout_combo = ttk.Combobox(
      form_frame,
      textvariable=self._layout_display_var,
      values=list(self._layout_display_to_value.keys()),
      state="readonly",
    )
    self.layout_combo.grid(row=row, column=0, sticky="ew", pady=(0, 12))
    row += 1

    ttk.Checkbutton(
      form_frame,
      text=_("dataset.form.has_header"),
      variable=self.has_header_var,
    ).grid(row=row, column=0, sticky="w", pady=(0, 12))
    row += 1

    self.full_label = ttk.Label(form_frame, text=_("dataset.form.file"), foreground="#333333")
    self.full_label.grid(row=row, column=0, sticky="w", pady=(0, 2))
    row += 1
    self.full_frame = ttk.Frame(form_frame)
    self.full_frame.grid(row=row, column=0, sticky="ew", pady=(0, 12))
    ttk.Entry(self.full_frame, textvariable=self.full_path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Button(self.full_frame, text=_("common.browse"), command=lambda: self._browse_into(self.full_path_var), width=8).pack(
      side=tk.RIGHT, padx=(5, 0)
    )
    row += 1

    self.train_label = ttk.Label(form_frame, text=_("dataset.form.train_file"), foreground="#333333")
    self.train_label.grid(row=row, column=0, sticky="w", pady=(0, 2))
    row += 1
    self.train_frame = ttk.Frame(form_frame)
    self.train_frame.grid(row=row, column=0, sticky="ew", pady=(0, 12))
    ttk.Entry(self.train_frame, textvariable=self.train_path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Button(self.train_frame, text=_("common.browse"), command=lambda: self._browse_into(self.train_path_var), width=8).pack(
      side=tk.RIGHT, padx=(5, 0)
    )
    row += 1

    self.test_label = ttk.Label(form_frame, text=_("dataset.form.test_file"), foreground="#333333")
    self.test_label.grid(row=row, column=0, sticky="w", pady=(0, 2))
    row += 1
    self.test_frame = ttk.Frame(form_frame)
    self.test_frame.grid(row=row, column=0, sticky="ew", pady=(0, 12))
    ttk.Entry(self.test_frame, textvariable=self.test_path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Button(self.test_frame, text=_("common.browse"), command=lambda: self._browse_into(self.test_path_var), width=8).pack(
      side=tk.RIGHT, padx=(5, 0)
    )
    row += 1

    self.target_label = ttk.Label(form_frame, text=_("dataset.form.target"), foreground="#333333")
    self.target_label.grid(row=row, column=0, sticky="w", pady=(0, 2))
    row += 1
    self.target_selector = ttk.Combobox(form_frame, textvariable=self.target_var, state="readonly")
    self.target_selector.grid(row=row, column=0, sticky="ew", pady=(0, 16))

    btn_text = _("dataset.form.update") if self.is_editing else _("dataset.form.save")
    ttk.Button(main_frame, text=btn_text, command=self._handle_save).pack(fill=tk.X, ipady=6)

  def _current_problem_type(self) -> ProblemType:
    return ProblemType(self.type_var.get())

  def _current_layout(self) -> DatasetLayout:
    return DatasetLayout(self.layout_var.get())

  def _is_supervised(self) -> bool:
    return self._current_problem_type() in SUPERVISED_TYPES

  def _on_layout_display_changed(self, *args) -> None:
    display = self._layout_display_var.get()
    value = self._layout_display_to_value.get(display, DatasetLayout.NO_SPLIT.value)
    self.layout_var.set(value)
    self._sync_file_widgets()
    self._load_csv_columns()

  def _on_type_changed(self, *args) -> None:
    if self._current_problem_type() in UNSUPERVISED_TYPES:
      self.layout_var.set(DatasetLayout.NO_SPLIT.value)
      self._layout_display_var.set(self._layout_value_to_display[DatasetLayout.NO_SPLIT.value])
      self.layout_combo.config(state="disabled")
      self.target_label.config(text=_("dataset.form.target_unused"))
      self.target_var.set("")
      self.target_selector.config(state="disabled")
    else:
      self.layout_combo.config(state="readonly")
      self.target_label.config(text=_("dataset.form.target"))
      self.target_selector.config(state="readonly")

    self._sync_file_widgets()
    self._load_csv_columns()

  def _on_header_or_path_changed(self, *args) -> None:
    self._load_csv_columns()

  def _sync_file_widgets(self) -> None:
    is_split = self._current_layout() == DatasetLayout.TRAIN_TEST_SPLIT

    if is_split:
      self.full_label.grid_remove()
      self.full_frame.grid_remove()
      self.train_label.grid()
      self.train_frame.grid()
      self.test_label.grid()
      self.test_frame.grid()
    else:
      self.train_label.grid_remove()
      self.train_frame.grid_remove()
      self.test_label.grid_remove()
      self.test_frame.grid_remove()
      self.full_label.grid()
      self.full_frame.grid()

  def _browse_into(self, var: tk.StringVar) -> None:
    filepath = filedialog.askopenfilename(
      parent=self,
      filetypes=[(_("common.filetypes.csv"), "*.csv")],
    )

    if filepath:
      var.set(filepath)

    self.lift()
    self.focus_force()

  def _primary_peek_path(self) -> str:
    if self._current_layout() == DatasetLayout.TRAIN_TEST_SPLIT:
      return self.train_path_var.get()

    return self.full_path_var.get()

  def _load_csv_columns(self, *args) -> None:
    filepath = self._primary_peek_path()

    if not filepath:
      self.target_selector["values"] = []
      return

    try:
      has_header = self.has_header_var.get()
      names = peek_column_names(filepath, has_header)
      labels = [
        format_target_display(i, names if has_header else None)
        for i in range(len(names))
      ]
      self.target_selector["values"] = labels

      if self._is_supervised() and labels:
        current = self.target_var.get()
        if current in labels:
          return

        try:
          idx = parse_target_display(current) if current else -1
          if 0 <= idx < len(labels):
            self.target_var.set(labels[idx])
            return
        except ValueError:
          pass

        self.target_var.set(labels[-1])
    except Exception as e:
      self.target_selector["values"] = []
      self.target_var.set("")
      print(f"Error reading CSV inside modal: {e}")

  def _handle_save(self) -> None:
    if not self.name_var.get().strip():
      messagebox.showerror(_("common.error"), _("dataset.form.err_name_file"), parent=self)
      return

    layout = self._current_layout()
    problem_type = self._current_problem_type()

    if layout == DatasetLayout.NO_SPLIT:
      if not self.full_path_var.get():
        messagebox.showerror(_("common.error"), _("dataset.form.err_name_file"), parent=self)
        return
      files = {DatasetFileRole.FULL.value: self.full_path_var.get()}
    else:
      if not self.train_path_var.get() or not self.test_path_var.get():
        messagebox.showerror(_("common.error"), _("dataset.form.err_train_test_files"), parent=self)
        return
      files = {
        DatasetFileRole.TRAIN.value: self.train_path_var.get(),
        DatasetFileRole.TEST.value: self.test_path_var.get(),
      }

    target_value: t.Optional[int] = None

    if problem_type in SUPERVISED_TYPES:
      raw = self.target_var.get().strip()

      if raw == "":
        messagebox.showerror(_("common.error"), _("dataset.form.err_target_required"), parent=self)
        return

      try:
        target_value = parse_target_display(raw)
      except ValueError:
        messagebox.showerror(_("common.error"), _("dataset.form.err_target_required"), parent=self)
        return

    dataset_payload = {
      "id": self.dataset_id,
      "name": self.name_var.get().strip(),
      "type": self.type_var.get(),
      "layout": layout.value,
      "has_header": self.has_header_var.get(),
      "files": files,
      "target": target_value,
    }

    try:
      self.on_save(dataset_payload)
    except Exception as e:
      messagebox.showerror(_("common.error"), str(e), parent=self)
      return

    self.destroy()
