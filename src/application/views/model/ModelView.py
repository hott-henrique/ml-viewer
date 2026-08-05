import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from application.components import HyperParamForm, SortableTreeview
from application.enums import ProblemType
from application.managers import ModelManager

class ModelView(ttk.Frame):
  def __init__(self, parent: tk.Misc) -> None:
    super().__init__(parent)

    header_frame = ttk.Frame(self)
    header_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(header_frame, text="🧠 Models Library", font=("", 16, "bold")).pack(side=tk.LEFT)

    ttk.Button(header_frame, text="🗑️ Delete", command=self.delete_model).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text="🔄 Update", command=self.update_model).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text="📥 Import", command=self.import_model).pack(side=tk.RIGHT)

    table_frame = ttk.Frame(self)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("name", "type", "source")
    self.tree = SortableTreeview(table_frame, columns=columns, height=8)

    self.tree.set_heading("name", "Model Name")
    self.tree.set_heading("type", "Problem Type")
    self.tree.set_heading("source", "Source")

    self.tree.column("name", width=250)
    self.tree.column("type", width=120)
    self.tree.column("source", width=100)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.tree.bind("<<TreeviewSelect>>", self.on_model_selected)
    self.tree.bind_context_menu(self._build_context_menu)

    param_frame = ttk.LabelFrame(self, text="Hyperparameters (Read-Only)")
    param_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=15)

    self.hyperparam_form = HyperParamForm(param_frame, is_readonly=True)
    self.hyperparam_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    self.load_table_data()

  def load_table_data(self) -> None:
    for item in self.tree.get_children():
      self.tree.delete(item)

    for problem_type in (
      ProblemType.CLASSIFICATION,
      ProblemType.REGRESSION,
      ProblemType.CLUSTERING,
      ProblemType.DIMENSIONALITY_REDUCTION,
    ):
      for name, model_config in ModelManager.registry(problem_type).items():
        source = "Custom" if model_config.plugin_path else "Native"
        self.tree.insert("", tk.END, values=(name, problem_type.value, source))

  def _selected_rows(self) -> list[tuple]:
    return [self.tree.item(iid)["values"] for iid in self.tree.selection()]

  def _build_context_menu(self, event: tk.Event) -> tk.Menu | None:
    if not self.tree.selection():
      return None

    menu = tk.Menu(self, tearoff=0)
    menu.add_command(label="Update", command=self.update_model)
    menu.add_command(label="Delete", command=self.delete_model)
    return menu

  def on_model_selected(self, event: object) -> None:
    rows = self._selected_rows()

    if len(rows) != 1:
      self.hyperparam_form.render_form([])
      return

    name, prob_type, _source = rows[0]
    model_config = ModelManager.registry(prob_type).get(name)

    if model_config:
      self.hyperparam_form.render_form(model_config.params)

  def import_model(self) -> None:
    filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])

    if not filepath:
      return

    try:
      added = ModelManager.import_from_file(filepath)
      messagebox.showinfo("Success", f"Successfully imported: {', '.join(added)}")
      self.load_table_data()
    except Exception as e:
      messagebox.showerror("Import Error", str(e))

  def update_model(self) -> None:
    rows = self._selected_rows()

    if len(rows) != 1:
      messagebox.showwarning("Warning", "Please select exactly one custom model to update.")
      return

    name, prob_type, source = rows[0]

    if source == "Native":
      messagebox.showwarning("Warning", "You cannot update native models.")
      return

    filepath = filedialog.askopenfilename(
      title=f"Select updated .py for {name}",
      filetypes=[("Python Files", "*.py")],
    )

    if not filepath:
      return

    try:
      added = ModelManager.import_from_file(filepath)
      messagebox.showinfo("Success", f"Successfully updated: {', '.join(added)}")
      self.load_table_data()
    except Exception as e:
      messagebox.showerror("Update Error", str(e))

  def delete_model(self) -> None:
    rows = self._selected_rows()

    if not rows:
      messagebox.showwarning("Warning", "Please select at least one model to delete.")
      return

    custom_rows = [row for row in rows if row[2] != "Native"]
    skipped_native = len(rows) - len(custom_rows)

    if not custom_rows:
      messagebox.showerror("Error", "Native models cannot be deleted.")
      return

    names = [str(row[0]) for row in custom_rows]
    label = names[0] if len(names) == 1 else f"{len(names)} models"
    extra = f"\n({skipped_native} native model(s) will be skipped.)" if skipped_native else ""

    if not messagebox.askyesno(
      "Confirm Delete",
      f"Delete {label} permanently?{extra}\nThis will permanently remove the plugin file(s).",
    ):
      return

    errors: list[str] = []

    for name, prob_type, _source in custom_rows:
      try:
        ModelManager.delete_model(prob_type, name)
      except Exception as e:
        errors.append(f"{name}: {e}")

    self.hyperparam_form.render_form([])
    self.load_table_data()

    if errors:
      messagebox.showerror("Delete Error", "Some models could not be deleted:\n\n" + "\n".join(errors))
