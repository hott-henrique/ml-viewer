import tkinter as tk
import pandas as pd
import threading
import time
import json

from tkinter import ttk, messagebox

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

from application.components import TextOutputView

from application.state import store

from loader import AlgorithmRegistry

class ExecutionTab(ttk.Frame):

  def __init__(self, master=None):
    super().__init__(master)

    self.text_output_view = TextOutputView(self)
    self.text_output_view.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    self.progress_bar = ttk.Progressbar(self, mode='determinate', value=0)
    self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

    self.run_btn = ttk.Button(self, text="Run Simple Pipeline", command=self.run_pipeline)
    self.run_btn.pack(fill=tk.X, padx=10, pady=5)

  def run_pipeline(self):
    if store.filepath == "":
      messagebox.showwarning("Warning", "Please select a CSV file first.")
      return

    if not store.target_col:
      messagebox.showwarning("Warning", "Please select a valid target variable.")
      return

    self.text_output_view.show("Loading data and running pipeline...\n")

    self.run_btn.config(state=tk.DISABLED)

    self.progress_bar.config(mode='indeterminate')
    self.progress_bar.start(15)

    thread = threading.Thread(
      target=self._process_ml_pipeline, 
      args=(store.filepath, store.target_col, store.train_size),
      daemon=True
    )

    thread.start()

  def _process_ml_pipeline(self, filepath: str, target_col: str, train_size: float):
    try:
      time.sleep(3) 

      df = pd.read_csv(filepath)
      df = df.dropna()

      if target_col not in df.columns:
        raise ValueError("Target column not found in dataset.")

      X = df.drop(columns=[target_col])
      y = df[target_col]

      X = pd.get_dummies(X) 
      
      if y.dtype == 'object':
        le = LabelEncoder()
        y = le.fit_transform(y)

      X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=train_size, random_state=42
      )

      model = AlgorithmRegistry.instantiate(store.selected_algorithm, store.hyperparameters)
      model.fit(X_train, y_train)

      preds = model.predict(X_test)
      acc = accuracy_score(y_test, preds)
      report = classification_report(y_test, preds)

      params_dict = model.get_params()
      formatted_params = json.dumps(params_dict, indent=2)

      result_msg = (
        f"Pipeline finished successfully!\n\n"
        f"Model Parameters:\n{formatted_params}\n"
        f"{'-'*40}\n"
        f"Dataset shape after dropna: {df.shape}\n"
        f"Train Size: {len(X_train)} samples\n"
        f"Test Size: {len(X_test)} samples\n"
        f"{'-'*40}\n"
        f"Accuracy: {acc:.4f}\n\n"
        f"Classification Report:\n{report}"
      )

      self.after(0, self._on_pipeline_success, result_msg)
    except Exception as e:
      self.after(0, self._on_pipeline_error, str(e))

  def _on_pipeline_success(self, result_msg):
    self.progress_bar.stop()

    self.progress_bar.config(mode='determinate', value=0)
    self.run_btn.config(state=tk.NORMAL)
    self.text_output_view.show(result_msg)

  def _on_pipeline_error(self, error_msg):
    self.progress_bar.stop()

    self.progress_bar.config(mode='determinate', value=0)
    self.run_btn.config(state=tk.NORMAL)
    self.text_output_view.show(f"An error occurred during execution:\n{error_msg}")