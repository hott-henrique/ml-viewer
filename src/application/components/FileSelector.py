import tkinter as tk
from tkinter import ttk, filedialog
import typing as t

class FileSelector(ttk.LabelFrame):
  file_path_var: tk.StringVar
  on_file_selected: t.Optional[t.Callable[[str], None]]

  def __init__(self, master=None, on_file_selected: t.Optional[t.Callable[[str], None]] = None):
    super().__init__(master, text="File", padding=(10, 10))
    self.on_file_selected = on_file_selected

    self.file_path_var = tk.StringVar(value="No file selected")

    self.columnconfigure(0, weight=4)
    self.columnconfigure(1, weight=1)

    self.file_label = ttk.Label(
      self,
      textvariable=self.file_path_var,
      foreground="gray",
      anchor=tk.W
    )

    self.file_label.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=10)

    self.main_btn = ttk.Button(self, text='Select CSV', command=self.select_csv)
    self.main_btn.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=10)

  def select_csv(self):
    filename = filedialog.askopenfilename(
      title='Select a File',
      initialdir='.',
      filetypes=(('Comma separated values files', '*.csv'), )
    )

    if filename:
      self.file_path_var.set(filename)

      if self.on_file_selected:
        self.on_file_selected(filename)
