import typing as t
import tkinter as tk
from tkinter import ttk

from application.components import FileSelector, DatasetHandler
from application.state import store

class DatasetTab(ttk.Frame):
  def __init__(self, master=None):
    super().__init__(master)

    self.file_selector = FileSelector(self, on_file_selected=self.on_file_selected)
    self.file_selector.pack(fill=tk.X, padx=10, pady=5)

    self.dataset_handler = DatasetHandler(
      self,
      on_target_change=self.on_target_change,
      on_split_change=self.on_split_change
    )

    self.dataset_handler.pack(fill=tk.X, padx=10, pady=5)

  def on_file_selected(self, filepath):
    store.filepath = filepath
    self.dataset_handler.load_columns(filepath)

  def on_target_change(self, target_value):
    store.target_col = target_value

  def on_split_change(self, split_value):
    try:
      store.train_size = float(split_value)
    except ValueError:
      pass