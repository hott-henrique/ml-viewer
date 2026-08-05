import tkinter as tk
from tkinter import ttk
import pandas as pd

from application.enums import ProblemType
from application.i18n import _, localize_enum

class DatasetHandler(ttk.LabelFrame):

  def __init__(self, master=None, on_target_change=None, on_split_change=None, on_type_change=None):
    super().__init__(master, text=_("dataset.handler.title"), padding=(10, 10))

    self.on_target_change = on_target_change
    self.on_split_change = on_split_change
    self.on_type_change = on_type_change

    self._type_label_to_value = {
      localize_enum(ProblemType.CLASSIFICATION): ProblemType.CLASSIFICATION.value,
      localize_enum(ProblemType.REGRESSION): ProblemType.REGRESSION.value,
    }
    self._display_type_var = tk.StringVar(value=localize_enum(ProblemType.CLASSIFICATION))
    self.type_var = tk.StringVar(value=ProblemType.CLASSIFICATION.value)
    self.target_var = tk.StringVar()
    self.split_var = tk.StringVar(value="0.8")

    self._display_type_var.trace_add("write", self._handle_display_type_update)
    self.target_var.trace_add("write", self._handle_target_update)
    self.split_var.trace_add("write", self._handle_split_update)

    type_row = ttk.Frame(self)
    type_row.pack(fill=tk.X)

    target_row = ttk.Frame(self)
    target_row.pack(fill=tk.X)

    split_row = ttk.Frame(self)
    split_row.pack(fill=tk.X)

    ttk.Label(type_row, text=_("dataset.handler.problem_type")).pack(side=tk.LEFT, padx=10, pady=10)

    self.type_selector = ttk.Combobox(
      type_row,
      textvariable=self._display_type_var,
      values=list(self._type_label_to_value.keys()),
      state="readonly",
      width=20,
    )

    self.type_selector.pack(side=tk.LEFT, padx=10, pady=10)

    ttk.Label(target_row, text=_("dataset.form.target")).pack(side=tk.LEFT, padx=10, pady=10)

    self.target_selector = ttk.Combobox(
      target_row,
      textvariable=self.target_var,
      state="readonly",
      width=20,
    )

    self.target_selector.pack(side=tk.LEFT, padx=10, pady=10)

    vcmd = (self.register(self.validate_split), '%P')

    ttk.Label(split_row, text=_("dataset.handler.train_size")).pack(side=tk.LEFT, padx=10, pady=10)

    self.split_input = ttk.Entry(
      split_row,
      textvariable=self.split_var,
      width=10,
      validate="key",
      validatecommand=vcmd,
    )
    self.split_input.pack(side=tk.LEFT, padx=10, pady=10)

    self._handle_display_type_update()

  def _handle_display_type_update(self, *args):
    canonical = self._type_label_to_value.get(self._display_type_var.get(), ProblemType.CLASSIFICATION.value)
    self.type_var.set(canonical)

    if self.on_type_change:
      self.on_type_change(canonical)

  def _handle_target_update(self, *args):
    if self.on_target_change:
      self.on_target_change(self.target_var.get())

  def _handle_split_update(self, *args):
    if self.on_split_change:
      self.on_split_change(self.split_var.get())

  def validate_split(self, typed_value):
    if typed_value == "":
      return True

    if typed_value in ("0", "0.", "1", "1."):
      return True

    try:
      value = float(typed_value)
      return 0.0 <= value <= 1.0
    except ValueError:
      return False

  def load_columns(self, filepath):
    try:
      df = pd.read_csv(filepath, nrows=0)
      columns = df.columns.tolist()

      self.target_selector['values'] = columns

      if columns:
        self.target_selector.set(columns[-1])

    except Exception as e:
      print(f"Error reading CSV: {e}")
      self.target_selector['values'] = []
      self.target_var.set(_("common.error_loading"))
