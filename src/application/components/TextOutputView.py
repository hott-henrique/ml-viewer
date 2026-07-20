import tkinter as tk
from tkinter import ttk

class TextOutputView(tk.Frame):

  def __init__(self, master=None):
    super().__init__(master)

    results_frame = ttk.LabelFrame(self, text="Output / Results")
    results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    self.output_text = tk.Text(results_frame, height=15, width=60, state=tk.DISABLED)
    self.output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

  def show(self, message):
    self.output_text.config(state=tk.NORMAL)
    self.output_text.delete(1.0, tk.END)
    self.output_text.insert(tk.END, message)
    self.output_text.config(state=tk.DISABLED)