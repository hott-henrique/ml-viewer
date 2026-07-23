from sklearn.base import BaseEstimator, ClassifierMixin
import numpy as np

class DummyMajorityClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, fallback_class=0):
        self.fallback_class = fallback_class
        self.majority_class_ = None

    def fit(self, X, y):
        values, counts = np.unique(y, return_counts=True)
        self.majority_class_ = values[np.argmax(counts)]
        return self

    def predict(self, X):
        prediction = self.majority_class_ if self.majority_class_ is not None else self.fallback_class
        return np.full(shape=(X.shape[0],), fill_value=prediction)

MODEL_CONFIG = {
    "Majority Vote Dummy": {
        "type": "Classification", 
        "class": "DummyMajorityClassifier",
        "description": "A custom classifier that always predicts the most frequent class in the training set. Good for baseline testing.",
        "params": [
            {
                "name": "fallback_class",
                "type": "int",
                "default": 0,
                "label": "Fallback Class",
                "description": "The class to predict if fit hasn't been called."
            }
        ]
    }
}