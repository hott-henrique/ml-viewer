import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from application.components import HyperParamForm, SortableTreeview
from application.enums import ProblemType
from application.i18n import _, display_title, localize_enum
from application.managers import ModelManager

class ModelView(ttk.Frame):
  def __init__(self, parent: tk.Misc) -> None:
    super().__init__(parent)

    header_frame = ttk.Frame(self)
    header_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(header_frame, text=_("model.view.title"), font=("", 16, "bold")).pack(side=tk.LEFT)

    ttk.Button(header_frame, text=_("action.delete"), command=self.delete_model).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text=_("action.update"), command=self.update_model).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text=_("action.import"), command=self.import_model).pack(side=tk.RIGHT)

    table_frame = ttk.Frame(self)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("key", "name", "type", "source")
    self.tree = SortableTreeview(
      table_frame,
      columns=columns,
      display_columns=("name", "type", "source"),
      height=8,
    )

    self.tree.set_heading("key", _("common.id"), sortable=False)
    self.tree.column("key", width=0, stretch=tk.NO)

    self.tree.set_heading("name", _("common.name"))
    self.tree.set_heading("type", _("model.col.problem_type"))
    self.tree.set_heading("source", _("common.source"))

    self.tree.column("name", width=250)
    self.tree.column("type", width=120)
    self.tree.column("source", width=100)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.tree.bind("<<TreeviewSelect>>", self.on_model_selected)
    self.tree.bind_context_menu(self._build_context_menu)

    param_frame = ttk.LabelFrame(self, text=_("model.hyperparams.readonly"))
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
        source = _("common.custom") if model_config.plugin_path else _("common.native")
        self.tree.insert(
          "",
          tk.END,
          values=(
            name,
            display_title(model_config.title, name),
            localize_enum(problem_type),
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
    menu.add_command(label=_("common.update"), command=self.update_model)
    menu.add_command(label=_("common.delete"), command=self.delete_model)
    return menu

  def on_model_selected(self, event: object) -> None:
    rows = self._selected_rows()

    if len(rows) != 1:
      self.hyperparam_form.render_form([])
      return

    key, _title, _prob_type_label, _source = rows[0]
    # Find config by stable key across registries
    model_config = None
    for problem_type in (
      ProblemType.CLASSIFICATION,
      ProblemType.REGRESSION,
      ProblemType.CLUSTERING,
      ProblemType.DIMENSIONALITY_REDUCTION,
    ):
      model_config = ModelManager.registry(problem_type).get(str(key))
      if model_config:
        break

    if model_config:
      self.hyperparam_form.render_form(model_config.params)

  def import_model(self) -> None:
    filepath = filedialog.askopenfilename(filetypes=[(_("common.filetypes.python"), "*.py")])

    if not filepath:
      return

    try:
      added = ModelManager.import_from_file(filepath)
      messagebox.showinfo(_("common.success"), _("model.msg.imported").format(names=", ".join(added)))
      self.load_table_data()
    except Exception as e:
      messagebox.showerror(_("common.import_error"), str(e))

  def update_model(self) -> None:
    rows = self._selected_rows()

    if len(rows) != 1:
      messagebox.showwarning(_("common.warning"), _("model.msg.select_one_update"))
      return

    key, _title, _prob_type_label, source = rows[0]

    if self._is_native_source(str(source)):
      messagebox.showwarning(_("common.warning"), _("model.msg.cannot_update_native"))
      return

    filepath = filedialog.askopenfilename(
      title=_("model.msg.select_updated_py").format(name=key),
      filetypes=[(_("common.filetypes.python"), "*.py")],
    )

    if not filepath:
      return

    try:
      added = ModelManager.import_from_file(filepath)
      messagebox.showinfo(_("common.success"), _("model.msg.updated").format(names=", ".join(added)))
      self.load_table_data()
    except Exception as e:
      messagebox.showerror(_("common.update_error"), str(e))

  def delete_model(self) -> None:
    rows = self._selected_rows()

    if not rows:
      messagebox.showwarning(_("common.warning"), _("model.msg.select_delete"))
      return

    custom_rows = [row for row in rows if not self._is_native_source(str(row[3]))]
    skipped_native = len(rows) - len(custom_rows)

    if not custom_rows:
      messagebox.showerror(_("common.error"), _("model.err.native_cannot_delete"))
      return

    names = [str(row[0]) for row in custom_rows]
    if len(names) == 1:
      label = names[0]
    else:
      label = _("model.msg.n_models").format(n=len(names))

    extra = ""
    if skipped_native:
      extra = "\n" + _("model.msg.skip_native").format(n=skipped_native)

    if not messagebox.askyesno(
      _("common.confirm_delete"),
      _("model.msg.delete_confirm").format(
        label=label,
        extra=extra,
      ),
    ):
      return

    errors: list[str] = []

    for key, _title, _prob_type_label, _source in custom_rows:
      deleted = False
      for problem_type in (
        ProblemType.CLASSIFICATION,
        ProblemType.REGRESSION,
        ProblemType.CLUSTERING,
        ProblemType.DIMENSIONALITY_REDUCTION,
      ):
        if str(key) in ModelManager.registry(problem_type):
          try:
            ModelManager.delete_model(problem_type, str(key))
            deleted = True
          except Exception as e:
            errors.append(f"{key}: {e}")
          break
      if not deleted:
        errors.append(f"{key}: not found")

    self.hyperparam_form.render_form([])
    self.load_table_data()

    if errors:
      messagebox.showerror(
        _("common.delete_error"),
        _("model.msg.delete_partial") + "\n".join(errors),
      )
