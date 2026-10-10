import tkinter as tk
from tkinter import ttk, messagebox

from application.components import SortableTreeview
from application.enums import DatasetLayout
from application.i18n import _, localize_enum
from application.managers import DatasetManager
from application.managers.DatasetManager import format_target_display, peek_column_names
from application.views.dataset import DatasetFormModal

class DatasetView(ttk.Frame):
  def __init__(self, parent: tk.Misc) -> None:
    super().__init__(parent)

    header_frame = ttk.Frame(self)
    header_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(header_frame, text=_("dataset.view.title"), font=("", 16, "bold")).pack(side=tk.LEFT)

    ttk.Button(header_frame, text=_("action.delete"), command=self.delete_dataset).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text=_("action.update"), command=self.open_edit_modal).pack(side=tk.RIGHT, padx=(5, 0))
    ttk.Button(header_frame, text=_("action.add"), command=self.open_add_modal).pack(side=tk.RIGHT)

    table_frame = ttk.Frame(self)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("id", "name", "type", "layout", "target", "date", "version", "md5")
    self.tree = SortableTreeview(table_frame, columns=columns, height=12)

    self.tree.set_heading("id", _("common.id"), sortable=False)
    self.tree.column("id", width=0, stretch=tk.NO)

    self.tree.set_heading("name", _("common.name"))
    self.tree.set_heading("type", _("common.type"))
    self.tree.set_heading("layout", _("dataset.col.layout"))
    self.tree.set_heading("target", _("dataset.col.target"))
    self.tree.set_heading("date", _("dataset.col.added_on"))
    self.tree.set_heading("version", _("common.version"))
    self.tree.set_heading("md5", _("common.md5"))

    self.tree.column("name", width=110)
    self.tree.column("type", width=90)
    self.tree.column("layout", width=110)
    self.tree.column("target", width=120)
    self.tree.column("date", width=120)
    self.tree.column("version", width=70)
    self.tree.column("md5", width=220)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    self.tree.bind("<Double-1>", self._on_double_click)
    self.tree.bind_context_menu(self._build_context_menu)

    self.load_table_data()

  def _format_target_cell(self, ds) -> str:
    if ds.target is None:
      return "—"

    if not ds.has_header:
      return str(ds.target)

    try:
      names = peek_column_names(ds.path, True)
      return format_target_display(ds.target, names)
    except Exception:
      return str(ds.target)

  def load_table_data(self) -> None:
    for item in self.tree.get_children():
      self.tree.delete(item)

    for ds in DatasetManager.get_all():
      self.tree.insert(
        "",
        tk.END,
        values=(
          ds.id,
          ds.name,
          localize_enum(ds.type),
          localize_enum(ds.layout),
          self._format_target_cell(ds),
          ds.date,
          ds.version,
          ds.md5_hash,
        ),
      )

  def _selected_rows(self) -> list[tuple]:
    return [self.tree.item(iid)["values"] for iid in self.tree.selection()]

  def _build_context_menu(self, event: tk.Event) -> tk.Menu | None:
    if not self.tree.selection():
      return None

    menu = tk.Menu(self, tearoff=0)
    menu.add_command(label=_("common.update"), command=self.open_edit_modal)
    menu.add_command(label=_("common.delete"), command=self.delete_dataset)
    return menu

  def _on_double_click(self, event: tk.Event) -> None:
    if self.tree.identify_row(event.y):
      self.open_edit_modal()

  def open_add_modal(self) -> None:
    DatasetFormModal(self, on_save=self._on_dataset_saved)

  def open_edit_modal(self) -> None:
    rows = self._selected_rows()

    if len(rows) != 1:
      messagebox.showwarning(_("common.warning"), _("dataset.msg.select_one_edit"))
      return

    values = rows[0]
    dataset_id = str(values[0])

    dataset = next((ds for ds in DatasetManager.get_all() if str(ds.id) == dataset_id), None)

    if dataset is None:
      messagebox.showerror(_("common.error"), _("dataset.err.not_found").format(id=dataset_id))
      return

    dataset_data = {
      "id": dataset_id,
      "name": dataset.name,
      "type": dataset.type.value,
      "target": dataset.target,
      "has_header": dataset.has_header,
      "layout": dataset.layout.value,
      "path": dataset.path,
      "full_path": dataset.path if dataset.layout == DatasetLayout.NO_SPLIT else "",
      "train_path": dataset.train_path if dataset.layout == DatasetLayout.TRAIN_TEST_SPLIT else "",
      "test_path": (
        dataset.test_path
        if dataset.layout in (DatasetLayout.TRAIN_TEST_SPLIT, DatasetLayout.LABELED_UNLABELED)
        else ""
      ),
      "labeled_path": dataset.labeled_path if dataset.layout == DatasetLayout.LABELED_UNLABELED else "",
      "unlabeled_path": dataset.unlabeled_path if dataset.layout == DatasetLayout.LABELED_UNLABELED else "",
    }

    DatasetFormModal(self, on_save=self._on_dataset_saved, dataset_data=dataset_data)

  def delete_dataset(self) -> None:
    rows = self._selected_rows()

    if not rows:
      messagebox.showwarning(_("common.warning"), _("dataset.msg.select_one_delete"))
      return

    names = [str(row[1]) for row in rows]
    label = names[0] if len(names) == 1 else _("dataset.msg.n_datasets").format(n=len(names))

    if not messagebox.askyesno(
      _("common.confirm_delete"),
      _("dataset.msg.delete_confirm").format(label=label),
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
        _("common.delete_error"),
        _("dataset.msg.delete_partial") + "\n".join(errors),
      )

  def _on_dataset_saved(self, dataset_payload: dict) -> None:
    try:
      if dataset_payload.get("id"):
        DatasetManager.update_dataset(dataset_payload)
      else:
        DatasetManager.add_dataset(
          name=dataset_payload["name"],
          problem_type=dataset_payload["type"],
          layout=dataset_payload["layout"],
          has_header=dataset_payload["has_header"],
          target=dataset_payload.get("target"),
          files=dataset_payload.get("files"),
        )
    except Exception as e:
      messagebox.showerror(_("common.error"), str(e))
      return

    self.load_table_data()
