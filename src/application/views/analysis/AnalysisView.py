import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from application.enums import ProblemType
from application.managers import AnalysisManager

class AnalysisView(ttk.Frame):
  def __init__(self, parent: tk.Misc) -> None:
    super().__init__(parent)

    header_frame = ttk.Frame(self)
    header_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(header_frame, text="Analyses Library", font=("", 16, "bold")).pack(side=tk.LEFT)

    ttk.Button(header_frame, text="Delete", command=self.delete_analysis).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text="Import", command=self.import_analysis).pack(side=tk.RIGHT)

    table_frame = ttk.Frame(self)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("name", "type", "output", "source")
    self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

    self.tree.heading("name", text="Analysis Name")
    self.tree.heading("type", text="Problem Type")
    self.tree.heading("output", text="Output Kind")
    self.tree.heading("source", text="Source")

    self.tree.column("name", width=220)
    self.tree.column("type", width=120)
    self.tree.column("output", width=100)
    self.tree.column("source", width=90)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.tree.bind("<<TreeviewSelect>>", self.on_analysis_selected)

    desc_frame = ttk.LabelFrame(self, text="Description")
    desc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=15)

    self.desc_text = tk.Text(desc_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#f5f5f5", height=6)
    self.desc_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    self.load_table_data()

  def load_table_data(self) -> None:
    for item in self.tree.get_children():
      self.tree.delete(item)

    for problem_type in (ProblemType.CLASSIFICATION, ProblemType.REGRESSION):
      for name, config in AnalysisManager.registry(problem_type).items():
        source = "Native" if config.is_native else "Custom"
        self.tree.insert("", tk.END, values=(name, problem_type.value, config.output_kind.value, source))

  def on_analysis_selected(self, event: object) -> None:
    selected = self.tree.selection()

    if not selected:
      return

    name, prob_type, _output, _source = self.tree.item(selected[0])["values"]
    config = AnalysisManager.registry(prob_type).get(name)

    self.desc_text.config(state=tk.NORMAL)
    self.desc_text.delete(1.0, tk.END)

    if config:
      self.desc_text.insert(tk.END, config.description or "(No description)")

    self.desc_text.config(state=tk.DISABLED)

  def import_analysis(self) -> None:
    filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])

    if not filepath:
      return

    try:
      added = AnalysisManager.import_from_file(filepath)
      messagebox.showinfo("Success", f"Successfully imported: {', '.join(added)}")
      self.load_table_data()
    except Exception as e:
      messagebox.showerror("Import Error", str(e))

  def delete_analysis(self) -> None:
    selected = self.tree.selection()

    if not selected:
      messagebox.showwarning("Warning", "Please select an analysis to delete.")
      return

    name, prob_type, _output, source = self.tree.item(selected[0])["values"]

    if source == "Native":
      messagebox.showerror("Error", "You cannot delete native analyses.")
      return

    if not messagebox.askyesno("Confirm Delete", f"Delete analysis '{name}' permanently?"):
      return

    try:
      AnalysisManager.delete_analysis(prob_type, name)
      self.desc_text.config(state=tk.NORMAL)
      self.desc_text.delete(1.0, tk.END)
      self.desc_text.config(state=tk.DISABLED)
      self.load_table_data()
    except Exception as e:
      messagebox.showerror("Delete Error", str(e))
