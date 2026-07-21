import tkinter as tk

from tkinter import ttk

from application.components import DatasetTab, AlgorithmTab, ExecutionTab

class Application(tk.Tk):
  def __init__(self):
    super().__init__()

    self.title('Machine Learning Classification App')
    self.geometry('600x850')

    self.notebook = ttk.Notebook(self)
    self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    self.tab_dataset = DatasetTab(self)
    self.tab_model = AlgorithmTab(self)
    self.tab_exec = ExecutionTab(self)

    self.notebook.add(self.tab_dataset, text='Dataset')
    self.notebook.add(self.tab_model, text='Model')
    self.notebook.add(self.tab_exec, text='Execution')

if __name__ == '__main__':
  app = Application()
  app.mainloop()