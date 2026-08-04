import typing as t
import tkinter as tk
from tkinter import ttk


def _sort_key(value: object) -> tuple[int, t.Any]:
  """Normalize cell values for mixed-type sorting (numbers before strings)."""
  if value is None:
    return (2, "")

  text = str(value).strip()

  try:
    return (0, int(text))
  except ValueError:
    pass

  try:
    return (0, float(text))
  except ValueError:
    pass

  return (1, text.casefold())


class SortableTreeview(ttk.Treeview):
  """Treeview with multi-select and clickable column headings for sorting."""

  def __init__(
    self,
    master: tk.Misc | None = None,
    *,
    columns: tuple[str, ...] | list[str],
    display_columns: t.Optional[tuple[str, ...] | list[str]] = None,
    sort_keys: t.Optional[dict[str, str]] = None,
    **kwargs: t.Any,
  ) -> None:
    kwargs.setdefault("selectmode", "extended")
    kwargs.setdefault("show", "headings")
    super().__init__(master, columns=columns, **kwargs)

    self._base_headings: dict[str, str] = {}
    self._sort_column: t.Optional[str] = None
    self._sort_reverse = False
    # Maps a visible column to a hidden column that holds the true sort value (e.g. disk -> disk_bytes).
    self._sort_keys = dict(sort_keys or {})

    if display_columns is not None:
      self["displaycolumns"] = display_columns

  def set_heading(self, column: str, text: str, *, sortable: bool = True) -> None:
    self._base_headings[column] = text

    if sortable:
      self.heading(column, text=text, command=lambda c=column: self.sort_by(c))
    else:
      self.heading(column, text=text)

  def sort_by(self, column: str) -> None:
    if self._sort_column == column:
      self._sort_reverse = not self._sort_reverse
    else:
      self._sort_column = column
      self._sort_reverse = False

    key_column = self._sort_keys.get(column, column)
    col_index = list(self["columns"]).index(key_column)

    rows: list[tuple[tuple[int, t.Any], str]] = []

    for iid in self.get_children(""):
      values = self.item(iid, "values")
      raw = values[col_index] if col_index < len(values) else ""
      rows.append((_sort_key(raw), iid))

    rows.sort(key=lambda item: item[0], reverse=self._sort_reverse)

    for index, (_, iid) in enumerate(rows):
      self.move(iid, "", index)

    self._refresh_heading_labels()

  def _refresh_heading_labels(self) -> None:
    for column, base in self._base_headings.items():
      if column == self._sort_column:
        suffix = " ▼" if self._sort_reverse else " ▲"
        self.heading(column, text=f"{base}{suffix}")
      else:
        self.heading(column, text=base)

  def bind_context_menu(self, build_menu: t.Callable[[tk.Event], t.Optional[tk.Menu]]) -> None:
    def _show(event: tk.Event) -> None:
      row = self.identify_row(event.y)

      if row:
        if row not in self.selection():
          self.selection_set(row)
          self.focus(row)

      menu = build_menu(event)

      if menu is None:
        return

      try:
        menu.tk_popup(event.x_root, event.y_root)
      finally:
        menu.grab_release()

    self.bind("<Button-3>", _show)
    self.bind("<Button-2>", _show)
