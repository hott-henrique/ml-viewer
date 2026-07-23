import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from application.components import HyperParamForm

from application.managers import ModelManager

class ModelView(ttk.Frame):
  def __init__(self, parent):
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
    self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
    
    self.tree.heading("name", text="Model Name")
    self.tree.heading("type", text="Problem Type")
    self.tree.heading("source", text="Source")

    self.tree.column("name", width=250)
    self.tree.column("type", width=120)
    self.tree.column("source", width=100)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.tree.bind("<<TreeviewSelect>>", self.on_model_selected)

    param_frame = ttk.LabelFrame(self, text="Hyperparameters (Read-Only)")
    param_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=15)

    self.hyperparam_form = HyperParamForm(param_frame, is_readonly=True)
    self.hyperparam_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    self.load_table_data()

  def load_table_data(self):
    for item in self.tree.get_children():
      self.tree.delete(item)

    for name, model_config in ModelManager.registry("Classification").items():
      source = "Custom" if model_config.plugin_path else "Native"
      self.tree.insert("", tk.END, values=(name, "Classification", source))

    for name, model_config in ModelManager.registry("Regression").items():
      source = "Custom" if model_config.plugin_path else "Native"
      self.tree.insert("", tk.END, values=(name, "Regression", source))

  def on_model_selected(self, event):
    selected = self.tree.selection()
    if not selected:
      return

    values = self.tree.item(selected[0])["values"]
    name, prob_type, source = values

    registry = ModelManager.registry(prob_type)

    model_config = registry.get(name)

    if model_config:
      self.hyperparam_form.render_form(model_config.params)

  def import_model(self):
    filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if filepath:
      try:
        added = ModelManager.import_from_file(filepath)
        messagebox.showinfo("Success", f"Successfully imported: {', '.join(added)}")
        self.load_table_data()
      except Exception as e:
        messagebox.showerror("Import Error", str(e))

  def update_model(self):
    selected = self.tree.selection()
    if not selected:
      messagebox.showwarning("Warning", "Please select a custom model to update.")
      return

    values = self.tree.item(selected[0])["values"]
    name, prob_type, source = values

    if source == "Native":
      messagebox.showwarning("Warning", "You cannot update native models.")
      return

    filepath = filedialog.askopenfilename(title=f"Select updated .py for {name}", filetypes=[("Python Files", "*.py")])

    if filepath:
      try:
        added = ModelManager.import_from_file(filepath)

        messagebox.showinfo("Success", f"Successfully updated: {', '.join(added)}")

        self.load_table_data()

      except Exception as e:
        messagebox.showerror("Update Error", str(e))

  def delete_model(self):
    selected = self.tree.selection()
    if not selected:
      messagebox.showwarning("Warning", "Please select a model to delete.")
      return

    values = self.tree.item(selected[0])["values"]
    name, prob_type, source = values

    if source == "Native":
      messagebox.showerror("Error", "You cannot delete native models.")
      return

    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?\nThis will permanently remove the plugin file.")

    if confirm:
      ModelManager.delete_model(prob_type, name)

      self.hyperparam_form.render_form([])

      self.load_table_data()