import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd

from application.components import ProblemTypeSelector

class DatasetFormModal(tk.Toplevel):

  def __init__(self, parent, on_save, dataset_data=None):
    super().__init__(parent)

    self.is_editing = dataset_data is not None
    self.title("Edit Dataset" if self.is_editing else "Add New Dataset")

    self.geometry("400x400")
    self.resizable(False, False)
    self.grab_set()

    self.on_save = on_save

    data = dataset_data or {}
    self.dataset_id = data.get("id")
    
    self.name_var = tk.StringVar(value=data.get("name", ""))
    self.type_var = tk.StringVar(value=data.get("type", "Classification"))
    self.path_var = tk.StringVar(value=data.get("path", ""))
    self.target_var = tk.StringVar(value=data.get("target", ""))

    self.path_var.trace_add("write", self._load_csv_columns)

    self._build_ui()

    if self.path_var.get():
      self._load_csv_columns()

  def _build_ui(self):
    main_frame = ttk.Frame(self, padding=(25, 20))
    main_frame.pack(fill=tk.BOTH, expand=True)

    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.BOTH, expand=True)
    form_frame.columnconfigure(0, weight=1)

    ttk.Label(form_frame, text="Dataset Name:", foreground="#333333").grid(row=0, column=0, sticky="w", pady=(0, 2))
    ttk.Entry(form_frame, textvariable=self.name_var).grid(row=1, column=0, sticky="ew", pady=(0, 15))

    ttk.Label(form_frame, text="Paradigm & Problem Type:", foreground="#333333").grid(row=2, column=0, sticky="w", pady=(0, 2))

    selector = ProblemTypeSelector(form_frame, type_var=self.type_var, initial_value=self.type_var.get())
    selector.grid(row=3, column=0, sticky="ew", pady=(0, 15))
    
    ttk.Label(form_frame, text="File (CSV):", foreground="#333333").grid(row=4, column=0, sticky="w", pady=(0, 2))
    
    file_frame = ttk.Frame(form_frame)
    file_frame.grid(row=5, column=0, sticky="ew", pady=(0, 15))
    
    ttk.Entry(file_frame, textvariable=self.path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Button(file_frame, text="Browse", command=self._browse_file, width=8).pack(side=tk.RIGHT, padx=(5, 0))

    ttk.Label(form_frame, text="Target Variable:", foreground="#333333").grid(row=6, column=0, sticky="w", pady=(0, 2))
    self.target_selector = ttk.Combobox(form_frame, textvariable=self.target_var, state="readonly")
    self.target_selector.grid(row=7, column=0, sticky="ew", pady=(0, 20))

    btn_text = "Update Dataset" if self.is_editing else "Save Dataset"

    save_btn = ttk.Button(main_frame, text=btn_text, command=self._handle_save)
    save_btn.pack(fill=tk.X, ipady=6)

  def _browse_file(self):
    filepath = filedialog.askopenfilename(
      parent=self, 
      filetypes=[("CSV Files", "*.csv")]
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

      self.target_selector['values'] = columns

      if columns and not self.target_var.get():
        self.target_var.set(columns[-1])

    except Exception as e:
      self.target_selector['values'] = []
      self.target_var.set("")
      print(f"Error reading CSV inside modal: {e}")

  def _handle_save(self):
    if not self.name_var.get() or not self.path_var.get() or not self.target_var.get():
      messagebox.showerror("Error", "Name, File, and Target Variable are required.", parent=self)
      return

    dataset_payload = {
      "id": self.dataset_id,
      "name": self.name_var.get(),
      "type": self.type_var.get(),
      "path": self.path_var.get(),
      "target": self.target_var.get()
    }

    self.on_save(dataset_payload)
    self.destroy()