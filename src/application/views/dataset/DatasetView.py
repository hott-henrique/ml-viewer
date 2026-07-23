import tkinter as tk
from tkinter import ttk, messagebox

from application.managers import DatasetManager
from application.views.dataset import DatasetFormModal

class DatasetView(ttk.Frame):
  def __init__(self, parent):
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
    self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
    
    self.tree.heading("id", text="ID")
    self.tree.column("id", width=0, stretch=tk.NO) 

    self.tree.heading("name", text="Name")
    self.tree.heading("type", text="Type")
    self.tree.heading("target", text="Target")
    self.tree.heading("date", text="Added On")
    self.tree.heading("path", text="File Path")

    self.tree.column("name", width=120)
    self.tree.column("type", width=90)
    self.tree.column("target", width=90)
    self.tree.column("date", width=130)
    self.tree.column("path", width=250)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.load_table_data()

  def load_table_data(self):
    for item in self.tree.get_children():
      self.tree.delete(item)

    datasets = DatasetManager.get_all()

    for ds in datasets:
      target_val = ds.get("target", "N/A") 
      self.tree.insert("", tk.END, values=(ds.get("id", ""), ds["name"], ds["type"], target_val, ds["date"], ds["path"]))

  def open_add_modal(self):
    DatasetFormModal(self, on_save=self._on_dataset_saved)

  def open_edit_modal(self):
    selected_item = self.tree.selection()

    if not selected_item:
      messagebox.showwarning("Warning", "Please select a dataset to edit.")
      return

    values = self.tree.item(selected_item[0])["values"]
    dataset_data = {
      "id": str(values[0]),
      "name": values[1],
      "type": values[2],
      "target": values[3],
      "path": values[5]
    }

    DatasetFormModal(self, on_save=self._on_dataset_saved, dataset_data=dataset_data)

  def delete_dataset(self):
    selected_item = self.tree.selection()

    if not selected_item:
      messagebox.showwarning("Warning", "Please select a dataset to delete.")
      return

    values = self.tree.item(selected_item[0])["values"]
    dataset_id = str(values[0])
    dataset_name = values[1]
    dataset_path = values[5]

    confirm = messagebox.askyesno(
      "Confirm Delete", 
      f"Are you sure you want to delete '{dataset_name}'?\nThis action cannot be undone."
    )

    if confirm:
      DatasetManager.delete_dataset(dataset_id)

      self.load_table_data()

  def _on_dataset_saved(self, dataset_payload: dict):
    if dataset_payload.get("id"):
      DatasetManager.update_dataset(dataset_payload)
    else:
      DatasetManager.add_dataset(
        name=dataset_payload["name"], 
        filepath=dataset_payload["path"], 
        problem_type=dataset_payload["type"],
        target=dataset_payload["target"]
      )

    self.load_table_data()