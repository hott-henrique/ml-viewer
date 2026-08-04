import tkinter as tk
from tkinter import ttk, messagebox

from application.components import SortableTreeview
from application.managers import DatasetManager
from application.views.dataset import DatasetFormModal

class DatasetView(ttk.Frame):
  def __init__(self, parent: tk.Misc) -> None:
    super().__init__(parent)

    header_frame = ttk.Frame(self)
    header_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(header_frame, text="📁 Datasets Library", font=("", 16, "bold")).pack(side=tk.LEFT)

    ttk.Button(header_frame, text="🗑️ Delete", command=self.delete_dataset).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text="✏️ Edit", command=self.open_edit_modal).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text="➕ Add", command=self.open_add_modal).pack(side=tk.RIGHT)

    table_frame = ttk.Frame(self)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("id", "name", "type", "target", "date", "path")
    self.tree = SortableTreeview(table_frame, columns=columns, height=12)

    self.tree.set_heading("id", "ID", sortable=False)
    self.tree.column("id", width=0, stretch=tk.NO)

    self.tree.set_heading("name", "Name")
    self.tree.set_heading("type", "Type")
    self.tree.set_heading("target", "Target")
    self.tree.set_heading("date", "Added On")
    self.tree.set_heading("path", "File Path")

    self.tree.column("name", width=120)
    self.tree.column("type", width=90)
    self.tree.column("target", width=90)
    self.tree.column("date", width=130)
    self.tree.column("path", width=250)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.tree.bind("<Double-1>", self._on_double_click)
    self.tree.bind_context_menu(self._build_context_menu)

    self.load_table_data()

  def load_table_data(self) -> None:
    for item in self.tree.get_children():
      self.tree.delete(item)

    for ds in DatasetManager.get_all():
      self.tree.insert("", tk.END, values=(ds.id, ds.name, ds.type, ds.target, ds.date, ds.path))

  def _selected_rows(self) -> list[tuple]:
    return [self.tree.item(iid)["values"] for iid in self.tree.selection()]

  def _build_context_menu(self, event: tk.Event) -> tk.Menu | None:
    if not self.tree.selection():
      return None

    menu = tk.Menu(self, tearoff=0)
    menu.add_command(label="Edit", command=self.open_edit_modal)
    menu.add_command(label="Delete", command=self.delete_dataset)
    return menu

  def _on_double_click(self, event: tk.Event) -> None:
    if self.tree.identify_row(event.y):
      self.open_edit_modal()

  def open_add_modal(self) -> None:
    DatasetFormModal(self, on_save=self._on_dataset_saved)

  def open_edit_modal(self) -> None:
    rows = self._selected_rows()

    if len(rows) != 1:
      messagebox.showwarning("Warning", "Please select exactly one dataset to edit.")
      return

    values = rows[0]
    dataset_data = {
      "id": str(values[0]),
      "name": values[1],
      "type": values[2],
      "target": values[3],
      "path": values[5],
    }

    DatasetFormModal(self, on_save=self._on_dataset_saved, dataset_data=dataset_data)

  def delete_dataset(self) -> None:
    rows = self._selected_rows()

    if not rows:
      messagebox.showwarning("Warning", "Please select at least one dataset to delete.")
      return

    names = [str(row[1]) for row in rows]
    label = names[0] if len(names) == 1 else f"{len(names)} datasets"

    if not messagebox.askyesno(
      "Confirm Delete",
      f"Delete {label} permanently?\nThis action cannot be undone.",
    ):
      return

    errors: list[str] = []

    for row in rows:
      dataset_id = str(row[0])
      dataset_name = str(row[1])

      try:
        DatasetManager.delete_dataset(dataset_id)
      except Exception as e:
        errors.append(f"{dataset_name}: {e}")

    self.load_table_data()

    if errors:
      messagebox.showerror(
        "Delete Error",
        "Some datasets could not be deleted (they may be used by experiments):\n\n" + "\n".join(errors),
      )

  def _on_dataset_saved(self, dataset_payload: dict) -> None:
    if dataset_payload.get("id"):
      DatasetManager.update_dataset(dataset_payload)
    else:
      DatasetManager.add_dataset(
        name=dataset_payload["name"],
        filepath=dataset_payload["path"],
        problem_type=dataset_payload["type"],
        target=dataset_payload["target"],
      )

    self.load_table_data()
