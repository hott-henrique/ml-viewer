import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from application.components import HyperParamForm, SortableTreeview
from application.i18n import _, display_title
from application.managers import EnvironmentManager


class EnvironmentView(ttk.Frame):
  def __init__(self, parent: tk.Misc) -> None:
    super().__init__(parent)

    header_frame = ttk.Frame(self)
    header_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(header_frame, text=_("environment.view.title"), font=("", 16, "bold")).pack(side=tk.LEFT)

    ttk.Button(header_frame, text=_("action.delete"), command=self.delete_environment).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text=_("action.update"), command=self.update_environment).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text=_("action.import"), command=self.import_environment).pack(side=tk.RIGHT)

    table_frame = ttk.Frame(self)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("id", "name", "source", "version", "md5")
    self.tree = SortableTreeview(
      table_frame,
      columns=columns,
      display_columns=("name", "source", "version", "md5"),
      height=8,
    )

    self.tree.set_heading("id", _("common.id"), sortable=False)
    self.tree.column("id", width=0, stretch=tk.NO)

    self.tree.set_heading("name", _("common.name"))
    self.tree.set_heading("source", _("common.source"))
    self.tree.set_heading("version", _("common.version"))
    self.tree.set_heading("md5", _("common.md5"))

    self.tree.column("name", width=280)
    self.tree.column("source", width=100)
    self.tree.column("version", width=70)
    self.tree.column("md5", width=220)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.tree.bind("<<TreeviewSelect>>", self.on_environment_selected)
    self.tree.bind_context_menu(self._build_context_menu)

    param_frame = ttk.LabelFrame(self, text=_("environment.params.readonly"))
    param_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=15)

    self.hyperparam_form = HyperParamForm(param_frame, is_readonly=True)
    self.hyperparam_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    self._versions: dict[int, object] = {}
    self.load_table_data()

  def load_table_data(self) -> None:
    for item in self.tree.get_children():
      self.tree.delete(item)

    self._versions = {}

    for version in EnvironmentManager.list_versions():
      self._versions[version.id] = version
      source = _("common.native") if version.is_native else _("common.custom")
      self.tree.insert(
        "",
        tk.END,
        values=(
          version.id,
          display_title(version.title, version.name),
          source,
          version.version,
          version.md5_hash or "",
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
    menu.add_command(label=_("common.update"), command=self.update_environment)
    menu.add_command(label=_("common.delete"), command=self.delete_environment)
    return menu

  def on_environment_selected(self, event: object) -> None:
    rows = self._selected_rows()

    if len(rows) != 1:
      self.hyperparam_form.render_form([])
      return

    version = self._versions.get(int(rows[0][0]))
    if version:
      self.hyperparam_form.render_form(version.params)

  def import_environment(self) -> None:
    filepath = filedialog.askopenfilename(filetypes=[(_("common.filetypes.python"), "*.py")])

    if not filepath:
      return

    try:
      added = EnvironmentManager.import_from_file(filepath)
      messagebox.showinfo(
        _("common.success"),
        _("environment.msg.imported").format(names=", ".join(added)),
      )
      self.load_table_data()
    except Exception as e:
      messagebox.showerror(_("common.import_error"), str(e))

  def update_environment(self) -> None:
    rows = self._selected_rows()

    if len(rows) != 1:
      messagebox.showwarning(_("common.warning"), _("environment.msg.select_one_update"))
      return

    version = self._versions.get(int(rows[0][0]))
    source = rows[0][2]

    if version is None or self._is_native_source(str(source)):
      messagebox.showwarning(_("common.warning"), _("environment.msg.cannot_update_native"))
      return

    filepath = filedialog.askopenfilename(
      title=_("environment.msg.select_updated_py").format(name=version.name),
      filetypes=[(_("common.filetypes.python"), "*.py")],
    )

    if not filepath:
      return

    try:
      added = EnvironmentManager.import_from_file(filepath)
      messagebox.showinfo(
        _("common.success"),
        _("environment.msg.updated").format(names=", ".join(added)),
      )
      self.load_table_data()
    except Exception as e:
      messagebox.showerror(_("common.update_error"), str(e))
      self.load_table_data()

  def delete_environment(self) -> None:
    rows = self._selected_rows()

    if not rows:
      messagebox.showwarning(_("common.warning"), _("environment.msg.select_delete"))
      return

    custom_rows = [row for row in rows if not self._is_native_source(str(row[2]))]
    skipped_native = len(rows) - len(custom_rows)

    if not custom_rows:
      messagebox.showerror(_("common.error"), _("environment.err.native_cannot_delete"))
      return

    names = [str(row[1]) for row in custom_rows]
    extra = ""
    if skipped_native:
      extra = "\n" + _("environment.msg.skip_native").format(n=skipped_native)

    if not messagebox.askyesno(
      _("common.confirm"),
      _("environment.msg.confirm_delete").format(n=len(names)) + extra,
    ):
      return

    errors: list[str] = []
    for row in custom_rows:
      label = str(row[1])
      try:
        EnvironmentManager.delete_environment(int(row[0]))
      except Exception as e:
        errors.append(f"{label}: {e}")

    if errors:
      messagebox.showerror(_("common.error"), "\n".join(errors))

    self.load_table_data()
