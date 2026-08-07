from enum import StrEnum

class LearningParadigm(StrEnum):
  SUPERVISED = "Supervised"
  UNSUPERVISED = "Unsupervised"

class ProblemType(StrEnum):
  CLASSIFICATION = "Classification"
  REGRESSION = "Regression"
  CLUSTERING = "Clustering"
  DIMENSIONALITY_REDUCTION = "Dimensionality Reduction"
  ASSOCIATION_RULES = "Association Rules"

class ParamType(StrEnum):
  INT = "int"
  FLOAT = "float"
  BOOL = "bool"
  CATEGORICAL = "categorical"
  STRING = "string"

class ExperimentStatus(StrEnum):
  PENDING = "Pending"
  OK = "OK"
  NOK = "NOK"

class AnalysisOutputKind(StrEnum):
  SCALAR = "scalar"
  TEXT = "text"
  IMAGE = "image"

class DatasetLayout(StrEnum):
  NO_SPLIT = "NoSplit"
  TRAIN_TEST_SPLIT = "TrainTestSplit"

class DatasetFileRole(StrEnum):
  FULL = "Full"
  TRAIN = "Train"
  TEST = "Test"
