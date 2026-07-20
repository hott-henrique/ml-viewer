import tkinter as tk

import pandas as pd

from tkinter import ttk, messagebox

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

from application.components import FileSelector, DatasetHandler, TextOutputView, AlgorithmSelector

class Application(tk.Tk):
  def __init__(self):
    super().__init__()

    self.title('Machine Learning Classification App')
    self.geometry('550x650')

    self.file_selector = FileSelector(self, on_file_selected=self.on_file_selected)
    self.file_selector.pack(fill=tk.X)

    self.dataset_handler = DatasetHandler(self)
    self.dataset_handler.pack(fill=tk.X)

    self.algorithm_selector = AlgorithmSelector(self)
    self.algorithm_selector.pack(fill=tk.X)

    self.run_btn = ttk.Button(self, text="Run Simple Pipeline", command=self.run_pipeline)
    self.run_btn.pack(pady=15)

    self.text_output_view = TextOutputView(self)
    self.text_output_view.pack(fill=tk.X)

  def on_file_selected(self, filepath):
    self.dataset_handler.load_columns(filepath)
    self.text_output_view.show(f"File selected: {filepath}\nColumns loaded successfully.")

  def run_pipeline(self):
    filepath = self.file_selector.file_path_var.get()
    target_col = self.dataset_handler.target_var.get()
    
    if filepath == "No file selected":
      messagebox.showwarning("Warning", "Please select a CSV file first.")
      return
    
    if not target_col or target_col == "Error loading":
      messagebox.showwarning("Warning", "Please select a valid target variable.")
      return

    try:
      train_size = float(self.dataset_handler.split_var.get())
    except ValueError:
      messagebox.showwarning("Warning", "Invalid train size.")
      return

    self.text_output_view.show("Loading data and running pipeline...\n")

    try:
      df = pd.read_csv(filepath)

      # INFO: ML Pipeline Simplification. TODO: ?
      df = df.dropna()

      if target_col not in df.columns:
        self.text_output_view.show("Error: Target column not found in dataset.")
        return

      X = df.drop(columns=[target_col])
      y = df[target_col]

      # INFO: ML Pipeline Simplification. TODO: ?
      # Transformação básica (One-Hot Encoding para features string, Label encoding para target)
      X = pd.get_dummies(X) 
      
      if y.dtype == 'object':
        le = LabelEncoder()
        y = le.fit_transform(y)

      # INFO: Train/Test Split
      X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=train_size, random_state=42
      )

      model = self.algorithm_selector.get_instance()

      model.fit(X_train, y_train)

      preds = model.predict(X_test)
      acc = accuracy_score(y_test, preds)
      report = classification_report(y_test, preds)

      result_msg = (
        f"Pipeline finished successfully!\n\n"
        f"Dataset shape after dropna: {df.shape}\n"
        f"Train Size: {len(X_train)} samples\n"
        f"Test Size: {len(X_test)} samples\n"
        f"{'-'*40}\n"
        f"Accuracy: {acc:.4f}\n\n"
        f"Classification Report:\n{report}"
      )

      self.text_output_view.show(result_msg)
    except Exception as e:
      self.text_output_view.show(f"An error occurred during execution:\n{str(e)}")

if __name__ == '__main__':
  app = Application()
  app.mainloop()