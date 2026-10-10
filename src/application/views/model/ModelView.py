import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from application.components import HyperParamForm, SortableTreeview
from application.enums import ProblemType
from application.i18n import _, display_title, localize_enum
from application.managers import EnvironmentManager, ModelManager
from application.views.model.AgentCompatModal import AgentCompatModal


class ModelView(ttk.Frame):
  def __init__(self, parent: tk.Misc) -> None:
    super().__init__(parent)

    self._selected_agent: str | None = None
    self._compat_vars: dict[str, tk.BooleanVar] = {}

    header_frame = ttk.Frame(self)
    header_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(header_frame, text=_("model.view.title"), font=("", 16, "bold")).pack(side=tk.LEFT)

    ttk.Button(header_frame, text=_("action.delete"), command=self.delete_model).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text=_("action.update"), command=self.update_model).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text=_("action.import"), command=self.import_model).pack(side=tk.RIGHT)

    table_frame = ttk.Frame(self)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("id", "name", "type", "source", "version", "md5")
    self.tree = SortableTreeview(
      table_frame,
      columns=columns,
      display_columns=("name", "type", "source", "version", "md5"),
      height=8,
    )

    self.tree.set_heading("id", _("common.id"), sortable=False)
    self.tree.column("id", width=0, stretch=tk.NO)

    self.tree.set_heading("name", _("common.name"))
    self.tree.set_heading("type", _("model.col.problem_type"))
    self.tree.set_heading("source", _("common.source"))
    self.tree.set_heading("version", _("common.version"))
    self.tree.set_heading("md5", _("common.md5"))

    self.tree.column("name", width=250)
    self.tree.column("type", width=120)
    self.tree.column("source", width=100)
    self.tree.column("version", width=70)
    self.tree.column("md5", width=220)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.tree.bind("<<TreeviewSelect>>", self.on_model_selected)
    self.tree.bind_context_menu(self._build_context_menu)

    param_frame = ttk.LabelFrame(self, text=_("model.hyperparams.readonly"))
    param_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(15, 5))

    self.hyperparam_form = HyperParamForm(param_frame, is_readonly=True)
    self.hyperparam_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    self.compat_frame = ttk.LabelFrame(self, text=_("model.compat.panel_title"))
    self.compat_inner = ttk.Frame(self.compat_frame, padding=(8, 6))
    self.compat_inner.pack(fill=tk.BOTH, expand=True)
    self.compat_save_btn = ttk.Button(
      self.compat_frame,
      text=_("model.compat.save"),
      command=self._save_compat_panel,
    )
    self.compat_save_btn.pack(anchor=tk.E, padx=10, pady=(0, 8))

    self._versions: dict[int, object] = {}
    self.load_table_data()

  def load_table_data(self) -> None:
    for item in self.tree.get_children():
      self.tree.delete(item)

    self._versions = {}

    for version in ModelManager.list_versions():
      self._versions[version.id] = version
      source = _("common.native") if version.is_native else _("common.custom")
      self.tree.insert(
        "",
        tk.END,
        values=(
          version.id,
          display_title(version.title, version.name),
          localize_enum(version.problem_type),
          source,
          version.version,
          version.md5_hash or "",
        ),
      )

  def _selected_rows(self) -> list[tuple]:
    return [self.tree.item(iid)["values"] for iid in self.tree.selection()]

  def _is_native_source(self, source: str) -> bool:
    return source in (_("common.native"), "Native")

  def _find_model(self, key: str):
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
      model_config = ModelManager.registry(problem_type).get(str(key))
      if model_config:
        return problem_type, model_config
    return None, None

  def _build_context_menu(self, event: tk.Event) -> tk.Menu | None:
    if not self.tree.selection():
      return None

    menu = tk.Menu(self, tearoff=0)
    menu.add_command(label=_("common.update"), command=self.update_model)
    menu.add_command(label=_("common.delete"), command=self.delete_model)
    return menu

  def _clear_compat_panel(self) -> None:
    self._selected_agent = None
    self._compat_vars = {}
    for child in self.compat_inner.winfo_children():
      child.destroy()
    self.compat_frame.pack_forget()

  def _render_compat_panel(self, agent_name: str) -> None:
    self._selected_agent = agent_name
    self._compat_vars = {}
    for child in self.compat_inner.winfo_children():
      child.destroy()

    current = set(EnvironmentManager.envs_for_agent(agent_name))
    kinds = EnvironmentManager.kind_options()
    if not kinds:
      ttk.Label(self.compat_inner, text=_("model.compat.no_environments"), foreground="#666666").pack(
        anchor=tk.W
      )
    else:
      for kind in kinds:
        config = EnvironmentManager.kind_config(kind)
        label = display_title(config.title, kind)
        var = tk.BooleanVar(value=kind in current)
        self._compat_vars[kind] = var
        ttk.Checkbutton(self.compat_inner, text=label, variable=var).pack(anchor=tk.W, pady=1)

    self.compat_frame.pack(fill=tk.X, padx=10, pady=(0, 15))

  def _save_compat_panel(self) -> None:
    if not self._selected_agent:
      return
    selected = [kind for kind, var in self._compat_vars.items() if var.get()]
    try:
      EnvironmentManager.set_compat_for_agent(self._selected_agent, selected)
      messagebox.showinfo(_("common.success"), _("model.compat.saved"))
    except Exception as e:
      messagebox.showerror(_("common.error"), str(e))

  def _prompt_compat_for_rl_imports(self, added: list[str]) -> None:
    rl_registry = ModelManager.registry(ProblemType.REINFORCEMENT_LEARNING)
    for name in added:
      if name not in rl_registry:
        continue
      initial = EnvironmentManager.envs_for_agent(name)
      chosen = AgentCompatModal.ask(self, agent_name=name, initial_kinds=initial)
      if chosen is None:
        messagebox.showwarning(
          _("common.warning"),
          _("model.compat.skipped").format(agent=name),
        )
        continue
      try:
        EnvironmentManager.set_compat_for_agent(name, chosen)
      except Exception as e:
        messagebox.showerror(_("common.error"), str(e))

  def on_model_selected(self, event: object) -> None:
    rows = self._selected_rows()

    if len(rows) != 1:
      self.hyperparam_form.render_form([])
      self._clear_compat_panel()
      return

    version = self._versions.get(int(rows[0][0]))

    if version:
      self.hyperparam_form.render_form(version.params)
    else:
      self.hyperparam_form.render_form([])

    if version and version.problem_type == ProblemType.REINFORCEMENT_LEARNING:
      self._render_compat_panel(version.name)
    else:
      self._clear_compat_panel()

  def import_model(self) -> None:
    filepath = filedialog.askopenfilename(filetypes=[(_("common.filetypes.python"), "*.py")])

    if not filepath:
      return

    try:
      added = ModelManager.import_from_file(filepath)
      self._prompt_compat_for_rl_imports(added)
      messagebox.showinfo(_("common.success"), _("model.msg.imported").format(names=", ".join(added)))
      self.load_table_data()
    except Exception as e:
      messagebox.showerror(_("common.import_error"), str(e))

  def update_model(self) -> None:
    rows = self._selected_rows()

    if len(rows) != 1:
      messagebox.showwarning(_("common.warning"), _("model.msg.select_one_update"))
      return

    version = self._versions.get(int(rows[0][0]))
    source = rows[0][3]

    if version is None or self._is_native_source(str(source)):
      messagebox.showwarning(_("common.warning"), _("model.msg.cannot_update_native"))
      return

    filepath = filedialog.askopenfilename(
      title=_("model.msg.select_updated_py").format(name=version.name),
      filetypes=[(_("common.filetypes.python"), "*.py")],
    )

    if not filepath:
      return

    try:
      added = ModelManager.import_from_file(filepath)
      self._prompt_compat_for_rl_imports(added)
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

    names = [str(row[1]) for row in custom_rows]
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

    for row in custom_rows:
      label = str(row[1])
      try:
        ModelManager.delete_model(int(row[0]))
      except Exception as e:
        errors.append(f"{label}: {e}")

    self.hyperparam_form.render_form([])
    self._clear_compat_panel()
    self.load_table_data()

    if errors:
      messagebox.showerror(
        _("common.delete_error"),
        _("model.msg.delete_partial") + "\n".join(errors),
      )
