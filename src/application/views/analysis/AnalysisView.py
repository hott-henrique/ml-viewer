import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from application.components import HyperParamForm, SortableTreeview
from application.enums import ProblemType
from application.i18n import _, display_title, localize_enum, resolve_text
from application.managers import AnalysisManager

class AnalysisView(ttk.Frame):
  def __init__(self, parent: tk.Misc) -> None:
    super().__init__(parent)

    header_frame = ttk.Frame(self)
    header_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(header_frame, text=_("analysis.view.title"), font=("", 16, "bold")).pack(side=tk.LEFT)

    ttk.Button(header_frame, text=_("common.delete"), command=self.delete_analysis).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text=_("common.import"), command=self.import_analysis).pack(side=tk.RIGHT)

    table_frame = ttk.Frame(self)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("key", "name", "type", "output", "source")
    self.tree = SortableTreeview(
      table_frame,
      columns=columns,
      display_columns=("name", "type", "output", "source"),
      height=10,
    )

    self.tree.set_heading("key", _("common.id"), sortable=False)
    self.tree.column("key", width=0, stretch=tk.NO)

    self.tree.set_heading("name", _("common.name"))
    self.tree.set_heading("type", _("model.col.problem_type"))
    self.tree.set_heading("output", _("analysis.col.output_kind"))
    self.tree.set_heading("source", _("common.source"))

    self.tree.column("name", width=220)
    self.tree.column("type", width=120)
    self.tree.column("output", width=100)
    self.tree.column("source", width=90)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.tree.bind("<<TreeviewSelect>>", self.on_analysis_selected)
    self.tree.bind_context_menu(self._build_context_menu)

    details_frame = ttk.Frame(self)
    details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=15)

    details_frame.columnconfigure(0, weight=1)
    details_frame.columnconfigure(1, weight=2)
    details_frame.rowconfigure(0, weight=1)

    param_frame = ttk.LabelFrame(details_frame, text=_("analysis.params.readonly"))
    param_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

    self.param_form = HyperParamForm(param_frame, is_readonly=True)
    self.param_form.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    desc_frame = ttk.LabelFrame(details_frame, text=_("common.description"))
    desc_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

    self.desc_text = tk.Text(desc_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#f5f5f5", height=6)
    self.desc_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    self.load_table_data()

  def load_table_data(self) -> None:
    for item in self.tree.get_children():
      self.tree.delete(item)

    for problem_type in (
      ProblemType.CLASSIFICATION,
      ProblemType.REGRESSION,
      ProblemType.CLUSTERING,
      ProblemType.DIMENSIONALITY_REDUCTION,
      ProblemType.ASSOCIATION_RULES,
      ProblemType.SEMI_SUPERVISED_CLASSIFICATION,
      ProblemType.SEMI_SUPERVISED_REGRESSION,
      ProblemType.REINFORCEMENT_LEARNING,
    ):
      for name, config in AnalysisManager.registry(problem_type).items():
        source = _("common.native") if config.is_native else _("common.custom")
        self.tree.insert(
          "",
          tk.END,
          values=(
            name,
            display_title(config.title, name),
            localize_enum(problem_type),
            localize_enum(config.output_kind),
            source,
          ),
        )

  def _selected_rows(self) -> list[tuple]:
    return [self.tree.item(iid)["values"] for iid in self.tree.selection()]

  def _is_native_source(self, source: str) -> bool:
    return source in (_("common.native"), "Native")

  def _build_context_menu(self, event: tk.Event) -> tk.Menu | None:
    if not self.tree.selection():
      return None

    menu = tk.Menu(self, tearoff=0)
    menu.add_command(label=_("common.delete"), command=self.delete_analysis)
    return menu

  def _clear_description(self) -> None:
    self.desc_text.config(state=tk.NORMAL)
    self.desc_text.delete(1.0, tk.END)
    self.desc_text.config(state=tk.DISABLED)

  def on_analysis_selected(self, event: object) -> None:
    rows = self._selected_rows()

    if len(rows) != 1:
      self.param_form.render_form([])
      self._clear_description()
      return

    key = str(rows[0][0])
    config = None
    for problem_type in (
      ProblemType.CLASSIFICATION,
      ProblemType.REGRESSION,
      ProblemType.CLUSTERING,
      ProblemType.DIMENSIONALITY_REDUCTION,
      ProblemType.ASSOCIATION_RULES,
      ProblemType.SEMI_SUPERVISED_CLASSIFICATION,
      ProblemType.SEMI_SUPERVISED_REGRESSION,
      ProblemType.REINFORCEMENT_LEARNING,
    ):
      config = AnalysisManager.registry(problem_type).get(key)
      if config:
        break

    if config:
      self.param_form.render_form(config.params)
    else:
      self.param_form.render_form([])

    self.desc_text.config(state=tk.NORMAL)
    self.desc_text.delete(1.0, tk.END)

    if config:
      text = resolve_text(config.description) or _("common.no_description")
      self.desc_text.insert(tk.END, text)

    self.desc_text.config(state=tk.DISABLED)

  def import_analysis(self) -> None:
    filepath = filedialog.askopenfilename(filetypes=[(_("common.filetypes.python"), "*.py")])

    if not filepath:
      return

    try:
      added = AnalysisManager.import_from_file(filepath)
      messagebox.showinfo(_("common.success"), _("model.msg.imported").format(names=", ".join(added)))
      self.load_table_data()
    except Exception as e:
      messagebox.showerror(_("common.import_error"), str(e))

  def delete_analysis(self) -> None:
    rows = self._selected_rows()

    if not rows:
      messagebox.showwarning(_("common.warning"), _("analysis.msg.select_delete"))
      return

    custom_rows = [row for row in rows if not self._is_native_source(str(row[4]))]
    skipped_native = len(rows) - len(custom_rows)

    if not custom_rows:
      messagebox.showerror(_("common.error"), _("analysis.err.native_cannot_delete"))
      return

    names = [str(row[0]) for row in custom_rows]
    if len(names) == 1:
      label = names[0]
    else:
      label = _("analysis.msg.n_analyses").format(n=len(names))

    extra = ""
    if skipped_native:
      extra = "\n" + _("analysis.msg.skip_native").format(n=skipped_native)

    if not messagebox.askyesno(
      _("common.confirm_delete"),
      _("analysis.msg.delete_confirm").format(label=label, extra=extra),
    ):
      return

    errors: list[str] = []

    for key, _title, _type, _output, _source in custom_rows:
      deleted = False
      for problem_type in (
        ProblemType.CLASSIFICATION,
        ProblemType.REGRESSION,
        ProblemType.CLUSTERING,
        ProblemType.DIMENSIONALITY_REDUCTION,
        ProblemType.ASSOCIATION_RULES,
        ProblemType.SEMI_SUPERVISED_CLASSIFICATION,
        ProblemType.SEMI_SUPERVISED_REGRESSION,
        ProblemType.REINFORCEMENT_LEARNING,
      ):
        if str(key) in AnalysisManager.registry(problem_type):
          try:
            AnalysisManager.delete_analysis(problem_type, str(key))
            deleted = True
          except Exception as e:
            errors.append(f"{key}: {e}")
          break
      if not deleted:
        errors.append(f"{key}: not found")

    self.param_form.render_form([])
    self._clear_description()
    self.load_table_data()

    if errors:
      messagebox.showerror(
        _("common.delete_error"),
        _("analysis.msg.delete_partial") + "\n".join(errors),
      )
